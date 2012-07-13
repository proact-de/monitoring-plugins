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

__version__ = '0.0.110715'
__all__ = ['MonitoringPlugin', 'SNMPMonitoringPlugin']

import datetime, optparse, os, re, sys

try:
	import netsnmp
except ImportError:
	pass

class MonitoringPlugin(object):

	RETURNSTRINGS = { 0: "OK", 1: "WARNING", 2: "CRITICAL", 3: "UNKNOWN", 127: "UNKNOWN" }
	RETURNCODE = { 'OK': 0, 'WARNING': 1, 'CRITICAL': 2, 'UNKNOWN': 3 }

	returncode_priority = [2, 1, 3, 0]

	powers_binary = ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']
	powers_binary_lower = [ p.lower() for p in powers_binary]
	powers_si = ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z']
	powers_si_lower = [ p.lower() for p in powers_si]


	def __init__(self, *args, **kwargs):
		self.__pluginname = kwargs.get('pluginname') or ''
		self.__version = kwargs.get('version') or None
		self.__tagforstatusline = kwargs.get('tagforstatusline') or ''
		self.__tagforstatusline = self.__tagforstatusline.replace('|', ' ')
		self.__description = kwargs.get('description') or None

		self.__output = []
		self.__multilineoutput = []
		self.__performancedata = []
		self.__returncode = []

		self.__brain_checks = []
		self.__brain_perfdata = []
		self.__brain_perfdatalabels = []

		self.__optparser = optparse.OptionParser(version=self.__version, description=self.__description)
		self._cmdlineoptions_parsed = False


	def add_cmdlineoption(self, shortoption, longoption, dest, help, **kwargs):
		self.__optparser.add_option(shortoption, longoption, dest=dest, help=help, **kwargs)


	def parse_cmdlineoptions(self):
		if self._cmdlineoptions_parsed:
			return
#		self.__optparser.add_option('-V', '--version', action='version', help='show version number and exit')
		self.__optparser.add_option('-v', '--verbose', dest='verbose',  help='Verbosity, more for more ;-)', action='count')

		(self.options, self.args) = self.__optparser.parse_args()
		self._cmdlineoptions_parsed = True


	def range_to_limits(self, range):
		# Check if we must negate result
		if len(range) > 0 and range[0] == '@':
			negate = True
			range = range[1:]
		else:
			negate = False

		# Look for a ':'...
		if range.find(':') >= 0:
			# ... this is a range
			(low, high) = range.split(':')

			if not low:
				low = float(0.0)
			elif low[0] == '~':
				low = float('-infinity')
			else:
				low = float(low)

			if high:
				high = float(high)
			else:
				high = float('infinity')

		elif len(range) == 0:
			low = float('-infinity')
			high = float('infinity')

		else:
			# ... this is just a number
			low = float(0.0)
			high = float(range)

		return (low, high, negate)


	def value_in_range(self, value, range):
		if range not in ['', None]:
			(low, high, negate) = self.range_to_limits(range)
		else:
			return True

		if value < low or value > high:
			result = False
		else:
			result = True

		if negate:
			result = not result

		return result


	def value_wc_to_returncode(self, value, range_warn, range_crit):
		if not self.value_in_range(value, range_crit):
			return 2
		elif not self.value_in_range(value, range_warn):
			return 1

		return 0


	def is_float(self, string):
		try:
			float(string)
			return True
		except ValueError:
			return False


	def special_value_wc_to_returncode(self, value, warn, crit):
		# Special add on: WARN > CRIT
		if self.is_float(warn) and self.is_float(crit) and float(warn) > float(crit):
			# Test if value is *smaller* than thresholds
			warn = '@0:' + warn
			crit = '@0:' + crit

		return self.value_wc_to_returncode(value, warn, crit)


	def add_output(self, value):
		self.__output.append(value)


	def add_multilineoutput(self, value):
		self.__multilineoutput.append(value)


	def format_performancedata(self, label, value, unit, *args, **kwargs):
		label = label.lstrip().rstrip()
		if re.search('[=\' ]', label):
			label = '\'' + label + '\''
		perfdata = label + '=' + str(value)
		if unit:
			perfdata += str(unit).lstrip().rstrip()
		for key in ['warn', 'crit', 'min', 'max']:
			perfdata += ';'
			if key in kwargs and kwargs[key]!=None:
				perfdata += str(kwargs[key])

		return perfdata


	def add_performancedata(self, perfdata):
		self.__performancedata.append(perfdata)


	def format_add_performancedata(self, label, value, unit, *args, **kwargs):
		self.add_performancedata(self.format_performancedata(label, value, unit, *args, **kwargs))


	def add_returncode(self, value):
		self.__returncode.append(value)


	def tagtarget(self, tag, target):
		if target:
			return str(tag) + ':' + str(target)
		else:
			return str(tag)


	def remember_check(self, tag, returncode, output, multilineoutput=None, perfdata=None, target=None):
		check = {}
		check['tag'] = tag
		check['returncode'] = returncode
		check['output'] = output
		check['multilineoutout'] = multilineoutput
		check['perfdata'] = perfdata
		check['target'] = target
		
		self.remember_perfdata(perfdata)
		
		self.__brain_checks.append(check)
		
		return check


	def remember_perfdata(self, perfdata=None):
		if perfdata:
			for pd in perfdata:
				if pd['label'] in self.__brain_perfdatalabels:
					pdidx = self.__brain_perfdatalabels.index(pd['label'])
					self.__brain_perfdata[pdidx] = pd
				else:
					self.__brain_perfdata.append(pd)
					self.__brain_perfdatalabels.append(pd['label'])


	def dump_brain(self):
		return (self.__brain_checks, self.__brain_perfdata)


	def brain2output(self):
		if len(self.__brain_checks) == 1:
			check = self.__brain_checks[0]
			self.add_output(check.get('output'))
			if check.get('multilineoutput'):
				self.add_multilineoutput(check.get('multilineoutput'))
			self.add_returncode(check.get('returncode') or 0)

		else:
			out = [[], [], [], []]
			for check in self.__brain_checks:
				tagtarget = self.tagtarget(check['tag'], check.get('target'))
				returncode = check.get('returncode') or 0
				self.add_returncode(returncode)

				out[returncode].append(tagtarget)

				self.add_multilineoutput(self.RETURNSTRINGS[returncode] + ' ' + tagtarget + ' - ' + check.get('output'))
				if check.get('multilineoutput'):
					self.add_multilineoutput(check.get('multilineoutput'))

			statusline = []
			for retcode in self.returncode_priority:
				if len(out[retcode]):
					statusline.append(str(len(out[retcode])) + ' ' + self.RETURNSTRINGS[retcode] + ': ' + ' '.join(out[retcode]))
			statusline = ', '.join(statusline)
			self.add_output(statusline)

		for pd in self.__brain_perfdata:
			self.format_add_performancedata(**pd)


	def value_to_human_binary(self, value, unit=''):
		for power in self.powers_binary:
			if value < 1024.0:
				return "%3.1f%s%s" % (value, power, unit)
			value /= 1024.0
		if float(value) not in [float('inf'), float('-inf')]:
			return "%3.1fYi%s" % (value, unit)
		else:
			return value


	def value_to_human_si(self, value, unit=''):
		for power in self.powers_si:
			if value < 1000.0:
				return "%3.1f%s%s" % (value, power, unit)
			value /= 1000.0
		if float(value) not in [float('inf'), float('-inf')]:
			return "%3.1fY%s" % (value, unit)
		else:
			return value


	def seconds_to_hms(self, seconds):
		seconds = int(seconds)
		hours = int(seconds / 3600)
		seconds -= (hours * 3600)
		minutes = seconds / 60
		seconds -= (minutes * 60)
		return '%i:%02i:%02i' % (hours, minutes, seconds)


	def seconds_to_timedelta(self, seconds):
		return datetime.timedelta(seconds=long(seconds))


	def human_to_number(self, value, total=None, unit=['',]):
		if total:
			if not self.is_float(total):
				total = self.human_to_number(total, unit=unit)

		if type(unit) == list:
			unit = [u.lower() for u in unit]
		elif type(unit) == str:
			unit = [unit.lower(),]
		else:
			unit = ['',]

		if value.lower()[-1] in unit:
			value = value[0:-1]

		if self.is_float(value):
			return float(value)
		elif value[-1] == '%':
			if total:
				return float(value[:-1])/100.0 * float(total)
			else:
				if total in [0, 0.0]:
					return 0.0
				else:
					return float(value[:-1]) # FIXME: Good idea?
		elif value[-1].lower() in self.powers_si_lower:
			return 1000.0 ** self.powers_si_lower.index(value[-1].lower()) * float(value[:-1])
		elif value[-2:].lower() in self.powers_binary_lower:
			return 1024.0 ** self.powers_binary_lower.index(value[-2:].lower()) * float(value[:-2])
		else:
			return value


	def range_dehumanize(self, range, total=None, unit=['',]):
		newrange = ''

		if len(range):
			if range[0] == '@':
				newrange += '@'
				range = range[1:]

			parts = range.split(':')
			newrange += ('%s' % self.human_to_number(parts[0], total, unit)).rstrip('0').rstrip('.')

			if len(parts) > 1:
				newrange += ':' + ('%s' % self.human_to_number(parts[1], total, unit)).rstrip('0').rstrip('.')

			if range != newrange:
				self.verbose(3, 'Changed range/thresold from "' + range + '" to "' + newrange + '"')

			return newrange
		else:
			return ''


	def verbose(self, level, output):
		if level <= self.options.verbose:
			print 'V' + str(level) + ': ' + output


	def max_returncode(self, returncodes):
		for rc in self.returncode_priority:
			if rc in returncodes:
				break

		return rc


	def exit(self):
		returncode = self.max_returncode(self.__returncode)

		self.back2nagios(returncode, statusline=self.__output, multiline=self.__multilineoutput, performancedata=self.__performancedata)


	def back2nagios(self, returncode, statusline=None, multiline=None, performancedata=None, subtag=None, exit=True):
		# FIXME: Make 'returncode' also accept strings
		# Build status line
		out = self.__tagforstatusline
		if subtag:
			out += '(' + subtag.replace('|', ' ') + ')'
		out += ' ' + self.RETURNSTRINGS[returncode]

		# Check if there's a status line text and build it
		if statusline:
			out += ' - '
			if type(statusline) == str:
				out += statusline
			elif type(statusline) in [list, tuple]:
				out += ', '.join(statusline).replace('|', ' ')

		# Check if we have multi line output and build it
		if multiline:
			if type(multiline) == str:
				out += '\n' + multiline.replace('|', ' ')
			elif type(multiline) in [list, tuple]:
				out += '\n' + '\n'.join(multiline).replace('|', ' ')

		# Check if there's perfdata
		if performancedata:
			out += '|'
			if type(performancedata) == str:
				out += performancedata
			elif type(performancedata) in [list, tuple]:
				out += ' '.join(performancedata).replace('|', ' ')

		# Exit program or return output line(s)
		if exit:
			print out
			sys.exit(returncode)
		else:
			return (returncode, out)

##############################################################################

class SNMPMonitoringPlugin(MonitoringPlugin):

	def __init__(self, *args, **kwargs):
		# Same as "MonitoringPlugin.__init__(*args, **kwargs)" but a little bit more flexible
		#super(MonitoringPlugin, self).__init__(*args, **kwargs)
		MonitoringPlugin.__init__(self, *args, **kwargs)

		self.add_cmdlineoption('-H', '', 'host', 'Host to check', default='127.0.0.1')
		self.add_cmdlineoption('-P', '', 'snmpversion', 'SNMP protocol version', metavar='1', default='1')
		self.add_cmdlineoption('-C', '', 'snmpauth', 'SNMP v1/v2c community OR SNMP v3 quadruple', metavar='public', default='public')
		self.add_cmdlineoption('', '--snmpcmdlinepath', 'snmpcmdlinepath', 'Path to "snmpget" and "snmpwalk"', metavar='/usr/bin/', default='/usr/bin')
		# FIXME
		self.add_cmdlineoption('', '--nonetsnmp', 'nonetsnmp', 'Do not use NET-SNMP python bindings', action='store_true')
		# self.__optparser.add_option('', '--nonetsnmp', dest='nonetsnmp',  help='Do not use NET-SNMP python bindings', action='store_true')

		self.__SNMP_Cache = {}

		self.__use_netsnmp = False
		self.__prepared_snmp = False


	def prepare_snmp(self):
		if not self._cmdlineoptions_parsed:
			self.parse_cmdlineoptions()

		if not self.options.nonetsnmp:
			try:
				import netsnmp
				self.__use_netsnmp = True
			except ImportError:
				pass

		if self.__use_netsnmp:
			self.verbose(1, 'Using NET-SNMP Python bindings')

			self.SNMPGET_wrapper = self.__SNMPGET_netsnmp
			self.SNMPWALK_wrapper = self.__SNMPWALK_netsnmp

			if self.options.snmpversion == '2c':
				self.options.snmpversion = '2'

		else:
			self.verbose(1, 'Using NET-SNMP command line tools')

			self.SNMPGET_wrapper = self.__SNMPGET_cmdline
			self.SNMPWALK_wrapper = self.__SNMPWALK_cmdline

			# Building command lines
			self.__CMDLINE_get = os.path.join(self.options.snmpcmdlinepath, 'snmpget') + ' -OqevtU '
			self.__CMDLINE_walk = os.path.join(self.options.snmpcmdlinepath, 'snmpwalk') + ' -OqevtU '

			if self.options.snmpversion in [1, 2, '1', '2', '2c']:
				if self.options.snmpversion in [2, '2']:
					self.options.snmpversion = '2c'
				self.__CMDLINE_get += ' -v' + str(self.options.snmpversion) + ' -c' + self.options.snmpauth + ' '
				self.__CMDLINE_walk += ' -v' + str(self.options.snmpversion) + ' -c' + self.options.snmpauth + ' '
			elif options.snmpversion == [3, '3']:
				# FIXME: Better error handling
				try:
					snmpauth = self.options.snmpauth.split(':')
					self.__CMDLINE_get += ' -v3 -l' + snmpauth[0] + ' -u' + snmpauth[1] + ' -a' + snmpauth[2] + ' -A' + snmpauth[3] + ' '
					self.__CMDLINE_walk += ' -v3 -l' + snmpauth[0] + ' -u' + snmpauth[1] + ' -a' + snmpauth[2] + ' -A' + snmpauth[3] + ' '
				except:
					self.back2nagios(3, 'Could not build SNMPv3 command line, need "SecLevel:SecName:AuthProtocol:AuthKey"')
			else:
				self.back2nagios(3, 'Unknown SNMP version "' + str(self.options.snmpversion) + '"')

			self.__CMDLINE_get += ' ' + self.options.host + ' %s 2>/dev/null'
			self.__CMDLINE_walk += ' ' + self.options.host + ' %s 2>/dev/null'

			self.verbose(3, 'Using commandline: ' + self.__CMDLINE_get)
			self.verbose(3, 'Using commandline: ' + self.__CMDLINE_walk)

			# Test if snmp(get|walk) are executable
			for fpath in [self.__CMDLINE_get, self.__CMDLINE_walk,]:
				fpath = fpath.split(' ',1)[0]
				if not( os.path.exists(fpath) and os.path.isfile(fpath) and os.access(fpath, os.X_OK) ):
					self.back2nagios(3, 'Could not execute "%s"' % fpath)

		self.__prepared_snmp = True


	def find_index_for_value(self, list_indexes, list_values, wanted):
		self.verbose(2, 'Look for "' + str(wanted) + '"')

		index = None

		if len(list_indexes) != len(list_values):
			self.verbose(1, 'Length of index and value lists do not match!')
			return None

		try:
			index = list_values.index(wanted)
			index = list_indexes[index]
		except ValueError:
			pass

		if index:
			self.verbose(2, 'Found "' + str(wanted) +'" with index "' + str(index) + '"')
		else:
			self.verbose(2, 'Nothing found!')

		return index


	def find_in_table(self, oid_index, oid_values, wanted):
		self.verbose(2, 'Look for "' + str(wanted) + '" in "' + str(oid_values) +'"')

		index = None
		indexes = list(self.SNMPWALK(oid_index))
		values = list(self.SNMPWALK(oid_values))

		if len(indexes) != len(values):
			self.back2nagios(3, 'Different data from 2 SNMP Walks!')

		return self.find_index_for_value(indexes, values, wanted)


	def SNMPGET(self, baseoid, idx=None, exitonerror=True):
		if type(baseoid) in (list, tuple):
			if idx not in ['', None]:
				idx = '.' + str(idx)
			else:
				idx = ''

			if self.options.snmpversion in [1, '1']:
				value_low = long(self.SNMPGET_wrapper(baseoid[1] +  idx, exitonerror=exitonerror))
				if value_low < 0L:
					value_low += 2 ** 32

				value_hi = long(self.SNMPGET_wrapper(baseoid[2] + idx, exitonerror=exitonerror))
				if value_hi < 0L:
					value_hi += 2 ** 32

				return value_hi * 2L ** 32L + value_low

			elif self.options.snmpversion in [2, 3, '2', '2c', '3']:
				return long(self.SNMPGET_wrapper(baseoid[0] + idx, exitonerror=exitonerror))

		elif type(baseoid) in (str, ) and idx != None:
			return self.SNMPGET_wrapper(baseoid + '.' + str(idx), exitonerror=exitonerror)
		else:
			return self.SNMPGET_wrapper(baseoid, exitonerror=exitonerror)


	def SNMPWALK(self, baseoid, exitonerror=True):
		return self.SNMPWALK_wrapper(baseoid, exitonerror=exitonerror)


	def __SNMPGET_netsnmp(self, oid, exitonerror=True):
		if not self.__prepared_snmp:
			self.prepare_snmp()

		if oid in self.__SNMP_Cache:
			self.verbose(2, "%40s -> (CACHED) %s" % (oid, self.__SNMP_Cache[oid]))
			return self.__SNMP_Cache[oid]

		result = netsnmp.snmpget(oid, Version=int(self.options.snmpversion), DestHost=self.options.host, Community=self.options.snmpauth)[0]

		if not result:
			if exitonerror:
				self.back2nagios(3, 'Timeout or no answer from "%s" looking for "%s"' % (self.options.host, oid))
			else:
				return None

		self.__SNMP_Cache[oid] = result

		self.verbose(2, "%40s -> %s" % (oid, result))
		return result


	def __SNMPWALK_netsnmp(self, oid, exitonerror=True):
		if not self.__prepared_snmp:
			self.prepare_snmp()

		if oid in self.__SNMP_Cache:
			self.verbose(2, "%40s -> (CACHED) %s" % (oid, self.__SNMP_Cache[oid]))
			return self.__SNMP_Cache[oid]

		result = netsnmp.snmpwalk(oid, Version=int(self.options.snmpversion), DestHost=self.options.host, Community=self.options.snmpauth)

		if not result:
			if exitonerror:
				self.back2nagios(3, 'Timeout or no answer from "%s" looking for "%s"' % (self.options.host, oid))
			else:
				return None

		self.__SNMP_Cache[oid] = result

		self.verbose(2, "%40s -> %s" %  (oid, result))
		return result


	def __SNMPGET_cmdline(self, oid, exitonerror=True):
		if not self.__prepared_snmp:
			self.prepare_snmp()

		cmdline = self.__CMDLINE_get % oid
		self.verbose(2, cmdline)

		if oid in self.__SNMP_Cache:
			self.verbose(2, "(CACHED) %s" % (self.__SNMP_Cache[oid]))
			return self.__SNMP_Cache[oid]

		cmd = os.popen(cmdline)
		out = cmd.readline().rstrip().replace('"','')
		retcode = cmd.close()

		if retcode:
			if not exitonerror:
				return None
			if retcode == 256:
				self.back2nagios(3, 'Timeout - no SNMP answer from "' + self.options.host + '"')
			elif retcode ==512:
				self.back2nagios(3, 'OID "' + oid + '" not found')
			else:
				self.back2nagios(3, 'Unknown error code "' + str(retcode) + '" from command line utils')

		self.__SNMP_Cache[oid] = out

		self.verbose(1, out)
		return out


	def __SNMPWALK_cmdline(self, oid, exitonerror=True):
		if not self.__prepared_snmp:
			self.prepare_snmp()

		cmdline = self.__CMDLINE_walk % oid
		self.verbose(2, cmdline)

		if oid in self.__SNMP_Cache:
			self.verbose(2, "(CACHED) %s" % (self.__SNMP_Cache[oid]))
			return self.__SNMP_Cache[oid]

		cmd = os.popen(cmdline)
		out = cmd.readlines()
		retcode = cmd.close()

		if retcode:
			if not exitonerror:
				return None
			if retcode == 256:
				self.back2nagios(3, 'Timeout - no SNMP answer from "' + self.options.host + '"')
			elif retcode ==512:
				self.back2nagios(3, 'OID "' + oid + '" not found')
			else:
				self.back2nagios(3, 'Unknown error code "' + str(retcode) + '" from command line utils')

		for line in range(0,len(out)):
			out[line] = out[line].rstrip().replace('"','')

		self.__SNMP_Cache[oid] = out

		self.verbose(1, str(out))
		return out


##############################################################################

def main():
	myplugin = MonitoringPlugin(pluginname='check_testplugin', tagforstatusline='TEST')

	from pprint import pprint
	pprint(myplugin.back2nagios(0, 'Nr. 01: Simple plugin', exit=False) )
	pprint(myplugin.back2nagios(0, 'Nr. 02: Simple plugin with sub tag', subtag='MySubTag', exit=False) )

	pprint(myplugin.back2nagios(0, 'Nr. 10: Exit Code OK', exit=False) )
	pprint(myplugin.back2nagios(1, 'Nr. 11: Exit Code WARNING', exit=False) )
	pprint(myplugin.back2nagios(2, 'Nr. 12: Exit Code CRITICAL', exit=False) )
	pprint(myplugin.back2nagios(3, 'Nr. 13: Exit Code UNKNOWN', exit=False) )

	ret = myplugin.back2nagios(0, 'Nr. 20: Plugin with string-based multiline output', 'Line 2\nLine 3\nLine4', exit=False)
	print ret[1]
	print 'Returncode: ' + str(ret[0])
	ret = myplugin.back2nagios(0, 'Nr. 21: Plugin with list-based multiline output', ['Line 2', 'Line 3', 'Line4'], exit=False)
	print ret[1]
	print 'Returncode: ' + str(ret[0])
	ret = myplugin.back2nagios(0, 'Nr. 22: Plugin with tuple-based multiline output', ('Line 2', 'Line 3', 'Line4'), exit=False)
	print ret[1]
	print 'Returncode: ' + str(ret[0])

	myplugin.add_performancedata('Val1', 42, '')
	myplugin.add_performancedata('Val2', 23, 'c', warn=10, crit=20, min=0, max=100)
	myplugin.add_performancedata('Val 3', '2342', 'c', warn=10, crit=20, min=0, max=100)
	pprint(myplugin.back2nagios(0, 'Nr. 30: With perfdatas', exit=False) )

	myplugin.back2nagios(0, 'Nr. 99: Exit test suite with OK')


if __name__ == '__main__':
	main()

#vim: ts=4 sw=4
