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

package Nagios::Plugin::NetApp;

use Carp;

use POSIX qw( :termios_h );

use Nagios::Plugin;
use NaServer;

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
	$self->{'srv'}     = undef;

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
			desc    => 'Hostname/IP of NetApp filer to connect to',
			default => 'localhost',
		},
		{
			spec    => 'port|p=i',
			usage   => '-p, --port=PORT',
			desc    => 'Port to connect to',
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
		{
			spec    => 'transport|t=s',
			usage   => '-t, --transport=TRANSPORT',
			desc    => 'Transport for the connection',
			default => 'HTTP',
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
		$c{'target'} = [ split(m/\+/, $check[1]) ];
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

	my $srv;

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
	$srv = new NaServer($host, 1, 7);
	if (! $srv) {
		$self->die("ERROR: failed to connect to $host!");
	}

	$srv->set_admin_user($user, $self->{'conf'}->{'password'});
	$srv->set_transport_type($self->{'conf'}->{'transport'});

	if ($self->{'conf'}->{'port'}) {
		$srv->set_port($self->{'conf'}->{'port'});
	}

	$srv->set_timeout($self->{'conf'}->{'timeout'});

	$self->{'srv'} = $srv;
	return $srv;
}

sub run_checks
{
	my $self = shift;

	foreach my $check ($self->get_checks()) {
		my @targets = ();

		if (defined $check->{'target'}) {
			@targets = @{$check->{'target'}};
		}

		$self->set_thresholds(
			warning  => $check->{'warning'},
			critical => $check->{'critical'},
		);

		my $sub = $self->get_check_impl($check->{'name'});
		$sub->($self, $self->{'srv'}, @targets);
	}
}

sub get_error
{
	my $self = shift;

	my $res = shift;
	my $msg = shift;

	if (! defined($res)) {
		return "$msg: Unknown error";
	}
	elsif ((ref($res) eq "NaElement") && (($res->results_errno != 0)
			|| ($res->results_status() eq "failed"))) {
		return "$msg: " . $res->results_reason();
	}
	return;
}

sub die_on_error
{
	my $self = shift;

	if ($self->get_error(@_)) {
		$self->die($self->get_error(@_));
	}
	return 1;
}

sub nagios_exit
{
	my $self = shift;

	if ($self->{'srv'}) {
		$self->{'srv'} = undef;
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

