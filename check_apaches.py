#!/usr/bin/python

from monitoringplugin import MonitoringPlugin

import re
import urllib2

plugin = MonitoringPlugin(pluginname='check_apaches', tagforstatusline='APACHE', description='Check Apache workers', version='0.1')

plugin.add_cmdlineoption('-H', '', 'host', 'Hostname/IP to check', default='localhost')
plugin.add_cmdlineoption('-p', '', 'port', 'port to connect', default=None)
plugin.add_cmdlineoption('-P', '', 'proto', 'protocol to use', default='http')
plugin.add_cmdlineoption('-u', '', 'url', 'path to "server-status"', default='/server-status')
plugin.add_cmdlineoption('-a', '', 'httpauth', 'HTTP Username and Password, separated by ":"')
plugin.add_cmdlineoption('-w', '', 'warn', 'warning thresold', default='20')
plugin.add_cmdlineoption('-c', '', 'crit', 'warning thresold', default='50')
plugin.add_cmdlineoption('', '--statistics', 'statistics', 'Output worker statistics', action='store_true')

plugin.parse_cmdlineoptions()

if plugin.options.proto not in ['http', 'https']:
	plugin.back2nagios(3, 'Unknown protocol "' + plugin.options.proto + '"')

if not plugin.options.port:
	if plugin.options.proto == 'https':
		plugin.options.port = '443'
	else:
		plugin.options.port = '80'

url = plugin.options.proto + '://' + plugin.options.host + ':' + plugin.options.port + '/' + plugin.options.url + '?auto'
plugin.verbose(1, 'Status URL: ' + url)

if plugin.options.httpauth:
	httpauth = plugin.options.httpauth.split(':')
	if len(httpauth) != 2:
		plugin.back2nagios(3, 'Wrong format of authentication data! Need "USERNAME:PASSWORD", got "' + plugin.options.httpauth + '"')
	passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
	passman.add_password(None, url, httpauth[0], httpauth[1])
	authhandler = urllib2.HTTPBasicAuthHandler(passman)
	opener = urllib2.build_opener(authhandler)
	urllib2.install_opener(opener)

try:
	data = urllib2.urlopen(url).read()
except urllib2.HTTPError, e:
	plugin.back2nagios(2, 'Could not read data! ' + str(e))
except urllib2.URLError, e:
	plugin.back2nagios(2, 'Could not connect to server!')

plugin.verbose(2, 'Got data:\n' + data)

try:
	idle = int(re.search('Idle(?:Workers|Servers): (\d+)\n', data).group(1))
	busy = int(re.search('Busy(?:Workers|Servers): (\d+)\n', data).group(1))
except:
	plugin.back2nagios(2, 'Could not analyze data!')

states = None
if plugin.options.statistics:
	scoreboard = re.search('Scoreboard: (.*)\n', data)
	if scoreboard:
		states = {'_':0, 'S':0, 'R':0, 'W':0, 'K':0, 'D':0, 'C':0, 'L':0, 'G':0, 'I':0, '.':0,}
		for worker in scoreboard.group(1):
			states[worker] += 1
		plugin.add_multilineoutput(str(states['_']) + ' waiting for connection')
		plugin.add_multilineoutput(str(states['S']) + ' starting up')
		plugin.add_multilineoutput(str(states['R']) + ' reading request')
		plugin.add_multilineoutput(str(states['W']) + ' writing/sending reply')
		plugin.add_multilineoutput(str(states['K']) + ' keepalive')
		plugin.add_multilineoutput(str(states['D']) + ' looking up in DNS')
		plugin.add_multilineoutput(str(states['C']) + ' closing connection')
		plugin.add_multilineoutput(str(states['L']) + ' logging')
		plugin.add_multilineoutput(str(states['G']) + ' gracefully finishing')
		plugin.add_multilineoutput(str(states['I']) + ' idle cleanup of worker')
		plugin.add_multilineoutput(str(states['.']) + ' open slots(up to ServerLimit)')

returncode = plugin.value_wc_to_returncode(busy, plugin.options.warn, plugin.options.crit)

plugin.add_output(str(busy) + ' busy workers, ' + str(idle) + ' idle')

plugin.add_returncode(returncode)

plugin.format_add_performancedata('busy', busy, '', warn=plugin.options.warn, crit=plugin.options.crit, min=0.0)
plugin.format_add_performancedata('idle', idle, '')

plugin.exit()

