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
	'AVGACTSVCLAT': { 'type':float, 'unit':'s', 'factor':0.001, 'descr':'Average active service check latency', },
	'AVGACTSVCEXT': { 'type':float, 'unit':'s', 'factor':0.001, 'descr':'Average active service check execution time', },
	'AVGACTSVCPSC': { 'type':float, 'unit':'%', },
	'AVGPSVSVCLAT': { 'type':float, 'unit':'s', 'factor':0.001, 'descr':'Average passive service check latency', },
	'AVGPSVSVCPSC': { 'type':float, 'unit':'%', },
	'AVGSVCPSC': { 'type':float, 'unit':'%', },
	'AVGACTHSTLAT': { 'type':float, 'unit':'s', 'factor':0.001, 'descr':'Average active host check latency', },
	'AVGACTHSTEXT': { 'type':float, 'unit':'s', 'factor':0.001, 'descr':'Average active host check execution time', },
	'AVGACTHSTPSC': { 'type':float, 'unit':'%', },
	'AVGPSVHSTLAT': { 'type':float, 'unit':'s', 'factor':0.001, 'descr':'Average passive host check latency', },
	'AVGPSVHSTPSC': { 'type':float, 'unit':'%', },
	'AVGHSTPSC': { 'type':float, 'unit':'%', },
	'MINACTSVCLAT': { 'type':float, 'unit':'s', 'factor':0.001, 'descr':'Minimum active service check latency', },
	'MINACTSVCEXT': { 'type':float, 'unit':'s', 'factor':0.001, 'descr':'Minimum active service check execution time', },
	'MINACTSVCPSC': { 'type':float, 'unit':'%', },
	'MINPSVSVCLAT': { 'type':float, 'unit':'s', 'factor':0.001, 'descr':'Minimum passive service check latency', },
	'MINPSVSVCPSC': { 'type':float, 'unit':'%', },
	'MINSVCPSC': { 'type':float, 'unit':'%', },
	'MINACTHSTLAT': { 'type':float, 'unit':'s', 'factor':0.001, 'descr':'Minimum active host check latency', },
	'MINACTHSTEXT': { 'type':float, 'unit':'s', 'factor':0.001, 'descr':'Minimum active host check execution time', },
	'MINACTHSTPSC': { 'type':float, 'unit':'%', },
	'MINPSVHSTLAT': { 'type':float, 'unit':'s', 'factor':0.001, 'descr':'Minimum passive host check latency', },
	'MINPSVHSTPSC': { 'type':float, 'unit':'%', },
	'MINHSTPSC': { 'type':float, 'unit':'%', },
	'MAXACTSVCLAT': { 'type':float, 'unit':'s', 'factor':0.001, 'descr':'Maximum active service check latency', },
	'MAXACTSVCEXT': { 'type':float, 'unit':'s', 'factor':0.001, 'descr':'Maximum active service check execution time', },
	'MAXACTSVCPSC': { 'type':float, 'unit':'%', },
	'MAXPSVSVCLAT': { 'type':float, 'unit':'s', 'factor':0.001, 'descr':'Maximum passive service check latency', },
	'MAXPSVSVCPSC': { 'type':float, 'unit':'%', },
	'MAXSVCPSC': { 'type':float, 'unit':'%', },
	'MAXACTHSTLAT': { 'type':float, 'unit':'s', 'factor':0.001, 'descr':'Maximum active host check latency', },
	'MAXACTHSTEXT': { 'type':float, 'unit':'s', 'factor':0.001, 'descr':'Maximum active host check execution time', },
	'MAXACTHSTPSC': { 'type':float, 'unit':'%', },
	'MAXPSVHSTLAT': { 'type':float, 'unit':'s', 'factor':0.001, 'descr':'Maximum passive host check latency', },
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

CHECKs = {
	'AVGACTLATENCY': ['AVGACTSVCLAT', 'AVGACTHSTLAT', ],
	'MAXACTLATENCY': ['MAXACTSVCLAT', 'MAXACTHSTLAT', ],
	'MINACTLATENCY': ['MINACTSVCLAT', 'MINACTHSTLAT', ],
	'AVGPSVLATENCY': ['AVGPSVSVCLAT', 'AVGPSVHSTLAT', ],
	'MAXPSVLATENCY': ['MAXPSVSVCLAT', 'MAXPSVHSTLAT', ],
	'MINPSVLATENCY': ['MINPSVSVCLAT', 'MINPSVHSTLAT', ],
	'AVGLATENCY': ['AVGACTSVCLAT', 'AVGACTHSTLAT', 'AVGPSVSVCLAT', 'AVGPSVHSTLAT', ],
	'MAXLATENCY': ['MAXACTSVCLAT', 'MAXACTHSTLAT', 'MAXPSVSVCLAT', 'MAXPSVHSTLAT',],
	'MINLATENCY': ['MINACTSVCLAT', 'MINACTHSTLAT', 'MINPSVSVCLAT', 'MINPSVHSTLAT',],
	'AVGEXECTIME': ['AVGACTSVCEXT', 'AVGACTHSTEXT', ],
	'MAXEXECTIME': ['MAXACTSVCEXT', 'MAXACTHSTEXT', ],
	'MINEXECTIME': ['MINACTSVCEXT', 'MINACTHSTEXT', ],
	'PERFORMANCE': ['AVGACTSVCLAT', 'AVGPSVSVCLAT', 'AVGACTSVCEXT', 'AVGACTHSTLAT', 'AVGPSVHSTLAT', 'AVGACTHSTEXT', ],
	'PEAK': [ 'MAXACTSVCLAT', 'MAXPSVSVCLAT', 'MAXACTSVCEXT', 'MAXACTHSTLAT', 'MAXPSVHSTLAT', 'MAXACTHSTEXT', ],
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

# Checks and Variables
varlist = []
varlist_unknown = []

# Built var list out of -C
if plugin.options.checks:
	for check in plugin.options.checks.split(','):
		if check not in CHECKs:
			plugin.back2nagios(3, 'Unknown check "%s"' % check)
		varlist.extend(CHECKs[check])

# Check for unknown vars and build list
for var in plugin.options.vars.split(','):
	if var:
		plugin.verbose(3, 'See if "%s" is a valid variable' % var)
		if var in VARs:
			varlist.append(var)
		else:
			varlist_unknown.append(var)

# See if there are unknown vars:
if varlist_unknown:
	plugin.back2nagios(3, 'Unknown variable(s): %s' % ', '.join(varlist_unknown))

# Thresholds
if ',' in plugin.options.warn:
	plugin.verbose(2, 'Multiple warning thresolds detected')
	plugin.options.warn = plugin.options.warn.split(',')
else:
	plugin.verbose(2, 'Single warning thresold detected - use for all variables')
	plugin.options.warn = [plugin.options.warn, ] * len(varlist)

if ',' in plugin.options.crit:
	plugin.verbose(2, 'Multiple critical thresolds detected')
	plugin.options.crit = plugin.options.crit.split(',')
else:
	plugin.verbose(2, 'Single critical thresold detected - use for all variables')
	plugin.options.crit = [plugin.options.crit, ] * len(varlist)


plugin.verbose(3, 'Length of vars:  %s' % len(varlist) )
plugin.verbose(3, 'Length of warns: %s' % len(plugin.options.warn) )
plugin.verbose(3, 'Length of crits: %s' % len(plugin.options.crit) )
if not ( len(varlist) == len(plugin.options.warn) == len(plugin.options.crit) ):
	plugin.back2nagios(3, 'Different length of -V, -w and -c')


# Go!
cmdline = '%s -m -d %s' % (plugin.options.nagiostats, ','.join(varlist))
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

plugin.verbose(1, 'Asked for variable(s): %s' % ' '.join(varlist) )
plugin.verbose(1, 'Got response(s): %s' % ' '.join(outputs) )

plugin.verbose(3, 'Length of vars:    %s' % len(outputs) )
plugin.verbose(3, 'Length of output:  %s' % len(varlist) )
if len(outputs) != len(varlist):
	plugin.back2nagios(3, 'Did not get expected infos')

for idx in xrange(0, len(varlist)):
	var = varlist[idx]
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
	unit = VARs[var].get('unit')
	if unit != None:
		perfdata.append({'label':var, 'value':output, 'unit':VARs[var]['unit'], 'warn':warn, 'crit':crit,})
	else:
		unit = ''

	descr = VARs[var].get('descr')
	if  descr != None:
		longoutput = descr + ': ' + str(output) + unit
	else:
		longoutput = str(output) + unit

	plugin.remember_check(var, returncode, longoutput, perfdata=perfdata)

plugin.brain2output()
plugin.exit()

