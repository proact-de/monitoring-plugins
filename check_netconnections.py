#!/usr/bin/env python
# -*- encoding: utf-8 -*-

#####################################################################
# (c) 2010-2011 by Sven Velt and team(ix) GmbH, Nuernberg, Germany  #
#                  sv@teamix.net                                    #
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

import os
import re
import sys

try:
	from monitoringplugin import MonitoringPlugin
except ImportError:
	print '=========================='
	print 'AIKS! Python import error!'
	print '==========================\n'
	print 'Could not find "monitoringplugin.py"!\n'
	print 'Did you download "%s"' % os.path.basename(sys.argv[0])
	print 'without "monitoringplugin.py"?\n'
	print 'Please go back to'
	print 'http://oss.teamix.org/projects/monitoringplugins/ and download it,'
	print 'or even better:'
	print 'get a hole archive at http://oss.teamix.org/projects/monitoringplugins/files\n'
	sys.exit(127)


plugin = MonitoringPlugin(pluginname='check_netconnections', tagforstatusline='NETCONNS', description='Count network connections', version='0.1')

plugin.add_cmdlineoption('-p', '', 'port', 'port number', default=None)
plugin.add_cmdlineoption('-t', '--tcp', 'tcp', 'count TCP connections (default)', action='store_true')
plugin.add_cmdlineoption('-u', '--udp', 'udp', 'count TCP connections', action='store_true')
plugin.add_cmdlineoption('-4', '', 'v4', 'count IPv4 connections (default)', action='store_true')
plugin.add_cmdlineoption('-6', '', 'v6', 'count IPv6 connections (default)', action='store_true')
plugin.add_cmdlineoption('-w', '', 'warn', 'warning thresold', default='20')
plugin.add_cmdlineoption('-c', '', 'crit', 'warning thresold', default='50')

plugin.parse_cmdlineoptions()

# Need a port number
if not plugin.options.port:
	plugin.back2nagios(3, 'No port number specified!')
else:
	plugin.options.port = int(plugin.options.port)


# Settings defaults
if not plugin.options.udp and not plugin.options.tcp:
	plugin.options.tcp = True

if not plugin.options.v4 and not plugin.options.v6:
	plugin.options.v4 = True
	plugin.options.v6 = True


# RegExp
v4match = re.compile('^\s*\d*:\s*([0-9A-Fa-f]{8}):([0-9A-Fa-f]{4})\s+([0-9A-Fa-f]{8}):([0-9A-Fa-f]{4})')
v6match = re.compile('^\s*\d*:\s*([0-9A-Fa-f]{32}):([0-9A-Fa-f]{4})\s+([0-9A-Fa-f]{32}):([0-9A-Fa-f]{4})')


# Prepare
count = 0
protos = []
versions = []

if plugin.options.tcp:
	protos.append('tcp')
if plugin.options.udp:
	protos.append('udp')
if plugin.options.v4:
	versions.append('')
if plugin.options.v6:
	versions.append('6')


# Go!
for version in versions:

	if version == '6':
		matcher = v6match
	else:
		matcher = v4match

	for proto in protos:
		filename = '/proc/net/%s%s' % (proto, version)
		f = file(filename)
		lines = f.readlines()

		for line in lines:
			m = matcher.match(line)
			if m:
				port = int(m.group(2), 16)
				if port == plugin.options.port and m.group(3) not in ['00000000','00000000000000000000000000000000']:
					count += 1


returncode = plugin.value_wc_to_returncode(count, plugin.options.warn, plugin.options.crit)
plugin.add_returncode(returncode)

plugin.add_output('%s network connections on port %s' % (count, plugin.options.port))
plugin.format_add_performancedata('netconns_%s' % plugin.options.port, count, '', warn=plugin.options.warn, crit=plugin.options.crit)

plugin.exit()

