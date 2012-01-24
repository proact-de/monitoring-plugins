#!/usr/bin/perl

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

use utf8;

use FindBin qw( $Bin );
use lib "$Bin/perl/lib";
use Nagios::Plugin::NetApp;

binmode STDOUT, ":utf8";

my $plugin = Nagios::Plugin::NetApp->new(
	plugin    => 'check_naf_exports',
	shortname => 'check_naf_exports',
	version   => '0.1',
	url       => 'http://oss.teamix.org/projects/monitoringplugins',
	blurb     => 'Monitor NetApp™ NFS exports.',
	usage     =>
"Usage: %s [-v|--verbose] [-H <host>] [-p <port>] [-t <timeout]
[-U <user>] [-P <password] check-tuple [...]",
	license   =>
"This nagios plugin is free software, and comes with ABSOLUTELY NO WARRANTY.
It may be used, redistributed and/or modified under the terms of the GNU
General Public License, either version 2 or (at your option) any later version
(see http://opensource.org/licenses/GPL-2.0).",
	extra     => "
This plugin connects to a NetApp™ filer and checks NFS exports related issues.

A check-tuple consists of the name of the check and, optionally, a \"target\"
which more closely specifies which characteristics should be checked, and
warning and critical thresholds:
checkname[,target[,warning[,critical]]]

The following checks are available:
 * exportfs_consistent: Check if /etc/exports is consistent with the currently
   exported filessytems.

Warning and critical thresholds may be specified in the format documented at
http://nagiosplug.sourceforge.net/developer-guidelines.html#THRESHOLDFORMAT.",
);

my %checks = (
	exportfs_consistent => \&check_exportfs_consistent,
);

my $srv = undef;

$plugin->add_common_args();

foreach my $check (keys %checks) {
	$plugin->add_check_impl($check, $checks{$check});
}

$plugin->set_default_check('exportfs_consistent');

# configure removes any options from @ARGV
$plugin->configure();
$plugin->set_checks(@ARGV);
$srv = $plugin->connect();

$plugin->run_checks();

my ($code, $msg) = $plugin->check_messages(join => ', ');

$plugin->nagios_exit($code, $msg);

sub get_exports_rules
{
	my $srv        = shift;
	my $persistent = shift;

	my $res = undef;

	$res = $srv->invoke('nfs-exportfs-list-rules', 'persistent', $persistent);
	$plugin->die_on_error($res, "Failed to read exports information");

	if (! $res->child_get('rules')) {
		return ();
	}

	my %exports = ();
	foreach my $rule ($res->child_get('rules')->children_get()) {
		my %rule;
		my $tmp;

		foreach my $info (qw( actual-pathname anon nosuid pathname )) {
			$tmp = $rule->child_get_string($info);
			if (defined($tmp)) {
				$rule{$info} = $tmp;
			}
		}

		foreach my $info (qw( read-only read-write root )) {
			my %info = ();

			if (! $rule->child_get($info)) {
				next;
			}

			foreach my $host_info ($rule->child_get($info)->children_get()) {
				my $host;

				my $all_hosts = $host_info->child_get_string('all-hosts');
				my $negate = $host_info->child_get_string('negate');

				$all_hosts ||= "false";
				$negate ||= "false";

				if ($all_hosts eq 'true') {
					$host = '*';
				}
				else {
					$host = $host_info->child_get_string('name');
				}

				if ($negate eq 'true') {
					$info{$host} = 1;
				}
				else {
					$info{$host} = 0;
				}
			}

			$rule{$info} = \%info;
		}

		if ($rule->child_get('sec-flavor')) {
			my %sec_flavors = map {
					$_->child_get_string('flavor') => 1
				} $rule->child_get('sec-flavor')->children_get();
			$rule{'sec-flavor'} = \%sec_flavors;
		}

		$exports{$rule{'pathname'}} = \%rule;
	}

	return %exports;
}

sub check_exportfs_consistent
{
	my $plugin  = shift;
	my $srv     = shift;
	my @targets = @_;

	my %exports = get_exports_rules($srv, 'true');
	my %memory  = get_exports_rules($srv, 'false');

	# diff export rules
	foreach my $path (keys %memory) {
		if (! defined($exports{$path})) {
			$plugin->add_message(CRITICAL,
				"$path not exported in /etc/exports");
			next;
		}

		my %export = %{$exports{$path}};
		my %mem    = %{$memory{$path}};

		foreach my $info (qw( actual-pathname anon nosuid pathname )) {
			my $e = $export{$info};
			my $m = $mem{$info};

			if ((! defined($e)) && (! defined($m))) {
				next;
			}

			$e ||= "<empty>";
			$m ||= "<empty>";

			if ($e ne $m) {
				$plugin->add_message(CRITICAL, "$path: $info differ "
					. "(exports: $e, exportfs: $m)");
			}
		}

		foreach my $info (qw( read-only read-write root )) {
			my $e = $export{$info};
			my $m = $mem{$info};

			if ((! defined($e)) && (! defined($m))) {
				next;
			}

			foreach my $host (keys %$m) {
				if (! defined($e->{$host})) {
					$plugin->add_message(CRITICAL, "$path: "
						. "$host does not have $info access in /etc/exports");
					next;
				}

				if ($m->{$host} != $e->{$host}) {
					$plugin->add_message(CRITICAL, "$path: "
						. "$host is negated in "
						. ($m->{$host} ? "/etc/exports" : "exportfs info"));
				}
			}

			foreach my $host (keys %$e) {
				if (! defined($m->{$host})) {
					$plugin->add_message(CRITICAL, "$path: "
						. "$host does not have $info access in exportfs info");
				}
			}
		}

		my $e = $export{'sec-flavor'};
		my $m = $mem{'sec-flavor'};

		if (! ((! defined($e)) && (! defined($m)))) {
			$e ||= {};
			$m ||= {};

			foreach my $flavor (keys %$m) {
				if (! defined($e->{$flavor})) {
					$plugin->add_message(CRITICAL, "$path: "
						. "security flavor $flavor is not specified "
						. "in /etc/exports");
				}
			}

			foreach my $flavor (keys %$e) {
				if (! defined($m->{$flavor})) {
					$plugin->add_message(CRITICAL, "$path: "
						. "security flavor $flavor is not specified "
						. "in exportfs info");
				}
			}
		}
	}

	foreach my $path (keys %exports) {
		if (! defined($memory{$path})) {
			$plugin->add_message(CRITICAL,
				"$path not exported (according to 'exportfs')");
		}
	}
}

