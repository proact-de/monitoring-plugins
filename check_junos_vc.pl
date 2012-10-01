#!/usr/bin/perl

#############################################################################
# (c) 2001, 2003 Juniper Networks, Inc.                                     #
# (c) 2011 Sebastian "tokkee" Harl <sh@teamix.net>                          #
#          and team(ix) GmbH, Nuernberg, Germany                            #
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

use Data::Dumper;

use POSIX qw( :termios_h );
use Nagios::Plugin;

use JUNOS::Device;

binmode STDOUT, ":utf8";

my $valid_checks = "members_count|master|backup|interfaces|version";

# TODO:
# (on newer JUNOS (10.4r5.5))
# request chassis routing-engine master switch check
# -> graceful switchover status

my $plugin = Nagios::Plugin->new(
	plugin    => 'check_junos_vc',
	shortname => 'check_junos_vc',
	version   => '0.1',
	url       => 'http://oss.teamix.org/projects/monitoringplugins',
	blurb     => 'Monitor Juniper™ Switch Virtual Chassis.',
	usage     =>
"Usage: %s [-v|--verbose] [-H <host>] [-p <port>] [-t <timeout]
[-U <user>] [-P <password] check-tuple [...]",
	license   =>
"This nagios plugin is free software, and comes with ABSOLUTELY NO WARRANTY.
It may be used, redistributed and/or modified under the terms of the 3-Clause
BSD License (see http://opensource.org/licenses/BSD-3-Clause).",
	extra     => "
This plugin connects to a Juniper™ Switch device and and checks Virtual
Chassis information.

A check-tuple consists of the name of the check and, optionally, a \"target\"
which more closely specifies which characteristics should be checked, and
warning and critical thresholds:
checkname[,target[,warning[,critical]]]

The following checks are available:
  * members_count: Total number of members in the Virtual Chassis. If a target
    is specified, only peers whose status (NotPrsnt, Prsnt) matches one of the
    specified targets are taken into account.

  * master, backup: Check the number or assignment of master resp. backup
    members. If a target is specified, check that those members whose serial
    number matches the specified target have the requested role (master,
    backup) assigned to them. Else, check the number of master resp. backup
    members against the specified thresholds.

  * interfaces: Check that all VCP interfaces are up. If warning or critical
    thresholds have been specified, also check the number of VCP interfaces
    against the thresholds.

  * version: Check the version of all physically connected members.

Warning and critical thresholds may be specified in the format documented at
http://nagiosplug.sourceforge.net/developer-guidelines.html#THRESHOLDFORMAT.",
);

# Predefined arguments (by Nagios::Plugin)
my @predefined_args = qw(
	usage
	help
	version
	extra-opts
	timeout
	verbose
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

my %conf  = ();
my $junos = undef;

foreach my $arg (@args) {
	add_arg($plugin, $arg);
}

$plugin->getopts;
# Initialize this first, so it may be used right away.
$conf{'verbose'} = $plugin->opts->verbose;

foreach my $arg (@args) {
	my @c = get_conf($plugin, $arg);
	$conf{$c[0]} = $c[1];
}

foreach my $arg (@predefined_args) {
	$conf{$arg} = $plugin->opts->$arg;
}

add_checks(\%conf, @ARGV);

if (! $plugin->opts->password) {
	my $term = POSIX::Termios->new();
	my $lflag;

	print "Password: ";

	$term->getattr(fileno(STDIN));
	$lflag = $term->getlflag;
	$term->setlflag($lflag & ~POSIX::ECHO);
	$term->setattr(fileno(STDIN), TCSANOW);

	$conf{'password'} = <STDIN>;
	chomp($conf{'password'});

	$term->setlflag($lflag | POSIX::ECHO);
	$term->setattr(fileno(STDIN), TCSAFLUSH);
	print "\n";
}

verbose(1, "Connecting to host $conf{'host'} as user $conf{'user'}.");
$junos = JUNOS::Device->new(
	hostname       => $conf{'host'},
	login          => $conf{'user'},
	password       => $conf{'password'},
	access         => 'ssh',
	'ssh-compress' => 0);

if (! ref $junos) {
	$plugin->die("ERROR: failed to connect to " . $conf{'host'} . "!");
}

my $vc              = undef;
my @vc_members      = ();
my $have_vc_members = 0;

foreach my $check (@{$conf{'checks'}}) {
	my $code;
	my $value;

	my @targets = ();

	if (defined $check->{'target'}) {
		@targets = @{$check->{'target'}};
	}

	$plugin->set_thresholds(
		warning  => $check->{'warning'},
		critical => $check->{'critical'},
	);

	if ($check->{'name'} eq 'members_count') {
		my @relevant_members = ();
		my $value = 0;
		my $code;

		@vc_members = get_vc_members($junos);

		if (scalar(@targets)) {
			foreach my $member (@vc_members) {
				my $role = get_member_status($member);
				if (scalar(grep { $role eq $_ } @targets)) {
					push @relevant_members, $member;
					$value++;
				}
			}
		}
		else {
			@relevant_members = @vc_members;
			$value = scalar(@vc_members);
		}

		$code = $plugin->check_threshold($value);

		$plugin->add_message($code, "$value " . join(" + ", @targets)
			. " member" . (($value == 1) ? "" : "s"));
		my $label = 'members';
		if (scalar(@targets)) {
			$label .= '[' . join('+', @targets) . ']';
		}
		$plugin->add_perfdata(
			label     => $label,
			value     => $value,
			min       => 0,
			max       => undef,
			uom       => '',
			threshold => $plugin->threshold(),
		);
	}
	elsif (($check->{'name'} eq 'master') || ($check->{'name'} eq 'backup')) {
		my $wanted_role = ($check->{'name'} eq 'master')
			? 'Master' : 'Backup';

		my @wanted_members = ();

		my $value;
		my $code;

		@vc_members = get_vc_members($junos);

		foreach my $member (@vc_members) {
			my $role = get_member_role($member);

			if ($role eq $wanted_role) {
				push @wanted_members, $member;
			}
		}

		if (scalar(@targets)) {
			my @ok_targets   = ();
			my @fail_targets = ();

			$code = UNKNOWN;

			foreach my $target (@targets) {
				if (scalar(grep { $target eq get_member_serial($_) } @wanted_members)) {
					# requested target does have wanted role assigned
					if (($code == UNKNOWN) || ($code == OK)) {
						$code = OK;
					}
					else {
						# we've had previous errors
						$code = WARNING;
					}

					push @ok_targets, $target;
				}
				else {
					if (($code == OK) || ($code == WARNING)) {
						# we've had previous success
						$code = WARNING;
					}
					else {
						$code = CRITICAL;
					}

					push @fail_targets, $target;
				}
			}

			$plugin->add_message($code, scalar(@fail_targets)
				. " missing/failed-over " . $check->{'name'}
				. ((scalar(@fail_targets) == 1) ? "" : "s")
				. (scalar(@fail_targets)
					? " (" . join(", ", @fail_targets) . ")" : "")
				. ", " . scalar(@ok_targets) . " active " . $check->{'name'}
				. ((scalar(@ok_targets) == 1) ? "" : "s")
				. (scalar(@ok_targets)
					? " (" . join(", ", @ok_targets) . ")" : ""));
			$plugin->add_perfdata(
				label     => 'active_' . $check->{'name'},
				value     => scalar(@ok_targets),
				min       => 0,
				max       => undef,
				uom       => '',
				threshold => undef,
			);
			$plugin->add_perfdata(
				label     => 'failed_' . $check->{'name'},
				value     => scalar(@fail_targets),
				min       => 0,
				max       => undef,
				uom       => '',
				threshold => undef,
			);
		}
		else {
			$value = scalar @wanted_members;
			$code  = $plugin->check_threshold($value);

			$plugin->add_message($code, "$value " . $check->{'name'} . " member"
				. (($value == 1) ? "" : "s"));
			$plugin->add_perfdata(
				label     => $check->{'name'},
				value     => $value,
				min       => 0,
				max       => undef,
				uom       => '',
				threshold => $plugin->threshold(),
			);
		}
	}
	elsif ($check->{'name'} eq 'interfaces') {
		my @up_ifaces   = ();
		my @down_ifaces = ();

		my @vc_interfaces = get_vc_interfaces($junos);

		foreach my $iface (@vc_interfaces) {
			my $status = get_iface_status($iface);

			if ($status eq 'up') {
				push @up_ifaces, get_iface_name($iface);
				next;
			}
			# else:

			push @down_ifaces, {
				name   => get_iface_name($iface),
				status => $status,
			};
		}

		if (scalar(@down_ifaces)) {
			$plugin->add_message(CRITICAL, scalar(@down_ifaces)
				. " VCP interface" . ((scalar(@down_ifaces) == 1) ? "" : "s")
				. " not up ("
				. join(", ",
					map { "$_->{'name'} $_->{'status'}" } @down_ifaces)
				. ")");
		}
		elsif ($check->{'warning'} || $check->{'critical'}) {
			my $value = scalar @vc_interfaces;
			my $code  = $plugin->check_threshold($value);

			$plugin->add_message($code, "$value VCP interface"
				. (($value == 1) ? "" : "s") . " found ("
				. scalar(@up_ifaces) . " up, "
				. scalar(@down_ifaces) . " down)");
		}
		elsif (! scalar(@up_ifaces)) {
			# no VCP interfaces at all
			$plugin->add_message(CRITICAL, "no VCP interfaces found");
		}
		else {
			$plugin->add_message(OK, "all VCP interfaces up");
		}

		$plugin->add_perfdata(
			label     => 'vcp_interfaces',
			value     => scalar(@vc_interfaces),
			min       => 0,
			max       => undef,
			uom       => '',
			threshold => $plugin->threshold(),
		);
		$plugin->add_perfdata(
			label     => 'up_interfaces',
			value     => scalar(@up_ifaces),
			min       => 0,
			max       => undef,
			uom       => '',
			threshold => undef,
		);
		$plugin->add_perfdata(
			label     => 'down_interfaces',
			value     => scalar(@down_ifaces),
			min       => 0,
			max       => undef,
			uom       => '',
			threshold => undef,
		);
	}
	elsif ($check->{'name'} eq 'version') {
		my %versions = get_versions($junos);
		my @v_keys   = keys %versions;

		my $first    = undef;

		my @base_mismatch = ();
		my %mismatches    = ();

		foreach my $k (@v_keys) {
			my $base  = $versions{$k}->{'base'};
			my $other = $versions{$k}->{'other'};

			foreach my $o (keys %$other) {
				if ($other->{$o} ne $base) {
					$mismatches{$k}->{$base} = 1;
					$mismatches{$k}->{$other->{$o}} = 1;
				}
			}
		}

		$first = shift @v_keys;
		$first = $versions{$first};
		foreach my $k (@v_keys) {
			if ($first->{'base'} ne $versions{$k}->{'base'}) {
				push @base_mismatch, $k;
			}
		}

		if (scalar @base_mismatch) {
			my @first_match = grep {
					$versions{$_}->{'base'} eq $first->{'base'}
				} keys %versions;
			my %mismatches = ();

			foreach my $m (@base_mismatch) {
				push @{$mismatches{$versions{$m}->{'base'}}}, $m;
			}

			$plugin->add_message(CRITICAL, "version mismatch detected: "
				. $first->{'base'} . " @ ("
				. join(", ", @first_match) . ") != "
				. join(" != ", map {
							$_ . " @ (" . join(", ", @{$mismatches{$_}}) . ")"
						} keys %mismatches));
		}
		elsif (scalar(keys %mismatches)) {
			$plugin->add_message(WARNING, "version mismatches detected: "
				. join(" / ", map {
						"$_: " . join(" != ", keys %{$mismatches{$_}})
					} keys %mismatches));
		}
		else {
			$plugin->add_message(OK, "all members at version "
				. $first->{'base'});
		}
	}
}

# add total numbers to perfdata to ease graphing stuff
if ($have_vc_members) {
	$plugin->add_perfdata(
		label     => 'members',
		value     => scalar(@vc_members),
		min       => 0,
		max       => undef,
		uom       => '',
		threshold => undef,
	);
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

	verbose(3, "Sending query '$query' to router.");

	if (ref $queryargs) {
		$res = $device->$query(%$queryargs);
	} else {
		$res = $device->$query();
	}

	verbose(5, "Got response: " . Dumper(\$res));

	if (! ref $res) {
		return "ERROR: Failed to execute query '$query'";
	}

	$err = $res->getFirstError();
	if ($err) {
		return "ERROR: " . $err->{message};
	}
	return $res;
}

sub send_command
{
	my $device = shift;
	my $cmd    = shift;

	my $res;
	my $err;

	verbose(3, "Sending command '$cmd' to router.");

	$res = $device->command($cmd);

	if (! ref $res) {
		return "ERROR: Failed to execute command '$cmd'";
	}

	$err = $res->getFirstError();
	if ($err) {
		return "ERROR: " . $err->{message};
	}
	return $res;
}

sub get_vc_information
{
	my $device   = shift;

	my $cmd = "show virtual-chassis status";
	my $res = send_command($device, $cmd);
	my $err;

	if (! ref $res) {
		return $res;
	}
	return $res;
}

sub get_vc_members
{
	my $device = shift;

	if ($have_vc_members) {
		return @vc_members;
	}

	$vc = get_vc_information($device);
	if (! ref $vc) {
		$plugin->die($vc);
	}
	my $vc_id = ($vc->getElementsByTagName('virtual-chassis-id-information'))[0];
	$vc_id    = ($vc_id->getElementsByTagName('virtual-chassis-id'))[0];
	$vc_id    = $vc_id->getFirstChild->getNodeValue;

	verbose(3, "Analyzing data from virtual chassis $vc_id.");

	@vc_members = ($vc->getElementsByTagName('member-list'))[0]->getElementsByTagName('member');
	if ($conf{'verbose'} >= 3) {
		my @m = map { get_member_id($_) . " => " . get_member_serial($_) }
			@vc_members;
		verbose(3, "Members: " . join(", ", @m));
	}
	$have_vc_members = 1;
	return @vc_members;
}

sub get_vc_interfaces
{
	my $device = shift;
	my @ifaces = ();

	my $cmd  = "get_interface_information";
	my %args = ( interface_name => 'vcp*' );
	my $res  = send_query($device, $cmd, \%args);

	if (! ref $res) {
		$plugin->die($res);
	}

	@ifaces = $res->getElementsByTagName('physical-interface');
	if ($conf{'verbose'} >= 3) {
		my @i = map { get_iface_name($_) . " => " . get_iface_status($_) }
			@ifaces;
		verbose(3, "VCP Interfaces: " . join(", ", @i));
	}
	return @ifaces;
}

sub get_versions
{
	my $device   = shift;
	my %versions = ();

	my $cmd = "show version";
	my $res = send_command($device, $cmd);

	my @v = ();

	if (! ref $res) {
		$plugin->die($res);
	}

	@v = $res->getElementsByTagName('multi-routing-engine-item');

	foreach my $i (@v) {
		my $name  = get_obj_element($i, 're-name');
		my @infos = $i->getElementsByTagName('software-information');

		@infos = $infos[0]->getElementsByTagName('package-information');

		foreach my $j (@infos) {
			my $comment = get_obj_element($j, 'comment');
			my ($desc, $version);

			$comment =~ m/^(.*) \[([^]]+)\]$/;
			$desc    = $1;
			$version = $2;

			if ($desc eq "JUNOS Base OS boot") {
				$versions{$name}->{'base'} = $version;
			}
			else {
				$versions{$name}->{'other'}->{$desc} = $version;
			}
		}
	}
	return %versions;
}

sub add_arg
{
	my $plugin = shift;
	my $arg    = shift;

	my $spec = $arg->{'spec'};
	my $help = $arg->{'usage'};

	if (defined $arg->{'desc'}) {
		my @desc;

		if (ref($arg->{'desc'})) {
			@desc = @{$arg->{'desc'}};
		}
		else {
			@desc = ( $arg->{'desc'} );
		}

		foreach my $d (@desc) {
			$help .= "\n   $d";
		}

		if (defined $arg->{'default'}) {
			$help .= " (default: $arg->{'default'})";
		}
	}
	elsif (defined $arg->{'default'}) {
		$help .= "\n   (default: $arg->{'default'})";
	}

	$plugin->add_arg(
		spec => $spec,
		help => $help,
	);
}

sub get_conf
{
	my $plugin = shift;
	my $arg    = shift;

	my ($name, undef) = split(m/\|/, $arg->{'spec'});
	my $value = $plugin->opts->$name || $arg->{'default'};

	if ($name eq 'password') {
		verbose(3, "conf: password => "
			. (($value eq '<prompt>') ? '<prompt>' : '<hidden>'));
	}
	else {
		verbose(3, "conf: $name => $value");
	}
	return ($name => $value);
}

sub add_single_check
{
	my $conf  = shift;
	my @check = split(m/,/, shift);

	my %c = ();

	if ($check[0] !~ m/\b(?:$valid_checks)\b/) {
		return "ERROR: invalid check '$check[0]'";
	}

	$c{'name'} = $check[0];

	$c{'target'} = undef;
	if (defined($check[1])) {
		$c{'target'} = [ split(m/\+/, $check[1]) ];
	}

	$c{'warning'}    = $check[2];
	$c{'critical'}   = $check[3];

	# check for valid thresholds
	# set_threshold() will die if any threshold is not valid
	$plugin->set_thresholds(
		warning  => $c{'warning'},
		critical => $c{'critical'},
	) || $plugin->die("ERROR: Invalid thresholds: "
		. "warning => $c{'warning'}, critical => $c{'critical'}");

	push @{$conf->{'checks'}}, \%c;
}

sub add_checks
{
	my $conf    = shift;
	my @checks  = @_;

	my $err_str = "ERROR:";

	if (scalar(@checks) == 0) {
		$conf->{'checks'}[0] = {
			name     => 'members_count',
			target   => [],
			warning  => undef,
			critical => undef,
		};
		return 1;
	}

	$conf->{'checks'} = [];

	foreach my $check (@checks) {
		my $e;

		$e = add_single_check($conf, $check);
		if ($e =~ m/^ERROR: (.*)$/) {
			$err_str .= " $1,";
		}
	}

	if ($err_str ne "ERROR:") {
		$err_str =~ s/,$//;
		$plugin->die($err_str);
	}
}

sub get_obj_element
{
	my $obj  = shift;
	my $elem = shift;

	$elem = $obj->getElementsByTagName($elem);
	return $elem->item(0)->getFirstChild->getNodeValue;
}

sub get_member_id
{
	my $member = shift;
	return get_obj_element($member, 'member-id');
}

sub get_member_serial
{
	my $member = shift;
	return get_obj_element($member, 'member-serial-number');
}

sub get_member_status
{
	my $member = shift;
	return get_obj_element($member, 'member-status');
}

sub get_member_role
{
	my $member = shift;
	my $elem;

	$elem = $member->getElementsByTagName('member-role');
	if ($elem && $elem->item(0)) {
		$elem = $elem->item(0)->getFirstChild->getNodeValue;
		# e.g., '*' may be appended to the member-role
		$elem =~ s/\W//g;
		return $elem;
	}
	else {
		return "";
	}
}

sub get_iface_name
{
	my $iface = shift;
	return get_obj_element($iface, 'name');
}

sub get_iface_status
{
	my $iface = shift;
	return get_obj_element($iface, 'oper-status');
}

sub verbose
{
	my $level = shift;
	my @msgs  = @_;

	if ($level > $conf{'verbose'}) {
		return;
	}

	foreach my $msg (@msgs) {
		print "V$level: $msg\n";
	}
}

