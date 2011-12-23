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

use POSIX qw( :termios_h );
use Nagios::Plugin;

use JUNOS::Device;

binmode STDOUT, ":utf8";

my $valid_checks = "interfaces|chassis_environment";

# TODO:
# * chassis_routing_engine: show chassis routing-engine (-> number and status)
#
# * storage: show system storage

my $plugin = Nagios::Plugin->new(
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
    (as provided by 'show chassis environment').

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

	if ($check->{'name'} eq 'interfaces') {
		my @interfaces = get_interfaces($junos, @targets);;

		my $down_count = 0;
		my @down_ifaces = ();

		my $phys_down_count = 0;
		my @phys_down_ifaces = ();

		my $have_lag_ifaces = 0;

		foreach my $iface (@interfaces) {
			my $name = get_iface_name($iface);
			my $status = check_interface($iface, @targets);

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

				verbose(3, "Quering physical interface '$phy_name' "
					. "for $name.");

				my @phy_interfaces = get_interfaces($junos, $phy_name);
				foreach my $phy_iface (@phy_interfaces) {
					if (check_interface($phy_iface, $phy_name) == 0) {
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
				$plugin->add_message(OK, "all interfaces up");
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
	elsif ($check->{'name'} eq 'chassis_environment') {
		# XXX
		#show chassis environment (see check_snmp_environment)
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

	verbose(3, "Sending query '$query' to router.");

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
	my @targets = @_;

	my $name = get_iface_name($iface);
	my $admin_status = get_iface_admin_status($iface);

	if ($admin_status !~ m/^up$/) {
		if (grep { $name =~ m/^$_$/; } @targets) {
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
	my @targets = @_;
	my @ifaces  = ();

	my $cmd = 'get_interface_information';
	my $res;

	my $args = { detail => 1 };

	if (scalar(@targets) == 1) {
		$args->{'interface_name'} = $targets[0];
	}
	$res = send_query($device, $cmd, $args);

	if (! ref $res) {
		$plugin->die($res);
	}

	@ifaces = $res->getElementsByTagName('physical-interface');

	@targets = map { s/\*/\.\*/g; s/\?/\./g; $_; } @targets;

	if (scalar(@targets)) {
		@ifaces = grep {
			my $i = $_;
			grep { get_iface_name($i) =~ m/^$_$/ } @targets;
		} @ifaces;
	}

	if ($conf{'verbose'} >= 3) {
		my @i = map { get_iface_name($_) . " => " . get_iface_status($_) }
			@ifaces;
		verbose(3, "Interfaces: " . join(", ", @i));
	}
	return @ifaces;
}

sub get_obj_element
{
	my $obj  = shift;
	my $elem = shift;

	$elem = $obj->getElementsByTagName($elem);
	return $elem->item(0)->getFirstChild->getNodeValue;
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
			name     => 'chassis_environment',
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

