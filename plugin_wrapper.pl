#! /usr/bin/perl

#####################################################################
# (c) 2012 Sebastian "tokkee" Harl <sh@teamix.net>                  #
#          and team(ix) GmbH, Nuernberg, Germany                    #
#                                                                   #
# This file is part of "team(ix) Monitoring Plugins"                #
# URL: http://oss.teamix.org/projects/monitoringplugins/            #
#                                                                   #
# This file is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published #
# by the Free Software Foundation, either version 2 of the License, #
# or (at your option) any later version.                            #
#                                                                   #
# This file is distributed in the hope that it will be useful, but  #
# WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the      #
# GNU General Public License for more details.                      #
#                                                                   #
# You should have received a copy of the GNU General Public License #
# along with this file. If not, see <http://www.gnu.org/licenses/>. #
#####################################################################

use strict;
use warnings;

my $p_script = shift;
my @p_args   = @ARGV;

if (! $p_script) {
	exit_usage(1);
}

my $p_stdout;
my $p_pid = open($p_stdout, '-|', "$p_script @p_args 2>&1");
if (! defined($p_pid)) {
	print "CRITICAL: Failed to execute plugin ($p_script): $!\n";
	print "Commandline: $p_script @p_args\n";
	exit 2;
}

my @p_output = <$p_stdout>;
if (waitpid($p_pid, 0) != $p_pid) {
	print "UNKNOWN: Lost track of plugin process\n";
	exit 3;
}
my $p_rc  = $?;
my $p_sig = $p_rc & 127;
my $p_cd  = $p_rc & 128; # core dumped?
$p_rc >>= 8;
close $p_stdout;

if ($p_sig || $p_cd) {
	print "CRITICAL: Plugin died with signal $p_sig (exit code: $p_rc)"
		. ($p_cd ? " (core dumped)" : "") . "\n";
	$p_rc = 2;
}

if ($p_rc == 255) {
	print "CRITICAL: Plugin died with status 255 "
		. "(see details for more info)\n";
	print "Commandline: $p_script @p_args\n";
}

my $p_output = join('', @p_output);
print $p_output;

if (($p_rc < 0) || ($p_rc > 3)) {
	$p_rc = 3;
}

exit $p_rc;

sub exit_usage {
	my $status = shift || 0;
	print STDERR "Usage: $0 <plugin> [<args>]\n";
	exit $status;
}

