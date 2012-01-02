#! /usr/bin/perl -w

#############################################################################
# (c) 2001, 2003 Juniper Networks, Inc.                                     #
# (c) 2011 Sebastian "tokkee" Harl <sh@teamix.net>                          #
#          and team(ix) GmbH, Nuernberg, Germany                            #
#                                                                           #
# This file is part of "team(ix) Monitoring Plugins"                        #
# URL: http://oss.teamix.org/projects/monitoringplugins/                    #
# It is based on the example diagnose_bgp.pl script of the                  #
# JUNOScript distribution.                                                  #
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

use JUNOS::Device;
use JUNOS::Trace;
use Getopt::Std;
use Term::ReadKey;
use File::Basename;

use Data::Dumper;

my $jnx;

# send a query
sub send_query
{
	my $device = shift;
	my $query = shift;
	my $href_queryargs = shift;
	my $res;
	unless ( ref $href_queryargs ) {
		eval {
			$res = $device->$query();
		};
		if ($@) {
			$res = $device->command($query);
		}
	} else {
		my %queryargs = %$href_queryargs;
		print "$_ => $queryargs{$_}\n" foreach (keys %queryargs);
		$res = $device->$query(%queryargs);
	}

	unless ( ref $res ) {
		print STDERR "ERROR: Failed to execute query '$query'\n";
		return 0;
	}

	unless (ref $res) {
		print STDERR "ERROR: failed to execute command $query\n";
		return undef;
	}

	my $err = $res->getFirstError();
	if ($err) {
		print STDERR "ERROR: ", $err->{message}, "\n";
		return 0;
	}

	return $res;
}

# get object identified by the specified spec
sub get_object_by_spec
{
	my $res  = shift;
	my $spec = shift;

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

# print the usage of this script
sub output_usage
{
	my $usage = "Usage: $0 [options] <target> <query> [<arg1>=<value1> [...]]

Where:

  <target>   The hostname of the target router.
  <query>    The query to send to the target router.

Options:

  -l <login>    A login name accepted by the target router.
  -p <password> The password for the login name.
  -m <access>   Access method.  It can be clear-text, ssl, ssh or telnet.  Default: telnet.
  -s <spec>     Specify a value to extract from the output.
  -o <file>     Output file.  Default: dump.xml.
  -d            Turn on debug, full blast.\n\n";

	die $usage;
}

my %opt;
getopts('l:p:dm:x:o:s:h', \%opt) || output_usage();
output_usage() if $opt{h};

# Check whether trace should be turned on
JUNOS::Trace::init(1) if $opt{d};

my $hostname = shift || output_usage();
my $query    = shift || output_usage();

my %args     = map { split m/=/, $_ } @ARGV;
if ($opt{d}) {
	print "Args:\n";
	foreach my $key (keys %args) {
		print "\t$key => $args{$key}\n";
	}
}

# Retrieve the access method, can only be telnet or ssh.
my $access = $opt{m} || "telnet";
use constant VALID_ACCESSES => "telnet|ssh|clear-text|ssl";
output_usage() unless (VALID_ACCESSES =~ /$access/);

# Check whether login name has been entered.  Otherwise prompt for it
my $login = "";
if ($opt{l}) {
	$login = $opt{l};
} else {
	print "login: ";
	$login = ReadLine 0;
	chomp $login;
}

# Check whether password has been entered.  Otherwise prompt for it
my $password = "";
if ($opt{p}) {
	$password = $opt{p};
} else {
	print "password: ";
	ReadMode 'noecho';
	$password = ReadLine 0;
	chomp $password;
	ReadMode 'normal';
	print "\n";
}

# Get the name of the output file
my $outfile = $opt{o} || 'dump.xml';

# Retrieve command line arguments
my %deviceinfo = (
	access => $access,
	login => $login,
	password => $password,
	hostname => $hostname,
	'ssh-compress' => 0,
);

#
# CONNECT TO the JUNOScript server
# Create a device object that contains all necessary information to
# connect to the JUNOScript server at a specific router.
#

$jnx = new JUNOS::Device(%deviceinfo);
unless ( ref $jnx ) {
	die "ERROR: $deviceinfo{hostname}: failed to connect.\n";
}

my $spec = $opt{s} || undef;
if ($spec) {
	$spec = [ split(",", $spec) ];
}

my $res = send_query($jnx, $query, scalar(keys %args) ? \%args : undef);
while ($res) {
	if ($spec) {
		$res = get_object_by_spec($res, $spec);
	}

	if (! $res) {
		print "NO OUTPUT!\n";
		last;
	}

	if ($outfile eq "-") {
		print STDOUT $res->toString;
	}
	else {
		$res->printToFile($outfile);
	}
	last;
}

$jnx->request_end_session();
$jnx->disconnect();

