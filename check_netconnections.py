#!/usr/bin/python

from monitoringplugin import MonitoringPlugin

import re

plugin = MonitoringPlugin(pluginname='check_netconnections', tagforstatusline='NETCONNS', description='Count network connections', version='0.1')

plugin.add_cmdlineoption('-p', '', 'port', 'port number', default=None)
plugin.add_cmdlineoption('-t', '--tcp', 'tcp', 'count TCP connections (default)', action='store_true')
plugin.add_cmdlineoption('-u', '--udp', 'udp', 'count TCP connections', action='store_true')
plugin.add_cmdlineoption('-4', '', 'v4', 'count IPv4 connections (default)', action='store_true')
plugin.add_cmdlineoption('-6', '', 'v6', 'count IPv6 connections', action='store_true')
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
plugin.format_add_performancedata('netconnections', count, '', warn=plugin.options.warn, crit=plugin.options.crit)

plugin.exit()

