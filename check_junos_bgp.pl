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

use Regexp::Common;
use Regexp::IPv6 qw( $IPv6_re );

use JUNOS::Device;

binmode STDOUT, ":utf8";

my $valid_checks = "peers_count|prefix_count";

my $plugin = Nagios::Plugin->new(
	plugin    => 'check_junos_bgp',
	shortname => 'check_junos_bgp',
	version   => '0.1',
	url       => 'http://oss.teamix.org/projects/monitoringplugins',
	blurb     => 'Monitor Juniper™ Router\'s BGP tables.',
	usage     =>
"Usage: %s [-v|--verbose] [-H <host>] [-p <port>] [-t <timeout]
[-U <user>] [-P <password] check-tuple [...]",
	license   =>
"This nagios plugin is free software, and comes with ABSOLUTELY NO WARRANTY.
It may be used, redistributed and/or modified under the terms of the 3-Clause
BSD License (see http://opensource.org/licenses/BSD-3-Clause).",
	extra     => "
This plugin connects to a Juniper™ Router device and requests BGP table
information using the 'show bgp neighbor' command. It then checks the
specified thresholds depending on the specified checks.

A check-tuple consists of the name of the check and, optionally, a \"target\"
(e.g., peer address), and warning and critical thresholds:
checkname[,target[,warning[,critical]]]

The following checks are available:
  * peers_count: Total number of peers. If a target is specified, only peers
    matching that target are taken into account.

  * prefix_count: Number of active prefixes for a single peer. If multiple
    peers match the specified target, each of those is checked against the
    specified thresholds.

Targets are either specified as IPv4/IPv6 addresses or regular expressions /
strings. In the former case, the target is compared against the peer's
address, else against the peer's description. When specifying regular
expressions, they have to be enclosed in '/'. Else, the pattern is treated as
verbatim string that has to be matched.

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

my $neigh_info = undef;
my @peers      = ();

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

verbose(1, "Querying BGP neighbor information.");
$neigh_info = get_neighbor_information($junos);
if (! ref $neigh_info) {
	$plugin->die($neigh_info);
}

@peers = $neigh_info->getElementsByTagName('bgp-peer');
if ($conf{'verbose'} >= 3) {
	my @p = map { (get_peer_address($_) // "<unknown address>")
		. " => " . (get_peer_description($_) // "<unkown description>") } @peers;
	verbose(3, "Peers: " . join(", ", @p));
}

foreach my $check (@{$conf{'checks'}}) {
	my $code;
	my $value;

	my @relevant_peers = get_relevant_peers($check, @peers);
	if ($conf{'verbose'} >= 2) {
		my @p = map { (get_peer_address($_) // "<unknown address>")
			. " => " . (get_peer_description($_) // "<unkown description>") } @relevant_peers;
		verbose(2, "Relevant peers: " . join(", ", @p));
	}

	$plugin->set_thresholds(
		warning  => $check->{'warning'},
		critical => $check->{'critical'},
	);

	if ($check->{'name'} eq 'peers_count') {
		$value = scalar(@relevant_peers);
		$code  = $plugin->check_threshold($value);

		$plugin->add_message($code, "$value peer" . (($value == 1) ? "" : "s"));
		$plugin->add_perfdata(
			label     => 'peers_count',
			value     => $value,
			min       => 0,
			max       => undef,
			uom       => '',
			threshold => $plugin->threshold(),
		);
	}
	elsif ($check->{'name'} eq 'prefix_count') {
		foreach my $peer (@relevant_peers) {
			my $peer_addr = get_peer_address($peer);

			if (! defined($peer_addr)) {
				$peer_addr = "<unkown address>";
			}

			$value = get_peer_element($peer, 'peer-state');

			if (! defined($value)) {
				$value = "<unknown state>";
			}

			verbose(2, "Peer $peer_addr: peer-state = $value.");

			if ($value eq 'Established') {
				$value = $peer->getElementsByTagName('bgp-rib');
				$value = get_peer_element($value->[0], 'active-prefix-count');
				if (! $value) {
					$value = 0;
				}
				$code  = $plugin->check_threshold($value);
				$plugin->add_message($code, "peer $peer_addr: $value prefix"
					. (($value == 1) ? "" : "es"));

				verbose(2, "Peer $peer_addr: active-prefix-count = $value.");
			}
			else {
				$value = "";
				$code  = CRITICAL;
				$plugin->add_message($code,
					"peer $peer_addr: no established connection");
			}

			$plugin->add_perfdata(
				label     => '\'prefix_count[' . $peer_addr . ']\'',
				value     => $value,
				min       => 0,
				max       => undef,
				uom       => '',
				threshold => $plugin->threshold(),
			);
		}
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

sub get_neighbor_information
{
	my $device   = shift;
	my @table;

	my $query = "get_bgp_summary_information";
	my $res   = send_query($device, $query);
	my $err;

	if (! ref $res) {
		return $res;
	}

	$err = $res->getFirstError();
	if ($err) {
		return "ERROR: " . $err->{message};
	}
	return $res;
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

	if ((! defined($check[1])) || ($check[1] eq "")) {
		$c{'target'} = qr//,
		$c{'ttype'}  = 'address',
	}
	elsif ($check[1] =~ m/^(?:$RE{'net'}{'IPv4'}|$IPv6_re)$/) {
		$c{'target'} = $check[1];
		$c{'ttype'}  = 'address';
	}
	elsif ($check[1] =~ m/^\/(.*)\/$/) {
		$c{'target'} = qr/$1/;
		$c{'ttype'}  = 'description';
	}
	else {
		$c{'target'} = $check[1];
		$c{'ttype'}  = 'description';
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
			name     => 'peers_count',
			target   => qr//,
			ttype    => 'address',
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

sub get_relevant_peers
{
	my $check = shift;
	my @peers = @_;

	my @rpeers = ();

	my $cmp = sub {
		my ($a, $b, undef) = @_;
		if (ref $b) {
			my $r = $a =~ $b;
			verbose(3, "Checking peer '$a' against regex '$b' -> "
				. ($r ? "true" : "false") . ".");
			return $r;
		}
		else {
			my $r = $a eq $b;
			verbose(3, "Comparing peer '$a' with string '$b' -> "
				. ($r ? "true" : "false") . ".");
			return $r;
		}
	};

	my $get_peer_elem;

	if ($check->{'ttype'} eq 'description') {
		$get_peer_elem = \&get_peer_description;
	}
	else {
		$get_peer_elem = \&get_peer_address;
	}

	@rpeers = grep { $cmp->($get_peer_elem->($_), $check->{'target'}) } @peers;
	return @rpeers;
}

sub get_peer_element
{
	my $peer = shift;
	my $elem = shift;

	my $e;

	if (! $peer) {
		print STDERR "Cannot retrieve element '$elem' "
			. "from undefined value.\n";
		return;
	}

	$e = $peer->getElementsByTagName($elem);
	if ((! $e) || (! $e->item(0))) {
		print STDERR "Attribute '$elem' not found for peer.\n";
		verbose(3, "Peer was: " . Dumper($peer));
		return;
	}

	return $e->item(0)->getFirstChild->getNodeValue;
}

sub get_peer_description
{
	my $peer = shift;
	return get_peer_element($peer, 'description');
}

sub get_peer_address
{
	my $peer = shift;
	return get_peer_element($peer, 'peer-address');
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

