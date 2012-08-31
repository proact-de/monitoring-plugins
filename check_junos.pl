#!/usr/bin/perl

#############################################################################
# (c) 2001, 2003 Juniper Networks, Inc.                                     #
# (c) 2011-2012 Sebastian "tokkee" Harl <sh@teamix.net>                     #
#               and team(ix) GmbH, Nuernberg, Germany                       #
#                                                                           #
# This file is part of "team(ix) Monitoring Plugins"                        #
# URL: http://oss.teamix.org/projects/monitoringplugins/                    #
#                                                                           #
# All rights reserved.                                                      #
# Redistribution and use in source and binary forms, with or without        #
# modification, are permitted provided that the following conditions        #
# are met:                                                                  #
# 1. Redistributions of source code must retain the above copyright         #
#    notice, this list of conditions and the following disclaimer.          #
# 2. Redistributions in binary form must reproduce the above copyright      #
#    notice, this list of conditions and the following disclaimer in the    #
#    documentation and/or other materials provided with the distribution.   #
# 3. The name of the copyright owner may not be used to endorse or          #
#    promote products derived from this software without specific prior     #
#    written permission.                                                    #
#                                                                           #
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR      #
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED            #
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE    #
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,        #
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES        #
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR        #
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)        #
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,       #
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING     #
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE        #
# POSSIBILITY OF SUCH DAMAGE.                                               #
#############################################################################

use strict;
use warnings;

use utf8;

use JUNOS::Device;

use FindBin qw( $Bin );
use lib "$Bin/perl/lib";
use Nagios::Plugin::JUNOS;

binmode STDOUT, ":utf8";

# TODO:
# * chassis_routing_engine: show chassis routing-engine (-> number and status)

my $plugin = Nagios::Plugin::JUNOS->new(
	plugin    => 'check_junos',
	shortname => 'check_junos',
	version   => '0.1',
	url       => 'http://oss.teamix.org/projects/monitoringplugins',
	blurb     => 'Monitor Juniper™ Switches.',
	usage     =>
"Usage: %s [-v|--verbose] [-H <host>] [-p <port>] [-t <timeout]
[-C] [-U <user>] [-P <password] check-tuple [...]",
	license   =>
"This nagios plugin is free software, and comes with ABSOLUTELY NO WARRANTY.
It may be used, redistributed and/or modified under the terms of the 3-Clause
BSD License (see http://opensource.org/licenses/BSD-3-Clause).",
	extra     => "
This plugin connects to a Juniper™ Switch device and checks various of its
components.

A check-tuple consists of the name of the check and, optionally, a \"target\"
which more closely specifies which characteristics should be checked, and
warning and critical thresholds:
checkname[,target[,warning[,critical]]]

The following checks are available:
  * interfaces: Status of interfaces. If a target is specified, only the
    specified interface(s) will be taken into account. The special target
    '\@with_description' selects all interfaces with a non-empty description.

    If an aggregated interface is encountered, the physical interfaces will
    be checked as well.

  * interface_forwarding: Check the forwarding state of interfaces as provided
    by 'show ethernet-switching interfaces'. Storm control, MAC limit and
    BPDUs will be considered CRITICAL states. If a target is specified, only
    the specified interface(s) will be taken into account. Targets may be
    specified as <interface_name>:<forwarding_state> in which case a CRITICAL
    state is assumed if the specified interface is not in the specified state.

  * chassis_environment: Check the status of verious system components
    (as provided by 'show chassis environment'). If a target is specified,
    only the specified component(s) will be taken into account. If specified,
    the thresholds will be checked against the temperature of the components.

  * system_storage: Check the amount of used space of system filesystems. If a
    target is specified, only the specified filesystem(s) will be taken into
    account (specified either by filesystem name or mount point). The
    threshold will be checked against the amount (percent) of used space.

Warning and critical thresholds may be specified in the format documented at
http://nagiosplug.sourceforge.net/developer-guidelines.html#THRESHOLDFORMAT.",
);

my %checks = (
	interfaces           => \&check_interfaces,
	interface_forwarding => \&check_interface_forwarding,
	chassis_environment  => \&check_chassis_environment,
	system_storage       => \&check_system_storage,
);

my $junos = undef;

my $cache = {};

$plugin->add_common_args();
$plugin->add_arg({
		spec    => 'caching|C',
		usage   => '-C, --caching',
		desc    => 'Enabling caching of API results',
		default => 0,
	});

foreach my $check (keys %checks) {
	$plugin->add_check_impl($check, $checks{$check});
}

$plugin->set_default_check('chassis_environment');

# configure removes any options from @ARGV
$plugin->configure();
$plugin->set_checks(@ARGV);
$junos = $plugin->connect();

$plugin->run_checks();

my ($code, $msg) = $plugin->check_messages(join => ', ');

$plugin->nagios_exit($code, $msg);

sub check_interface
{
	my $plugin  = shift;
	my $iface   = shift;
	my $opts    = shift || {};
	my @targets = @_;

	my $name = $plugin->get_query_object_value($iface, 'name');
	my $admin_status = $plugin->get_query_object_value($iface, 'admin-status');

	if ($admin_status !~ m/^up$/) {
		if ((grep { $name =~ m/^$_$/; } @targets)
				|| ($opts->{'with_description'} &&
					$plugin->get_query_object_value($iface, 'description'))) {
			$plugin->add_message(CRITICAL,
				"$name is not enabled");
			return -1;
		}
		return 1;
	}

	if ($plugin->get_query_object_value($iface, 'oper-status') !~ m/^up$/i) {
		return 0;
	}

	$plugin->add_perfdata(
		label     => "'$name-input-bytes'",
		value     => $plugin->get_query_object_value($iface,
				['traffic-statistics', 'input-bytes']),
		min       => 0,
		max       => undef,
		uom       => 'B',
		threshold => undef,
	);
	$plugin->add_perfdata(
		label     => "'$name-output-bytes'",
		value     => $plugin->get_query_object_value($iface,
				['traffic-statistics', 'output-bytes']),
		min       => 0,
		max       => undef,
		uom       => 'B',
		threshold => undef,
	);
	return 1;
}

sub get_interfaces
{
	my $plugin  = shift;
	my $opts    = shift || {};
	my @targets = @_;

	my @ifaces  = ();
	my @ret     = ();

	if (defined($cache->{'interfaces'})) {
		@ifaces = @{$cache->{'interfaces'}};
	}
	else {
		my $cmd = 'get_interface_information';
		my $res;

		my $args = { detail => 1 };

		if ((scalar(@targets) == 1) && (! $opts->{'with_description'})
				&& (! $plugin->{'conf'}->{'caching'})) {
			$args->{'interface_name'} = $targets[0];
		}
		$res = $plugin->send_query($cmd, $args);

		if (! ref $res) {
			$plugin->die($res);
		}

		@ifaces = $res->getElementsByTagName('physical-interface');
	}

	if ($plugin->{'conf'}->{'caching'}) {
		$cache->{'interfaces'} = \@ifaces;
	}

	@targets = map { s/\*/\.\*/g; s/\?/\./g; $_; } @targets;

	if (scalar(@targets)) {
		@ret = grep {
			my $i = $_;
			grep { $plugin->get_query_object_value($i, 'name') =~ m/^$_$/ } @targets;
		} @ifaces;
	}
	elsif (! $opts->{'with_description'}) {
		@ret = @ifaces;
	}

	if ($opts->{'with_description'}) {
		foreach my $iface (@ifaces) {
			my $name = $plugin->get_query_object_value($iface, 'name');
			if ($plugin->get_query_object_value($iface, 'description')
					&& (! grep { m/^$name$/; } @targets)) {
				push @ret, $iface;
			}
		}
	}

	{
		my @i = map { $plugin->get_query_object_value($_, 'name'). " => "
			. $plugin->get_query_object_value($_, 'oper-status') } @ret;
		$plugin->verbose(3, "Interfaces: " . join(", ", @i));
	}
	return @ret;
}

sub check_interfaces
{
	my $plugin  = shift;
	my $junos   = shift;
	my $targets = shift || [];
	my $exclude = shift || [];

	my $opts = {
		with_description => 0,
	};

	if (grep { m/^\@with_description$/; } @$targets) {
		$opts->{'with_description'} = 1;

		@$targets = grep { ! m/^\@with_description$/; } @$targets;
	}

	my @interfaces = get_interfaces($plugin, $opts, @$targets);;

	my $down_count = 0;
	my @down_ifaces = ();

	my $phys_down_count = 0;
	my @phys_down_ifaces = ();

	my $have_lag_ifaces = 0;

	foreach my $iface (@interfaces) {
		my $name = $plugin->get_query_object_value($iface, 'name');
		my $desc = $plugin->get_query_object_value($iface, 'description');
		my $status = check_interface($plugin, $iface, $opts, @$targets);

		my $tmp;

		if ($status == 0) {
			++$down_count;
			$tmp = $name . ($desc ? " ($desc)" : "");
			push @down_ifaces, $tmp;
		}

		if ($status <= 0) {
			# disabled or down
			next;
		}

		if ($name !~ m/^ae/) {
			next;
		}

		$have_lag_ifaces = 1;

		my @markers = $plugin->get_query_object($iface,
			['logical-interface', 'lag-traffic-statistics', 'lag-marker']);

		if (! @markers) {
			print STDERR "Cannot get marker for non-LACP interfaces yet!\n";
			next;
		}

		foreach my $marker (@markers) {
			my $phy_name = $plugin->get_query_object_value($marker, 'name');
			$phy_name =~ s/\.\d+$//;

			$plugin->verbose(3, "Quering physical interface '$phy_name' "
				. "for $name.");

			my @phy_interfaces = get_interfaces($plugin, {}, $phy_name);
			foreach my $phy_iface (@phy_interfaces) {
				if (check_interface($plugin, $phy_iface, {}, $phy_name) == 0) {
					++$phys_down_count;
					$tmp = $name . ($desc ? " ($desc)" : "");
					push @phys_down_ifaces, "$tmp -> $phy_name";
				}
			}
		}
	}

	if ($down_count > 0) {
		$plugin->add_message(CRITICAL, $down_count . " interface"
			. ($down_count == 1 ? "" : "s")
			. " down (" . join(", ", @down_ifaces) . ")");
	}

	if ($phys_down_count > 0) {
		$plugin->add_message(WARNING, $phys_down_count
			. " LAG member interface"
			. ($phys_down_count == 1 ? "" : "s")
			. " down ("
			. join(", ", @phys_down_ifaces) . ")");
	}

	if ((! $down_count) && (! $phys_down_count)) {
		if ((! scalar(@$targets)) || $opts->{'with_description'}) {
			$plugin->add_message(OK, "all interfaces up"
				. ($have_lag_ifaces
					? " (including all LAG member interfaces)" : ""));
		}
		else {
			$plugin->add_message(OK, "interface"
				. (scalar(@$targets) == 1 ? " " : "s ")
				. join(", ", @$targets) . " up"
				. ($have_lag_ifaces
					? " (including all LAG member interfaces)" : ""));
		}
	}
}

sub check_interface_forwarding
{
	my $plugin  = shift;
	my $junos   = shift;
	my $targets = shift || [];
	my $exclude = shift || [];

	my $res = $plugin->send_query('show ethernet-switching interfaces brief');

	my %critical_map = (
		'Disabled by bpdu-control' => 1,
		'MAC limit exceeded'       => 1,
		'MAC move limit exceeded'  => 1,
		'Storm control in effect'  => 1,
	);

	my %targets = map { my @t = split(':', $_); $t[0] => $t[1]; } @$targets;

	my @failed = ();

	foreach my $iface ($plugin->get_query_object($res, 'interface')) {
		my $name = $plugin->get_query_object_value($iface, 'interface-name');
		my $failed_status = undef;

		if (scalar(@$targets) && (! exists($targets{$name}))) {
			next;
		}

		foreach my $vlan_member ($plugin->get_query_object($iface,
				['interface-vlan-member-list', 'interface-vlan-member'])) {
			my $status = $plugin->get_query_object_value($vlan_member,
				'blocking-status');

			if (defined($targets{$name})) {
				if ($status ne $targets{$name}) {
					$failed_status = "$status (should: $targets{$name})";
					last;
				}
			}
			elsif (defined $critical_map{$status}) {
				$failed_status = $status;
				last;
			}
		}

		if ($failed_status) {
			push @failed, { name => $name, status => $failed_status };
		}
	}

	if (scalar(@failed)) {
		$plugin->add_message(CRITICAL, scalar(@failed) . " interface"
			. (scalar(@failed) == 1 ? "" : "s")
			. " blocked: "
			. join(", ", map { "$_->{'name'}: $_->{'status'}" } @failed));
	}
	else {
		$plugin->add_message(OK, "forwarding state of all interfaces OK");
	}
}

sub check_chassis_environment
{
	my $plugin  = shift;
	my $junos   = shift;
	my $targets = shift || [];
	my $exclude = shift || [];

	my $res = $plugin->send_query('get_environment_information');

	my %status_map = (
		OK      => OK,
		Testing => UNKNOWN,
		Check   => UNKNOWN,
		Failed  => CRITICAL,
		Absent  => CRITICAL,
	);

	my $items_count = 0;
	my $items_ok    = 0;

	my $class = "";
	foreach my $item ($plugin->get_query_object($res, 'environment-item')) {
		my $name = $plugin->get_query_object_value($item, 'name');

		if (scalar(@$targets) && (! grep { m/^$name$/ } @$targets)) {
			next;
		}

		if ($plugin->get_query_object_value($item, 'class')) {
			$class = $plugin->get_query_object_value($item, 'class');
		}

		my $status = $plugin->get_query_object_value($item, 'status');

		if ($status eq "Absent") {
			if (! scalar(@$targets)) {
				next;
			}
			# else: check this component
		}

		my $state  = UNKNOWN;
		if (defined $status_map{$status}) {
			$state = $status_map{$status};
		}

		++$items_count;

		if ($state == OK) {
			++$items_ok;
		}
		else {
			$plugin->add_message($state, $class . " $name: status " .
				$status);
		}

		my $temp = $plugin->get_query_object_value($item, 'temperature');
		if (! $temp) {
			next;
		}

		($temp) = $temp =~ m/(\d+) degrees C/;
		if (! defined($temp)) {
			next;
		}

		$state = $plugin->check_threshold($temp);
		if ($state != OK) {
			$plugin->add_message($state, $class
				. " $name: ${temp} degrees C");
		}

		my $label = "$name-temp";
		$label =~ s/ /_/g;
		$plugin->add_perfdata(
			label     => "'$label'",
			value     => $temp,
			min       => undef,
			max       => undef,
			uom       => '',
			threshold => $plugin->threshold(),
		);
	}

	if (! $items_count) {
		$plugin->add_message(WARNING, "no components found");
	}
	elsif ($items_count == $items_ok) {
		$plugin->add_message(OK, "$items_ok component"
			. ($items_ok == 1 ? "" : "s")
			. " OK");
	}
	else {
		$plugin->add_message(WARNING,
			"$items_ok / $items_count components OK");
	}
}

sub check_system_storage
{
	my $plugin  = shift;
	my $junos   = shift;
	my $targets = shift || [];
	my $exclude = shift || [];

	my $res = $plugin->send_query('get_system_storage');

	my $all_ok = 1;

	foreach my $re ($plugin->get_query_object($res,
			'multi-routing-engine-item')) {
		my $re_name = $plugin->get_query_object_value($re, 're-name');

		foreach my $fs ($plugin->get_query_object($re,
				['system-storage-information', 'filesystem'])) {
			my $name = $plugin->get_query_object_value($fs, 'filesystem-name');
			my $mnt_pt = $plugin->get_query_object_value($fs, 'mounted-on');

			if (scalar(@$targets) && (! grep { m/^$name$/ } @$targets)
					&& (! grep { m/^$mnt_pt$/ } @$targets)) {
				next;
			}

			my $used = $plugin->get_query_object_value($fs, 'used-percent') + 0;

			my $state = $plugin->check_threshold($used);
			if ($state != OK) {
				$all_ok = 0;
				$plugin->add_message($state, "$re_name $mnt_pt: "
					. "$used\% used");
			}
			$plugin->add_perfdata(
				label     => "'$re_name-$mnt_pt'",
				value     => $used,
				min       => 0,
				max       => 100,
				uom       => '%',
				threshold => $plugin->threshold(),
			);
		}
	}

	if ($all_ok) {
		$plugin->add_message(OK, "all filesystems within thresholds");
	}
}

