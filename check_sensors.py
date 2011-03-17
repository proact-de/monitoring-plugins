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

import datetime
import time
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


plugin = MonitoringPlugin(pluginname='check_sensors', tagforstatusline='Sensors', description='Check environment sensors', version='0.2')

plugin.add_cmdlineoption('-s', '', 'sensorid', '(comma separated list of) sensor id(s), no spaces', default=None)
plugin.add_cmdlineoption('-m', '', 'maxage', 'maximum age of data files (default: 600 seconds/10 minutes)', type="int", default=600)
plugin.add_cmdlineoption('-p', '', 'path', 'path to data files', default='/tmp')
plugin.add_cmdlineoption('-b', '', 'basefilename', 'base of sensor file name', default='sensor_')
plugin.add_cmdlineoption('-w', '', 'tempwarn', 'warning thresold for temperature sensors', default=None)
plugin.add_cmdlineoption('-c', '', 'tempcrit', 'critical thresold for temperature sensors', default=None)
plugin.add_cmdlineoption('-W', '', 'humwarn', 'warning thresold for humidity sensors', default=None)
plugin.add_cmdlineoption('-C', '', 'humcrit', 'critical thresold for humidity sensors', default=None)

plugin.parse_cmdlineoptions()

# No sensor id
if not plugin.options.sensorid:
	plugin.back2nagios(3, 'Need at least one sensor id!')

# Make list of sensor ids
if ',' in plugin.options.sensorid:
	plugin.options.sensorid = plugin.options.sensorid.split(',')
else:
	plugin.options.sensorid = [plugin.options.sensorid,]

# Check all sensor ids are hex
re_hex = re.compile('^[0-9A-Fa-f]+$')
for sid in plugin.options.sensorid:
	if not re_hex.search(sid):
		plugin.back2nagios(3, 'Sensor id "%s" must be integer or hex!' % sid)

plugin.verbose(1, 'Sensor id(s): ' + ' - '.join([str(s) for s in plugin.options.sensorid]))

searchpattern = re.compile(r'(\d+)\s+Sensor:\s*([0-9A-Za-z]+)\s+Raw:\s*(-?[0-9\.]+)?\s+Value:\s*(-?[0-9\.]+)\s+Unit:\s*(\S+)\b')

for sensorid in plugin.options.sensorid:
	filename = os.path.join(plugin.options.path, '%s%s' % (plugin.options.basefilename, sensorid))
	try:
		plugin.verbose(2, 'Reading sensor %s' % sensorid)
		data = file(filename).readlines()
	except IOError:
		plugin.back2nagios(3, 'Could not read file "%s"' % filename)

	if plugin.options.verbose >= 3:
		plugin.verbose(3, 'Read line(s):' % data)
		for line in data:
			plugin.verbose(3, '--> ' + line.lstrip().rstrip())

	plugin.verbose(2, 'Checking age of file')
	fileage = time.time() - os.path.getmtime(filename)
	if fileage > plugin.options.maxage:
		plugin.add_output('Data of sensor "%s" to old' % sensorid)
		plugin.add_returncode(3)
		plugin.verbose(2, 'File to old, age: %s but only %s seconds allowed'% (long(fileage), plugin.options.maxage))
	else:
		plugin.verbose(2, 'File age OK, age: %s and %s seconds are allowed'% (long(fileage), plugin.options.maxage))
	
		valuesinfile = 0

		for line in data:
			result = searchpattern.search(line)
			if result:
				sensor_type = None
				(readtime, sid, raw, value, unit) = result.groups()
	
				readtime = datetime.datetime.fromtimestamp(long(readtime))
				readtime = readtime.isoformat(' ')
	
				if unit in ['degC', '\xc2\xb0C']:
					sensor_type = 'temp'
					sensor_name = 'temp_' + str(sensorid)
					warn = plugin.options.tempwarn
					crit = plugin.options.tempcrit
					unit = 'C'
					pdunit = ''
				elif unit == '%RH':
					sensor_type = 'hum'
					sensor_name = 'hum_' + str(sensorid)
					warn = plugin.options.humwarn
					crit = plugin.options.humcrit
					pdunit = '%'
	
				if sensor_type:
					valuesinfile += 1
					returncode = plugin.value_wc_to_returncode(float(value), warn, crit)
					if returncode == 0:
						plugin.add_output('%s: %s%s' % (sensor_name, value, unit))
					else:
						plugin.add_output('%s: %s %s%s' % (sensor_name, plugin.RETURNSTRINGS[returncode], value, unit))
					plugin.add_returncode(returncode)
					plugin.add_multilineoutput('%s %s: %s%s (%s)' % (sensor_name, plugin.RETURNSTRINGS[returncode], value, unit, readtime))
					plugin.format_add_performancedata(sensor_name, value, pdunit, warn=warn, crit=crit)
				else:
					plugin.verbose(1, 'Unknown sensor type "%s" on %s' % (unit, sensorid))

		if valuesinfile == 0:
			plugin.verbose(2, 'No data found for sensor %s' % sensorid)

plugin.exit()

