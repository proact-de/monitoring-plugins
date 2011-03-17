#!/usr/bin/env python
# -*- encoding: utf-8 -*-

#####################################################################
# (c) 2005-2011 by Sven Velt and team(ix) GmbH, Nuernberg, Germany  #
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
import shlex
import subprocess
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


plugin = MonitoringPlugin(pluginname='check_nagiostats', tagforstatusline='NAGIOSTATS', description='Check Nagios statistics', version='0.1')

NAGIOSTATSs = ['/usr/sbin/nagios3stats', '/usr/local/nagios/bin/nagiostats']
VARs = {
	'PROGRUNTIME': { 'type':str, },
	'PROGRUNTIMETT': { 'type':long, 'unit':'', },
	'STATUSFILEAGE': { 'type':str, },
	'STATUSFILEAGETT': { 'type':long, 'unit':'', },
	'NAGIOSVERSION': { 'type':str, },
	'NAGIOSPID': { 'type':str, },
	'NAGIOSVERPID': { 'type':str, },
	'TOTCMDBUF': { 'type':long, 'unit':'', },
	'USEDCMDBUF': { 'type':long, 'unit':'', },
	'HIGHCMDBUF': { 'type':long, 'unit':'', },
	'NUMSERVICES': { 'type':long, 'unit':'', },
	'NUMSVCOK': { 'type':long, 'unit':'', },
	'NUMSVCWARN': { 'type':long, 'unit':'', },
	'NUMSVCUNKN': { 'type':long, 'unit':'', },
	'NUMSVCCRIT': { 'type':long, 'unit':'', },
	'NUMSVCPROB': { 'type':long, 'unit':'', },
	'NUMSVCCHECKED': { 'type':long, 'unit':'', },
	'NUMSVCSCHEDULED': { 'type':long, 'unit':'', },
	'NUMSVCFLAPPING': { 'type':long, 'unit':'', },
	'NUMSVCDOWNTIME': { 'type':long, 'unit':'', },
	'NUMHOSTS': { 'type':long, 'unit':'', },
	'NUMHSTUP': { 'type':long, 'unit':'', },
	'NUMHSTDOWN': { 'type':long, 'unit':'', },
	'NUMHSTUNR': { 'type':long, 'unit':'', },
	'NUMHSTPROB': { 'type':long, 'unit':'', },
	'NUMHSTCHECKED': { 'type':long, 'unit':'', },
	'NUMHSTSCHEDULED': { 'type':long, 'unit':'', },
	'NUMHSTFLAPPING': { 'type':long, 'unit':'', },
	'NUMHSTDOWNTIME': { 'type':long, 'unit':'', },
	'NUMHSTACTCHK1M': { 'type':long, 'unit':'', },
	'NUMHSTPSVCHK1M': { 'type':long, 'unit':'', },
	'NUMSVCACTCHK1M': { 'type':long, 'unit':'', },
	'NUMSVCPSVCHK1M': { 'type':long, 'unit':'', },
	'NUMHSTACTCHK5M': { 'type':long, 'unit':'', },
	'NUMHSTPSVCHK5M': { 'type':long, 'unit':'', },
	'NUMSVCACTCHK5M': { 'type':long, 'unit':'', },
	'NUMSVCPSVCHK5M': { 'type':long, 'unit':'', },
	'NUMHSTACTCHK15M': { 'type':long, 'unit':'', },
	'NUMHSTPSVCHK15M': { 'type':long, 'unit':'', },
	'NUMSVCACTCHK15M': { 'type':long, 'unit':'', },
	'NUMSVCPSVCHK15M': { 'type':long, 'unit':'', },
	'NUMHSTACTCHK60M': { 'type':long, 'unit':'', },
	'NUMHSTPSVCHK60M': { 'type':long, 'unit':'', },
	'NUMSVCACTCHK60M': { 'type':long, 'unit':'', },
	'NUMSVCPSVCHK60M': { 'type':long, 'unit':'', },
	'AVGACTSVCLAT': { 'type':float, 'unit':'s', 'factor':0.001, },
	'AVGACTSVCEXT': { 'type':float, 'unit':'s', 'factor':0.001, },
	'AVGACTSVCPSC': { 'type':float, 'unit':'%', },
	'AVGPSVSVCLAT': { 'type':float, 'unit':'s', 'factor':0.001, },
	'AVGPSVSVCPSC': { 'type':float, 'unit':'%', },
	'AVGSVCPSC': { 'type':float, 'unit':'%', },
	'AVGACTHSTLAT': { 'type':float, 'unit':'s', 'factor':0.001, },
	'AVGACTHSTEXT': { 'type':float, 'unit':'s', 'factor':0.001, },
	'AVGACTHSTPSC': { 'type':float, 'unit':'%', },
	'AVGPSVHSTLAT': { 'type':float, 'unit':'s', 'factor':0.001, },
	'AVGPSVHSTPSC': { 'type':float, 'unit':'%', },
	'AVGHSTPSC': { 'type':float, 'unit':'%', },
	'MINACTSVCLAT': { 'type':float, 'unit':'s', 'factor':0.001, },
	'MINACTSVCEXT': { 'type':float, 'unit':'s', 'factor':0.001, },
	'MINACTSVCPSC': { 'type':float, 'unit':'%', },
	'MINPSVSVCLAT': { 'type':float, 'unit':'s', 'factor':0.001, },
	'MINPSVSVCPSC': { 'type':float, 'unit':'%', },
	'MINSVCPSC': { 'type':float, 'unit':'%', },
	'MINACTHSTLAT': { 'type':float, 'unit':'s', 'factor':0.001, },
	'MINACTHSTEXT': { 'type':float, 'unit':'s', 'factor':0.001, },
	'MINACTHSTPSC': { 'type':float, 'unit':'%', },
	'MINPSVHSTLAT': { 'type':float, 'unit':'s', 'factor':0.001, },
	'MINPSVHSTPSC': { 'type':float, 'unit':'%', },
	'MINHSTPSC': { 'type':float, 'unit':'%', },
	'MAXACTSVCLAT': { 'type':float, 'unit':'s', 'factor':0.001, },
	'MAXACTSVCEXT': { 'type':float, 'unit':'s', 'factor':0.001, },
	'MAXACTSVCPSC': { 'type':float, 'unit':'%', },
	'MAXPSVSVCLAT': { 'type':float, 'unit':'s', 'factor':0.001, },
	'MAXPSVSVCPSC': { 'type':float, 'unit':'%', },
	'MAXSVCPSC': { 'type':float, 'unit':'%', },
	'MAXACTHSTLAT': { 'type':float, 'unit':'s', 'factor':0.001, },
	'MAXACTHSTEXT': { 'type':float, 'unit':'s', 'factor':0.001, },
	'MAXACTHSTPSC': { 'type':float, 'unit':'%', },
	'MAXPSVHSTLAT': { 'type':float, 'unit':'s', 'factor':0.001, },
	'MAXPSVHSTPSC': { 'type':float, 'unit':'%', },
	'MAXHSTPSC': { 'type':float, 'unit':'%', },
	'NUMACTHSTCHECKS1M': { 'type':long, 'unit':'', },
	'NUMOACTHSTCHECKS1M': { 'type':long, 'unit':'', },
	'NUMCACHEDHSTCHECKS1M': { 'type':long, 'unit':'', },
	'NUMSACTHSTCHECKS1M': { 'type':long, 'unit':'', },
	'NUMPARHSTCHECKS1M': { 'type':long, 'unit':'', },
	'NUMSERHSTCHECKS1M': { 'type':long, 'unit':'', },
	'NUMPSVHSTCHECKS1M': { 'type':long, 'unit':'', },
	'NUMACTSVCCHECKS1M': { 'type':long, 'unit':'', },
	'NUMOACTSVCCHECKS1M': { 'type':long, 'unit':'', },
	'NUMCACHEDSVCCHECKS1M': { 'type':long, 'unit':'', },
	'NUMSACTSVCCHECKS1M': { 'type':long, 'unit':'', },
	'NUMPSVSVCCHECKS1M': { 'type':long, 'unit':'', },
	'NUMEXTCMDS1M': { 'type':long, 'unit':'', },
	'NUMACTHSTCHECKS5M': { 'type':long, 'unit':'', },
	'NUMOACTHSTCHECKS5M': { 'type':long, 'unit':'', },
	'NUMCACHEDHSTCHECKS5M': { 'type':long, 'unit':'', },
	'NUMSACTHSTCHECKS5M': { 'type':long, 'unit':'', },
	'NUMPARHSTCHECKS5M': { 'type':long, 'unit':'', },
	'NUMSERHSTCHECKS5M': { 'type':long, 'unit':'', },
	'NUMPSVHSTCHECKS5M': { 'type':long, 'unit':'', },
	'NUMACTSVCCHECKS5M': { 'type':long, 'unit':'', },
	'NUMOACTSVCCHECKS5M': { 'type':long, 'unit':'', },
	'NUMCACHEDSVCCHECKS5M': { 'type':long, 'unit':'', },
	'NUMSACTSVCCHECKS5M': { 'type':long, 'unit':'', },
	'NUMPSVSVCCHECKS5M': { 'type':long, 'unit':'', },
	'NUMEXTCMDS5M': { 'type':long, 'unit':'', },
	'NUMACTHSTCHECKS15M': { 'type':long, 'unit':'', },
	'NUMOACTHSTCHECKS15M': { 'type':long, 'unit':'', },
	'NUMCACHEDHSTCHECKS15M': { 'type':long, 'unit':'', },
	'NUMSACTHSTCHECKS15M': { 'type':long, 'unit':'', },
	'NUMPARHSTCHECKS15M': { 'type':long, 'unit':'', },
	'NUMSERHSTCHECKS15M': { 'type':long, 'unit':'', },
	'NUMPSVHSTCHECKS15M': { 'type':long, 'unit':'', },
	'NUMACTSVCCHECKS15M': { 'type':long, 'unit':'', },
	'NUMOACTSVCCHECKS15M': { 'type':long, 'unit':'', },
	'NUMCACHEDSVCCHECKS15M': { 'type':long, 'unit':'', },
	'NUMSACTSVCCHECKS15M': { 'type':long, 'unit':'', },
	'NUMPSVSVCCHECKS15M': { 'type':long, 'unit':'', },
	'NUMEXTCMDS15M': { 'type':long, 'unit':'', },
	}

plugin.add_cmdlineoption('-C', '', 'checks', 'Use built-in checks (predefined lists of variables)', default='')
plugin.add_cmdlineoption('-V', '', 'vars', 'List of "nagiostats" variables to check', default='')
plugin.add_cmdlineoption('-n', '', 'nagiostats', 'Full path to nagiostat', default='')
plugin.add_cmdlineoption('-w', '', 'warn', 'warning thresold', default='')
plugin.add_cmdlineoption('-c', '', 'crit', 'warning thresold', default='')

plugin.parse_cmdlineoptions()


if not plugin.options.nagiostats:
	plugin.verbose(2, 'Auto-detecting path to "nagiostats"...')
	for nagiostats in NAGIOSTATSs:
		if os.path.exists(nagiostats):
			plugin.options.nagiostats = nagiostats
			plugin.verbose(2, 'Found it at "%s"' % nagiostats)
			break

if not os.path.exists(plugin.options.nagiostats):
	plugin.back2nagios(3, 'Could not find "nagiostats"')

if not plugin.options.checks and not plugin.options.vars:
	plugin.back2nagios(3, 'Need either "-C" or "-V"')

# FIXME: Built var list out of -C

if ',' in plugin.options.vars:
	plugin.verbose(2, 'Multiple variables detected')
	plugin.options.vars = plugin.options.vars.split(',')
else:
	plugin.verbose(2, 'Single variable detected')
	plugin.options.vars = [plugin.options.vars, ]

for var in plugin.options.vars:
	plugin.verbose(3, 'See if "%s" is a valid variable' % var)
	if var not in VARs:
		plugin.back2nagios(3, 'Unknown variable "%s"' % var)

if ',' in plugin.options.warn:
	plugin.verbose(2, 'Multiple warning thresolds detected')
	plugin.options.warn = plugin.options.warn.split(',')
else:
	plugin.verbose(2, 'Single warning thresold detected - use for all variables')
	plugin.options.warn = [plugin.options.warn, ] * len(plugin.options.vars)

if ',' in plugin.options.crit:
	plugin.verbose(2, 'Multiple critical thresolds detected')
	plugin.options.crit = plugin.options.crit.split(',')
else:
	plugin.verbose(2, 'Single critical thresold detected - use for all variables')
	plugin.options.crit = [plugin.options.crit, ] * len(plugin.options.vars)


plugin.verbose(3, 'Length of vars:  %s' % len(plugin.options.vars) )
plugin.verbose(3, 'Length of warns: %s' % len(plugin.options.warn) )
plugin.verbose(3, 'Length of crits: %s' % len(plugin.options.crit) )
if not ( len(plugin.options.vars) == len(plugin.options.warn) == len(plugin.options.crit) ):
	plugin.back2nagios(3, 'Different length of -V, -w and -c')


# Go!
cmdline = '%s -m -d %s' % (plugin.options.nagiostats, ','.join(plugin.options.vars))
plugin.verbose(1, 'Using command line: %s' % cmdline)
cmdline = shlex.split(cmdline)
try:
	cmd = subprocess.Popen(cmdline, stdout=subprocess.PIPE)
	outputs = cmd.communicate()[0].rstrip().split('\n')
	retcode = cmd.returncode
except OSError:
	plugin.back2nagios(3, 'Could not execute "%s"' % cmdline)

plugin.verbose(3, 'Returncode of "nagiostats": %s' % retcode)
if retcode == 254:
	plugin.back2nagios(2, 'Could not read "status.dat"')
elif retcode != 0:
	plugin.back2nagios(3, 'Unknown return code "%s" - please send output of "-vvv" command line to author!' % retcode)

plugin.verbose(1, 'Asked for variable(s): %s' % ' '.join(plugin.options.vars) )
plugin.verbose(1, 'Got response(s): %s' % ' '.join(outputs) )

plugin.verbose(3, 'Length of vars:    %s' % len(outputs) )
plugin.verbose(3, 'Length of output:  %s' % len(plugin.options.vars) )
if len(outputs) != len(plugin.options.vars):
	plugin.back2nagios(3, 'Did not get expected infos')

for idx in xrange(0, len(plugin.options.vars)):
	var = plugin.options.vars[idx]
	warn = plugin.options.warn[idx]
	crit = plugin.options.crit[idx]
	output = (VARs[var]['type'])(outputs[idx])

	if VARs[var]['type'] in [float, long, int]:
		factor = VARs[var].get('factor')
		if factor != None:
			output = output * factor

		returncode = plugin.value_wc_to_returncode(output, warn, crit)
	else:
		returncode = plugin.RETURNCODE['OK']

	perfdata = []
	if VARs[var].get('unit') != None:
		perfdata.append({'label':var, 'value':output, 'unit':VARs[var]['unit'], 'warn':warn, 'crit':crit,})
	plugin.remember_check(var, returncode, str(output), perfdata=perfdata)

plugin.brain2output()
plugin.exit()

