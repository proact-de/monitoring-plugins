#############################################################################
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

package Nagios::Plugin::JUNOS;

use Carp;

use Data::Dumper;

use POSIX qw( :termios_h );

use Nagios::Plugin;
use JUNOS::Device;

use Nagios::Plugin::Functions qw( %ERRORS %STATUS_TEXT @STATUS_CODES );

# re-export Nagios::Plugin's (default) exports
use Exporter;
our @ISA = qw( Nagios::Plugin Exporter );
our @EXPORT = (@STATUS_CODES);
our @EXPORT_OK = qw( %ERRORS %STATUS_TEXT );

sub new
{
	my $class = shift;
	my %args  = @_;

	my $self = Nagios::Plugin->new(%args);

	$self->{'conf'}    = { verbose => 0 };
	$self->{'cl_args'} = [];
	$self->{'junos'}   = undef;

	return bless($self, $class);
}

sub add_arg
{
	my $self = shift;
	my $arg  = shift;

	my $spec = $arg->{'spec'};
	my $help;

	push @{$self->{'cl_args'}}, $arg;

	if (defined $arg->{'usage'}) {
		$help = $arg->{'usage'};
	}
	else {
		$help = $arg->{'help'};
	}

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

	$self->SUPER::add_arg(
		spec => $spec,
		help => $help,
	);
}

sub add_common_args
{
	my $self = shift;

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

	foreach my $arg (@args) {
		$self->add_arg($arg);
	}
}

sub add_check_impl
{
	my $self = shift;
	my $name = shift;
	my $sub  = shift;

	if ((! $name) || (! $sub) || (ref($sub) ne "CODE")) {
		carp "Invalid check specification: $name -> $sub";
		return;
	}

	if (! defined($self->{'check_impls'})) {
		$self->{'check_impls'} = {};
	}

	$self->{'check_impls'}->{$name} = $sub;
}

sub get_check_impl
{
	my $self = shift;
	my $name = shift;

	if (! defined($self->{'check_impls'}->{$name})) {
		return;
	}
	return $self->{'check_impls'}->{$name};
}

sub is_valid_check
{
	my $self = shift;
	my $name = shift;

	if (defined $self->{'check_impls'}->{$name}) {
		return 1;
	}
	return;
}

sub set_default_check
{
	my $self = shift;
	my $def  = shift;

	if (! $self->is_valid_check($def)) {
		carp "set_default_check: Check '$def' does not exist";
		return;
	}

	$self->{'default_check'} = $def;
}

sub configure
{
	my $self = shift;

	# Predefined arguments (by Nagios::Plugin)
	my @predefined_args = qw(
		usage
		help
		version
		extra-opts
		timeout
		verbose
	);

	$self->getopts;
	# Initialize this first, so it may be used right away.
	$self->{'conf'}->{'verbose'} = $self->opts->verbose;

	foreach my $arg (@{$self->{'cl_args'}}) {
		my @c = $self->_get_conf($arg);
		$self->{'conf'}->{$c[0]} = $c[1];
	}

	foreach my $arg (@predefined_args) {
		$self->{'conf'}->{$arg} = $self->opts->$arg;
	}
}

sub _get_conf
{
	my $self = shift;
	my $arg  = shift;

	my ($name, undef) = split(m/\|/, $arg->{'spec'});
	my $value = $self->opts->$name || $arg->{'default'};

	if ($name eq 'password') {
		$self->verbose(3, "conf: password => "
			. (($value eq '<prompt>') ? '<prompt>' : '<hidden>'));
	}
	else {
		$self->verbose(3, "conf: $name => $value");
	}
	return ($name => $value);
}

sub _add_single_check
{
	my $self  = shift;
	my @check = split(m/,/, shift);

	my %c = ();

	if (! $self->is_valid_check($check[0])) {
		return "ERROR: invalid check '$check[0]'";
	}

	$c{'name'} = $check[0];

	$c{'target'} = undef;
	if (defined($check[1])) {
		my @tmp = split(m/(\+|\~)/, $check[1]);

		$c{'target'}  = [];
		$c{'exclude'} = [];

		for (my $i = 0; $i < scalar(@tmp); ++$i) {
			my $t = $tmp[$i];

			if ((($t ne "+") && ($t ne "~")) || ($i == $#tmp)) {
				push @{$c{'target'}}, $t;
				next;
			}

			++$i;

			if ($t eq "+") {
				push @{$c{'target'}}, $tmp[$i];
			}
			else {
				push @{$c{'exclude'}}, $tmp[$i];
			}
		}
	}

	$c{'warning'}    = $check[2];
	$c{'critical'}   = $check[3];

	# check for valid thresholds
	# set_threshold() will die if any threshold is not valid
	$self->set_thresholds(
		warning  => $c{'warning'},
		critical => $c{'critical'},
	) || $self->die("ERROR: Invalid thresholds: "
		. "warning => $c{'warning'}, critical => $c{'critical'}");

	push @{$self->{'conf'}->{'checks'}}, \%c;
}

sub set_checks
{
	my $self   = shift;
	my @checks = @_;

	my $err_str = "ERROR:";

	if (! defined($self->{'conf'}->{'timeout'})) {
		croak "No timeout set -- did you call configure()?";
	}

	if (scalar(@checks) == 0) {
		if ($self->{'default_check'}) {
			$self->{'conf'}->{'checks'}->[0] = {
				name     => $self->{'default_check'},
				target   => [],
				exclude  => [],
				warning  => undef,
				critical => undef,
			};
		}
		return 1;
	}

	$self->{'conf'}->{'checks'} = [];

	foreach my $check (@checks) {
		my $e;

		$e = $self->_add_single_check($check);
		if ($e =~ m/^ERROR: (.*)$/) {
			$err_str .= " $1,";
		}
	}

	if ($err_str ne "ERROR:") {
		$err_str =~ s/,$//;
		$self->die($err_str);
	}
}

sub get_checks
{
	my $self = shift;
	return @{$self->{'conf'}->{'checks'}};
}

sub connect
{
	my $self = shift;

	my $host = $self->{'conf'}->{'host'};
	my $user = $self->{'conf'}->{'user'};

	if ((! $host) || (! $user)) {
		croak "Host and/or user not set -- did you call configure()?";
	}

	if (! $self->opts->password) {
		my $term = POSIX::Termios->new();
		my $lflag;

		print "Password: ";

		$term->getattr(fileno(STDIN));
		$lflag = $term->getlflag;
		$term->setlflag($lflag & ~POSIX::ECHO);
		$term->setattr(fileno(STDIN), TCSANOW);

		$self->{'conf'}->{'password'} = <STDIN>;
		chomp($self->{'conf'}->{'password'});

		$term->setlflag($lflag | POSIX::ECHO);
		$term->setattr(fileno(STDIN), TCSAFLUSH);
		print "\n";
	}

	$self->verbose(1, "Connecting to host $host as user $user.");
	$junos = JUNOS::Device->new(
		hostname       => $host,
		login          => $user,
		password       => $self->{'conf'}->{'password'},
		access         => 'ssh',
		'ssh-compress' => 0);

	if (! ref $junos) {
		$self->die("ERROR: failed to connect to $host!");
	}

	$self->{'junos'} = $junos;
	return $junos;
}

sub run_checks
{
	my $self = shift;

	foreach my $check ($self->get_checks()) {
		my $targets = [];
		my $exclude = [];

		if (defined $check->{'target'}) {
			$targets = $check->{'target'};
		}

		if (defined $check->{'exclude'}) {
			$exclude = $check->{'exclude'};
		}

		$self->set_thresholds(
			warning  => $check->{'warning'},
			critical => $check->{'critical'},
		);

		my $sub = $self->get_check_impl($check->{'name'});
		$sub->($self, $self->{'junos'}, $targets, $exclude);
	}
}

sub send_query
{
	my $self      = shift;
	my $query     = shift;
	my $queryargs = shift || {};

	my $res;
	my $err;

	$self->verbose(3, "Sending query '$query' "
		. join(", ", map { "$_ => $queryargs->{$_}" } keys %$queryargs)
		. " to router.");

	if (scalar(keys %$queryargs)) {
		$res = $self->{'junos'}->$query(%$queryargs);
	} else {
		eval {
			$res = $self->{'junos'}->$query();
		};
		if ($@) {
			$res = $self->{'junos'}->command($query);
		}
	}

	$self->verbose(5, "Got response: " . Dumper(\$res));

	if (! ref $res) {
		return "ERROR: Failed to execute query '$query'";
	}

	$err = $res->getFirstError();
	if ($err) {
		return "ERROR: " . $err->{message};
	}
	return $res;
}

sub get_query_object
{
	my $self = shift;
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

sub get_query_object_value
{
	my $self = shift;
	my $res  = $self->get_query_object(@_);

	if (! $res) {
		return;
	}

	if (ref($res) eq "XML::DOM::NodeList") {
		$res = $res->item(0);
	}

	return $res->getFirstChild->getNodeValue;
}

sub nagios_exit
{
	my $self = shift;

	if ($self->{'junos'}) {
		$self->{'junos'}->disconnect();
	}
	$self->SUPER::nagios_exit(@_);
}

sub verbose
{
	my $self  = shift;
	my $level = shift;
	my @msgs  = @_;

	if ($level > $self->{'conf'}->{'verbose'}) {
		return;
	}

	foreach my $msg (@msgs) {
		print "V$level: $msg\n";
	}
}

return 1;

