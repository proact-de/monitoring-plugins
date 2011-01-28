#!/usr/bin/python
# -*- encoding: utf-8 -*-

from monitoringplugin import MonitoringPlugin

import datetime
import time
import os
import re

plugin = MonitoringPlugin(pluginname='check_tl500', tagforstatusline='TL500', description='Check TL500 environment sensors', version='0.1')

plugin.add_cmdlineoption('-s', '', 'sensorid', '(comma separated list of) sensor id(s), no spaces', default=None)
plugin.add_cmdlineoption('-m', '', 'maxage', 'maximum age of data files (default: 600 seconds/10 minutes)', type="int", default=600)
plugin.add_cmdlineoption('-p', '', 'path', 'path to data files', default='/tmp')
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

# Convert all sensor ids to long
for idx in xrange(len(plugin.options.sensorid)):
	try:
		plugin.options.sensorid[idx] = long(plugin.options.sensorid[idx])
	except ValueError:
		plugin.back2nagios(3, 'Sensor id "%s" must be numeric!' % plugin.options.sensorid[idx])

plugin.options.sensorid.sort()
plugin.verbose(1, 'Sensor id(s): ' + ' - '.join([str(s) for s in plugin.options.sensorid]))

searchpattern = re.compile(r'Sensor:\s*([0-9A-Za-z]+)\s+Raw:\s*(-?[0-9\.]+)?\s+Value:\s*(-?[0-9\.]+)\s+Unit:\s*(\S+)$')

for sensorid in plugin.options.sensorid:
	filename = os.path.join(plugin.options.path, 'tl-500_%s' % sensorid)
	try:
		plugin.verbose(3, 'Reading sensor %s' % sensorid)
		data = file(filename).read().lstrip().rstrip()
	except IOError:
		plugin.back2nagios(3, 'Could not read file "%s"' % filename)

	plugin.verbose(2, 'Read line: %s' % data)

	plugin.verbose(2, 'Checking age of file')
	readtime = os.path.getmtime(filename)
	fileage = time.time() - readtime
	if fileage > plugin.options.maxage:
		plugin.add_output('Data of sensor "%s" to old' % sensorid)
		plugin.add_returncode(3)
		plugin.verbose(2, 'File to old, age: %s but only %s seconds allowed'% (long(fileage), plugin.options.maxage))
	else:
		plugin.verbose(2, 'File age OK, age: %s and %s seconds are allowed'% (long(fileage), plugin.options.maxage))
	
		result = searchpattern.search(data)
		if result:
			sensor_type = None
			(sid, raw, value, unit) = result.groups()

			readtime = datetime.datetime.fromtimestamp(long(readtime))
			readtime = readtime.isoformat(' ')

			if unit == '\xc2\xb0C':
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
		else:
			plugin.verbose(2, 'No data found for sensor %s' % sensorid)

plugin.exit()

