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

my $valid_checks = "interfaces|chassis_environment|system_storage";

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
[-U <user>] [-P <password] check-tuple [...]",
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
    specified interface is taken into account.

    If an aggregated interface is encountered, the physical interfaces will
    be checked as well.

  * chassis_environment: Check the status of verious system components
    (as provided by 'show chassis environment'). If specified, the thresholds
    will be checked against the temperature of the components.

  * system_storage: Check the amount of used space of system filesystems. The
    threshold will be checked against the amount (percent) of used space.

Warning and critical thresholds may be specified in the format documented at
http://nagiosplug.sourceforge.net/developer-guidelines.html#THRESHOLDFORMAT.",
);

my @args = (
	{
		spec    => 'host|H=s',
		usage   => '-H, --host=HOSTNAME',
		desc    => 'Hostname/IP of Juniper box to connect to',
		default => 'localhost',
	},
	{
		spec    => 'port|p=i',
		usage   => '-p, --port=PORT',
		desc    => 'Port to connect to',
		default => 22,
	},
	{
		spec    => 'user|U=s',
		usage   => '-U, --user=USERNAME',
		desc    => 'Username to log into box as',
		default => 'root',
	},
	{
		spec    => 'password|P=s',
		usage   => '-P, --password=PASSWORD',
		desc    => 'Password for login username',
		default => '<prompt>',
	},
);

my $junos = undef;

foreach my $arg (@args) {
	$plugin->add_arg($arg);
}

$plugin->configure();
$plugin->set_checks($valid_checks, 'chassis_environment', @ARGV);
$junos = $plugin->connect();

foreach my $check ($plugin->get_checks()) {
	my @targets = ();

	if (defined $check->{'target'}) {
		@targets = @{$check->{'target'}};
	}

	$plugin->set_thresholds(
		warning  => $check->{'warning'},
		critical => $check->{'critical'},
	);

	if ($check->{'name'} eq 'interfaces') {
		check_interfaces(@targets);
	}
	elsif ($check->{'name'} eq 'chassis_environment') {
		check_chassis_environment(@targets);
	}
	elsif ($check->{'name'} eq 'system_storage') {
		check_system_storage(@targets);
	}
}

my ($code, $msg) = $plugin->check_messages(join => ', ');

$junos->disconnect();

$plugin->nagios_exit($code, $msg);

sub send_query
{
	my $device    = shift;
	my $query     = shift;
	my $queryargs = shift;

	my $res;
	my $err;

	$plugin->verbose(3, "Sending query '$query' "
		. join(", ", map { "$_ => $queryargs->{$_}" } keys %$queryargs)
		. " to router.");

	if (ref $queryargs) {
		$res = $device->$query(%$queryargs);
	} else {
		$res = $device->$query();
	}

	if (! ref $res) {
		return "ERROR: Failed to execute query '$query'";
	}

	$err = $res->getFirstError();
	if ($err) {
		return "ERROR: " . $err->{message};
	}
	return $res;
}

sub check_interface {
	my $iface = shift;
	my $opts  = shift || {};
	my @targets = @_;

	my $name = get_iface_name($iface);
	my $admin_status = get_iface_admin_status($iface);

	if ($admin_status !~ m/^up$/) {
		if ((grep { $name =~ m/^$_$/; } @targets)
				|| ($opts->{'with_description'} &&
					get_iface_description($iface))) {
			$plugin->add_message(CRITICAL,
				"$name is not enabled");
			return -1;
		}
		return 1;
	}

	if (get_iface_status($iface) !~ m/^up$/i) {
		return 0;
	}

	$plugin->add_perfdata(
		label     => "'$name-input-bytes'",
		value     => get_iface_traffic($iface, "input"),
		min       => 0,
		max       => undef,
		uom       => 'B',
		threshold => undef,
	);
	$plugin->add_perfdata(
		label     => "'$name-output-bytes'",
		value     => get_iface_traffic($iface, "output"),
		min       => 0,
		max       => undef,
		uom       => 'B',
		threshold => undef,
	);
	return 1;
}

sub get_interfaces
{
	my $device  = shift;
	my $opts    = shift || {};
	my @targets = @_;
	my @ifaces  = ();
	my @ret     = ();

	my $cmd = 'get_interface_information';
	my $res;

	my $args = { detail => 1 };

	if ((scalar(@targets) == 1) && (! $opts->{'with_description'})) {
		$args->{'interface_name'} = $targets[0];
	}
	$res = send_query($device, $cmd, $args);

	if (! ref $res) {
		$plugin->die($res);
	}

	@ifaces = $res->getElementsByTagName('physical-interface');

	@targets = map { s/\*/\.\*/g; s/\?/\./g; $_; } @targets;

	if (scalar(@targets)) {
		@ret = grep {
			my $i = $_;
			grep { get_iface_name($i) =~ m/^$_$/ } @targets;
		} @ifaces;
	}
	elsif (! $opts->{'with_description'}) {
		@ret = @ifaces;
	}

	if ($opts->{'with_description'}) {
		foreach my $iface (@ifaces) {
			my $name = get_iface_name($iface);
			if (get_iface_description($iface)
					&& (! grep { m/^$name$/; } @targets)) {
				push @ret, $iface;
			}
		}
	}

	{
		my @i = map { get_iface_name($_) . " => " . get_iface_status($_) }
			@ret;
		$plugin->verbose(3, "Interfaces: " . join(", ", @i));
	}
	return @ret;
}

sub get_obj_element
{
	my $obj  = shift;
	my $elem = shift;

	$elem = $obj->getElementsByTagName($elem);
	if ((! $elem) || (! $elem->item(0))) {
		return;
	}
	return $elem->item(0)->getFirstChild->getNodeValue;
}

sub get_object_value
{
	my $res = shift;

	if (! $res) {
		return;
	}

	if (ref($res) eq "XML::DOM::NodeList") {
		$res = $res->item(0);
	}

	return $res->getFirstChild->getNodeValue;
}

sub get_object_by_spec
{
	my $res  = shift;
	my $spec = shift;

	if (! $res) {
		return;
	}

	if (! $spec) {
		return $res;
	}

	if (! ref($spec)) {
		$spec = [ $spec ];
	}

	my $iter = $res;
	for (my $i = 0; $i < scalar(@$spec) - 1; ++$i) {
		my $tmp = $iter->getElementsByTagName($spec->[$i]);

		if ((! $tmp) || (! $tmp->item(0))) {
			return;
		}

		$iter = $tmp->item(0);
	}

	if (wantarray) {
		my @ret = $iter->getElementsByTagName($spec->[scalar(@$spec) - 1]);
		return @ret;
	}
	else {
		my $ret = $iter->getElementsByTagName($spec->[scalar(@$spec) - 1]);
		if ((! $ret) || (! $ret->item(0))) {
			return;
		}
		return $ret->item(0);
	}
}

sub get_object_value_by_spec
{
	my $res = get_object_by_spec(@_);
	return get_object_value($res);
}

sub get_iface_name
{
	my $iface = shift;
	return get_obj_element($iface, 'name');
}

sub get_iface_description
{
	my $iface = shift;
	return get_obj_element($iface, 'description');
}

sub get_iface_status
{
	my $iface = shift;
	return get_obj_element($iface, 'oper-status');
}

sub get_iface_admin_status
{
	my $iface = shift;
	return get_obj_element($iface, 'admin-status');
}

sub get_iface_traffic
{
	my $iface = shift;
	my $type  = shift;

	my $stats = get_obj_element($iface, 'traffic-statistics');
	return get_obj_element($iface, "$type-bytes");
}

sub get_iface_first_logical
{
	my $iface = shift;
	return $iface->getElementsByTagName('logical-interface')->item(0);
}

sub get_liface_marker
{
	my $liface = shift;

	my $lag_stats = $liface->getElementsByTagName('lag-traffic-statistics')->item(0);
	if (! $lag_stats) {
		print STDERR "Cannot get marker for non-LACP interfaces yet!\n";
		return;
	}

	my @markers = $lag_stats->getElementsByTagName('lag-marker');
	return @markers;
}

sub check_interfaces
{
	my @targets = @_;

	my $opts = {
		with_description => 0,
	};

	if (grep { m/^\@with_description$/; } @targets) {
		$opts->{'with_description'} = 1;

		@targets = grep { ! m/^\@with_description$/; } @targets;
	}

	my @interfaces = get_interfaces($junos, $opts, @targets);;

	my $down_count = 0;
	my @down_ifaces = ();

	my $phys_down_count = 0;
	my @phys_down_ifaces = ();

	my $have_lag_ifaces = 0;

	foreach my $iface (@interfaces) {
		my $name = get_iface_name($iface);
		my $status = check_interface($iface, $opts, @targets);

		if ($status == 0) {
			++$down_count;
			push @down_ifaces, $name;
		}

		if ($status <= 0) {
			# disabled or down
			next;
		}

		if ($name !~ m/^ae/) {
			next;
		}

		$have_lag_ifaces = 1;

		my @markers = get_liface_marker(get_iface_first_logical($iface));
		if (! @markers) {
			next;
		}

		foreach my $marker (@markers) {
			my $phy_name = get_iface_name($marker);
			$phy_name =~ s/\.\d+$//;

			$plugin->verbose(3, "Quering physical interface '$phy_name' "
				. "for $name.");

			my @phy_interfaces = get_interfaces($junos, {}, $phy_name);
			foreach my $phy_iface (@phy_interfaces) {
				if (check_interface($phy_iface, {}, $phy_name) == 0) {
					++$phys_down_count;
					push @phys_down_ifaces, "$name -> $phy_name";
				}
			}
		}
	}

	if ($down_count > 0) {
		$plugin->add_message(CRITICAL, $down_count
			. " interfaces down (" . join(", ", @down_ifaces) . ")");
	}

	if ($phys_down_count > 0) {
		$plugin->add_message(WARNING, $phys_down_count
			. " LAG member interfaces down ("
			. join(", ", @phys_down_ifaces) . ")");
	}

	if ((! $down_count) && (! $phys_down_count)) {
		if (! scalar(@targets)) {
			$plugin->add_message(OK, "all interfaces up"
				. ($have_lag_ifaces
					? " (including all LAG member interfaces)" : ""));
		}
		else {
			$plugin->add_message(OK, "interface"
				. (scalar(@targets) == 1 ? " " : "s ")
				. join(", ", @targets) . " up"
				. ($have_lag_ifaces
					? " (including all LAG member interfaces)" : ""));
		}
	}
}

sub check_chassis_environment
{
	my @targets = @_;

	my $res = send_query($junos, 'get_environment_information');

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
	foreach my $item (get_object_by_spec($res, 'environment-item')) {
		my $name = get_object_value_by_spec($item, 'name');

		if (scalar(@targets) && (! grep { m/^$name$/ } @targets)) {
			next;
		}

		if (get_object_value_by_spec($item, 'class')) {
			$class = get_object_value_by_spec($item, 'class');
		}

		my $status = get_object_value_by_spec($item, 'status');

		if ($status eq "Absent") {
			if (! scalar(@targets)) {
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

		my $temp = get_object_value_by_spec($item, 'temperature');
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
		$plugin->add_message(UNKNOWN, "no components found");
	}
	elsif ($items_count == $items_ok) {
		$plugin->add_message(OK, "$items_ok components OK");
	}
	else {
		$plugin->add_message(WARNING,
			"$items_ok / $items_count components OK");
	}
}

sub check_system_storage
{
	my @targets = @_;

	my $res = send_query($junos, 'get_system_storage');

	foreach my $re (get_object_by_spec($res,
			'multi-routing-engine-item')) {
		my $re_name = get_object_value_by_spec($re, 're-name');

		foreach my $fs (get_object_by_spec($re,
				['system-storage-information', 'filesystem'])) {
			my $name = get_object_value_by_spec($fs, 'filesystem-name');
			my $mnt_pt = get_object_value_by_spec($fs, 'mounted-on');

			if (scalar(@targets) && (! grep { m/^$name$/ } @targets)
					&& (! grep { m/^$mnt_pt$/ } @targets)) {
				next;
			}

			my $used = get_object_value_by_spec($fs, 'used-percent') + 0;

			my $state = $plugin->check_threshold($used);
			if ($state != OK) {
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
}

