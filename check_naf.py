#!/usr/bin/env python
# -*- encoding: utf-8 -*-

#####################################################################
# (c) 2006-2010 by Sven Velt and team(ix) GmbH, Nuernberg, Germany  #
#                  sv@teamix.net                                    #
#                                                                   #
# This file is part of check_naf (FKA check_netappfiler)            #
#                                                                   #
# check_naf is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published #
# by the Free Software Foundation, either version 2 of the License, #
# or (at your option) any later version.                            #
#                                                                   #
# check_naf is distributed in the hope that it will be useful, but  #
# WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the      #
# GNU General Public License for more details.                      #
#                                                                   #
# You should have received a copy of the GNU General Public License #
# along with check_naf. If not, see <http://www.gnu.org/licenses/>. #
#####################################################################

from monitoringplugin import SNMPMonitoringPlugin

class CheckNAF(SNMPMonitoringPlugin):
	OID = {
			'CPU_Arch': '.1.3.6.1.4.1.789.1.1.11.0',
			'CPU_Time_Busy': '.1.3.6.1.4.1.789.1.2.1.3.0',
			'CPU_Time_Idle': '.1.3.6.1.4.1.789.1.2.1.5.0',
			'CPU_Context_Switches': '.1.3.6.1.4.1.789.1.2.1.8.0',

			'Disks_Total': '.1.3.6.1.4.1.789.1.6.4.1.0',
			'Disks_Active': '.1.3.6.1.4.1.789.1.6.4.2.0',
			'Disks_Reconstructing': '.1.3.6.1.4.1.789.1.6.4.3.0',
			'Disks_ReconstParity': '.1.3.6.1.4.1.789.1.6.4.4.0',
			'Disks_Scrubbing': '.1.3.6.1.4.1.789.1.6.4.6.0',
			'Disks_Failed': '.1.3.6.1.4.1.789.1.6.4.7.0',
			'Disks_Spare': '.1.3.6.1.4.1.789.1.6.4.8.0',
			'Disks_ZeroDisks': '.1.3.6.1.4.1.789.1.6.4.9.0',
			'Disks_Failed_Descr': '.1.3.6.1.4.1.789.1.6.4.10.0',

			'Global_Status': '.1.3.6.1.4.1.789.1.2.2.4.0',
			'Global_Status_Message': '.1.3.6.1.4.1.789.1.2.2.25.0',

			'NVRAM_Status': '.1.3.6.1.4.1.789.1.2.5.1.0',

			'Model': '.1.3.6.1.4.1.789.1.1.5.0',
			'ONTAP_Version': '.1.3.6.1.4.1.789.1.1.2.0',

			'df_FS_Index': '.1.3.6.1.4.1.789.1.5.4.1.1',
			'df_FS_Name': '.1.3.6.1.4.1.789.1.5.4.1.2',
			'df_FS_Mounted_On': '.1.3.6.1.4.1.789.1.5.4.1.10',
			'df_FS_Status': '.1.3.6.1.4.1.789.1.5.4.1.20',
			'df_FS_Type': '.1.3.6.1.4.1.789.1.5.4.1.23',

			'df_FS_kBTotal': ['.1.3.6.1.4.1.789.1.5.4.1.29', '.1.3.6.1.4.1.789.1.5.4.1.15', '.1.3.6.1.4.1.789.1.5.4.1.14',],
			'df_FS_kBUsed': ['.1.3.6.1.4.1.789.1.5.4.1.30', '.1.3.6.1.4.1.789.1.5.4.1.17', '.1.3.6.1.4.1.789.1.5.4.1.16',],
			'df_FS_kBAvail': ['.1.3.6.1.4.1.789.1.5.4.1.31', '.1.3.6.1.4.1.789.1.5.4.1.19', '.1.3.6.1.4.1.789.1.5.4.1.18',],

			'df_FS_INodeUsed': '.1.3.6.1.4.1.789.1.5.4.1.7',
			'df_FS_INodeFree': '.1.3.6.1.4.1.789.1.5.4.1.8',

			'df_FS_MaxFilesAvail': '.1.3.6.1.4.1.789.1.5.4.1.11',
			'df_FS_MaxFilesUsed': '.1.3.6.1.4.1.789.1.5.4.1.12',
			'df_FS_MaxFilesPossible': '.1.3.6.1.4.1.789.1.5.4.1.13',
			}

	OWC = {
			'Global_Status': ( (3,), (4,), (5,6), ),
			'NVRAM_Status': ( (1,9), (2,5,8), (3,4,6), ),
			}

	Status2String = {
			'CPU_Arch' : { '1' : 'x86', '2' : 'alpha', '3' : 'mips', '4' : 'sparc', '5' : 'amd64', },
			'NVRAM_Status' : { '1' : 'ok', '2' : 'partiallyDischarged', '3' : 'fullyDischarged', '4' : 'notPresent', '5' : 'nearEndOfLife', '6' : 'atEndOfLife', '7' : 'unknown', '8' : 'overCharged', '9' : 'fullyCharged', },
			'df_FS_Status' : { '1' : 'unmounted', '2' : 'mounted', '3' : 'frozen', '4' : 'destroying', '5' : 'creating', '6' : 'mounting', '7' : 'unmounting', '8' : 'nofsinfo', '9' : 'replaying', '10': 'replayed', },
			'df_FS_Type' : { '1' : 'traditionalVolume', '2' : 'flexibleVolume', '3' : 'aggregate', },
		}


	def map_status_to_returncode(self, value, mapping):
		for returncode in xrange(0,3):
			if value in mapping[returncode]:
				return returncode
		return 3


	def check_cpu(self, warn='', crit=''):
		cpu_arch = self.SNMPGET(self.OID['CPU_Arch'])
		cpu_timebusy = int(self.SNMPGET(self.OID['CPU_Time_Busy']))
		# cputimeidle = int(self.SNMPGET(self.OID['CPU_Time_Idle']))
		cpu_cs = self.SNMPGET(self.OID['CPU_Context_Switches'])

		if '%' in warn:
			warn = warn[:-1]
		if '%' in crit:
			crit = crit[:-1]

		returncode = self.value_wc_to_returncode(cpu_timebusy, warn, crit)
		output = 'CPU ' + str(cpu_timebusy) + '% busy, CPU architecture: ' + self.Status2String['CPU_Arch'].get(cpu_arch)
		perfdata = []
		pd = {'label':'nacpu', 'value':cpu_timebusy, 'unit':'%', 'min':0, 'max':100}
		if warn:
			pd['warn'] = warn
		if crit:
			pd['crit'] = crit
		perfdata.append(pd)
		perfdata.append({'label':'nacs', 'value':cpu_cs, 'unit':'c'})

		return self.remember_check('cpu', returncode, output, perfdata=perfdata)


	def check_disk(self, target='failed', warn='', crit=''):
		di_total = int(self.SNMPGET(self.OID['Disks_Total']))
		di_active = int(self.SNMPGET(self.OID['Disks_Active']))
		di_reconstructing = int(self.SNMPGET(self.OID['Disks_Reconstructing']))
		di_reconstparity = int(self.SNMPGET(self.OID['Disks_ReconstParity']))
		# di_scrubbing = int(self.SNMPGET(self.OID['Disks_Scrubbing']))
		di_failed = int(self.SNMPGET(self.OID['Disks_Failed']))
		di_spare = int(self.SNMPGET(self.OID['Disks_Spare']))
		# di_zerodisks = int(self.SNMPGET(self.OID['Disks_ZeroDisks']))

		di_reconstr = di_reconstructing + di_reconstparity

		if target == 'spare':
			returncode = self.value_wc_to_returncode(di_spare, warn, crit)
			output = str(di_spare) + ' spare disk'
			if di_spare > 1:
				output += 's'
		else:
			target = 'failed' # Set to defined value
			returncode = self.value_wc_to_returncode(di_failed, warn, crit)
			if returncode == 0:
				output = 'No failed disks'
			else:
				output = self.SNMPGET(self.OID['Disks_Failed_Descr'])

		perfdata = []
		perfdata.append({'label':'nadisk_total', 'value':di_total, 'unit':'', 'min':0})
		perfdata.append({'label':'nadisk_active', 'value':di_active, 'unit':'', 'min':0})
		pd = {'label':'nadisk_spare', 'value':di_spare, 'unit':'', 'min':0}
		if warn and target=='spare':
			pd['warn'] = warn
		if crit and target=='spare':
			pd['crit'] = crit
		perfdata.append(pd)
		pd = {'label':'nadisk_failed', 'value':di_failed, 'unit':'', 'min':0}
		if warn and target=='failed':
			pd['warn'] = warn
		if crit and target=='failed':
			pd['crit'] = crit
		perfdata.append(pd)

		return self.remember_check('disk', returncode, output, perfdata=perfdata, target=target)


	def check_global(self):
		model = self.SNMPGET(self.OID['Model'])
		globalstatus = int(self.SNMPGET(self.OID['Global_Status']))
		globalstatusmsg = self.SNMPGET(self.OID['Global_Status_Message'])[:255]

		returncode = self.map_status_to_returncode(globalstatus, self.OWC['Global_Status'])
		output = model + ': ' + globalstatusmsg

		return self.remember_check('global', returncode, output)


	def check_nvram(self):
		nvramstatus = int(self.SNMPGET(self.OID['NVRAM_Status']))

		returncode = self.map_status_to_returncode(nvramstatus, self.OWC['NVRAM_Status'])
		output = 'NVRAM battery status is "' + self.Status2String['NVRAM_Status'].get(str(nvramstatus)) + '"'

		return self.remember_check('nvram', returncode, output)


	def check_version(self):
		model = self.SNMPGET(self.OID['Model'])
		ontapversion = self.SNMPGET(self.OID['ONTAP_Version'])

		return self.remember_check('version', 0, model + ': ' + ontapversion)


	def common_vol_idx(self, volume):
		if volume.endswith('.snapshot'):
			return None

		idx = str(self.find_in_table(self.OID['df_FS_Index'], self.OID['df_FS_Name'] , volume))
		sn_idx = int(idx) + 1

		return (idx, sn_idx)


	def check_vol_data(self, volume, warn, crit):
		(idx, sn_idx) = self.common_vol_idx(volume)

		fs_total = long(self.SNMPGET(self.OID['df_FS_kBTotal'], idx)) * 1024L
		fs_used = long(self.SNMPGET(self.OID['df_FS_kBUsed'], idx)) * 1024L
		# fs_avail = long(self.SNMPGET(self.OID['df_FS_kBAvail'], idx)) * 1024L
		sn_total = long(self.SNMPGET(self.OID['df_FS_kBTotal'], sn_idx)) * 1024L
		sn_used = long(self.SNMPGET(self.OID['df_FS_kBUsed'], sn_idx)) * 1024L
		# sn_avail = long(self.SNMPGET(self.OID['df_FS_kBAvail'], sn_idx)) * 1024L

		mountedon = self.SNMPGET(self.OID['df_FS_Mounted_On'] + "." + idx)
		status = self.Status2String['df_FS_Status'].get(self.SNMPGET(self.OID['df_FS_Status'] + "." + idx))
		fstype = self.Status2String['df_FS_Type'].get(self.SNMPGET(self.OID['df_FS_Type'] + "." + idx))

		fs_pctused = float(fs_used) / float(fs_total) * 100.0

		warn = self.range_dehumanize(warn, fs_total)
		crit = self.range_dehumanize(crit, fs_total)

		returncode = self.value_wc_to_returncode(fs_used, warn, crit)
		output = volume + ': Used ' + self.value_to_human_binary(fs_used, 'B')
		output += ' (' + '%3.1f' % fs_pctused + '%)'+ ' out of ' + self.value_to_human_binary(fs_total, 'B')
		target = volume.replace('/vol/', '')[:-1]
		perfdata = []
		perfdata.append({'label':'navdu_' + target, 'value':fs_used, 'unit':'B', 'warn':warn, 'crit':crit, 'min':0})
		perfdata.append({'label':'navdt_' + target, 'value':fs_total, 'unit':'B'})
		perfdata.append({'label':'navsu_' + target, 'value':sn_used, 'unit':'B', 'min':0})
		perfdata.append({'label':'navst_' + target, 'value':sn_total, 'unit':'B'})

		return self.remember_check('vol_data', returncode, output, perfdata=perfdata, target=target)


	def check_vol_snap(self, volume, warn, crit):
		(idx, sn_idx) = self.common_vol_idx(volume)

		# fs_total = long(self.SNMPGET(self.OID['df_FS_kBTotal'], idx)) * 1024L
		# fs_used = long(self.SNMPGET(self.OID['df_FS_kBUsed'], idx)) * 1024L
		# fs_avail = long(self.SNMPGET(self.OID['df_FS_kBAvail'], idx)) * 1024L
		sn_total = long(self.SNMPGET(self.OID['df_FS_kBTotal'], sn_idx)) * 1024L
		sn_used = long(self.SNMPGET(self.OID['df_FS_kBUsed'], sn_idx)) * 1024L
		# sn_avail = long(self.SNMPGET(self.OID['df_FS_kBAvail'], sn_idx)) * 1024L

		sn_pctused = float(sn_used) / float(sn_total) * 100.0

		warn = self.range_dehumanize(warn, sn_total)
		crit = self.range_dehumanize(crit, sn_total)

		returncode = self.value_wc_to_returncode(sn_used, warn, crit)
		output = volume + '.snapshot: Used ' + self.value_to_human_binary(sn_used, 'B')
		output += ' (' + '%3.1f' % sn_pctused + '%)'+ ' out of ' + self.value_to_human_binary(sn_total, 'B')
		target = volume.replace('/vol/', '')[:-1]
		perfdata = []
		perfdata.append({'label':'navsu_' + target, 'value':sn_used, 'unit':'B', 'warn':warn, 'crit':crit, 'min':0})
		perfdata.append({'label':'navst_' + target, 'value':sn_total, 'unit':'B'})

		return self.remember_check('vol_snap', returncode, output, perfdata=perfdata, target=target)


	def check_vol_inode(self, volume, warn, crit):
		(idx, sn_idx) = self.common_vol_idx(volume)

		in_used = long(self.SNMPGET(self.OID['df_FS_INodeUsed'] + '.' + idx))
		in_free = long(self.SNMPGET(self.OID['df_FS_INodeFree'] + '.' + idx))
		in_total = in_used + in_free

		in_pctused = float(in_used) / float(in_total) * 100.0

		warn = self.range_dehumanize(warn, in_total)
		crit = self.range_dehumanize(crit, in_total)

		returncode = self.value_wc_to_returncode(in_used, warn, crit)
		output = volume + ': Used inodes ' + self.value_to_human_si(in_used)
		output += ' (' + '%3.1f' % in_pctused + '%)'+ ' out of ' + self.value_to_human_si(in_total)
		target = volume.replace('/vol/', '')[:-1]
		perfdata = []
		perfdata.append({'label':'naviu_' + target, 'value':in_used, 'unit':None, 'warn':warn, 'crit':crit, 'min':0})
		perfdata.append({'label':'navit_' + target, 'value':in_total, 'unit':None})

		return self.remember_check('vol_inode', returncode, output, perfdata=perfdata, target=target)


	def check_vol_files(self, volume, warn, crit):
		(idx, sn_idx) = self.common_vol_idx(volume)

		fi_avail = long(self.SNMPGET(self.OID['df_FS_MaxFilesAvail'] + '.' + idx))
		fi_used = long(self.SNMPGET(self.OID['df_FS_MaxFilesUsed'] + '.' + idx))
		fi_possible = long(self.SNMPGET(self.OID['df_FS_MaxFilesPossible'] + '.' + idx))
		fi_total = fi_used + fi_avail

		fi_pctused = float(fi_used) / float(fi_total) * 100.0

		warn = self.range_dehumanize(warn, fi_total)
		crit = self.range_dehumanize(crit, fi_total)

		returncode = self.value_wc_to_returncode(fi_used, warn, crit)
		output = volume + ': Used files ' + self.value_to_human_si(fi_used)
		output += ' (' + '%3.1f' % fi_pctused + '%)'+ ' out of ' + self.value_to_human_si(fi_total)
		output += ', may raised to ' + self.value_to_human_si(fi_possible)
		target = volume.replace('/vol/', '')[:-1]
		perfdata = []
		perfdata.append({'label':'navfu_' + target, 'value':fi_used, 'unit':None, 'warn':warn, 'crit':crit, 'min':0})
		perfdata.append({'label':'navft_' + target, 'value':fi_total, 'unit':None})

		return self.remember_check('vol_files', returncode, output, perfdata=perfdata, target=target)






def main():
	plugin = CheckNAF(pluginname='check_naf', tagforstatusline='NAF', description=u'Monitoring NetApp™ FAS systems', version='0.9')

	plugin.add_cmdlineoption('', '--check', 'check', 'OBSOLETE - use new syntax!', default='')
	plugin.add_cmdlineoption('', '--target', 'target', 'OBSOLETE - use new syntax!', default='')
	plugin.add_cmdlineoption('-w', '', 'warn', 'OBSOLETE - use new syntax!', default='')
	plugin.add_cmdlineoption('-c', '', 'crit', 'OBSOLETE - use new syntax!', default='')
	plugin.parse_cmdlineoptions()

	plugin.prepare_snmp()

	if plugin.options.check or plugin.options.target:
		import sys
		arguments = plugin.options.check
		for s in [plugin.options.target, plugin.options.warn, plugin.options.crit]:
			arguments += ':' + s
		plugin.back2nagios(3, 'Obsolete syntax - please use new syntax: "%s %s"' % (sys.argv[0], arguments))


	checks = []

	for quad in plugin.args:
		quad = quad.split(':')
		quad = (quad + ['', '', ''])[:4] # Fix length to 4, fill with ''

		# Convert list of checks to list
		if ',' in quad[0]:
			quad[0] = quad[0].split(',')
		else:
			quad[0] = [quad[0],]

		# Convert list of targets to list
		if ',' in quad[1]:
			quad[1] = quad[1].split(',')
		else:
			quad[1] = [quad[1],]

		for target in quad[1]:
			for check in quad[0]:
				checks.append(tuple([check, target, quad[2], quad[3]]))

	if len(checks) == 0:
		plugin.back2nagios(3, 'No check specified!')

	for quad in checks:
		(check, target, warn, crit) = tuple(quad)

		if check == 'global':
			result = plugin.check_global()
		elif check == 'cpu':
			result = plugin.check_cpu(warn=warn, crit=crit)
		elif check == 'disk':
			result = plugin.check_disk(target=target, warn=warn, crit=crit)
		elif check == 'nvram':
			result = plugin.check_nvram()
		elif check == 'version':
			result = plugin.check_version()
		elif check == 'vol_data':
			result = plugin.check_vol_data(volume=target, warn=warn, crit=crit)
		elif check == 'vol_snap':
			result = plugin.check_vol_snap(volume=target, warn=warn, crit=crit)
		elif check =='vol_inode':
			result = plugin.check_vol_inode(volume=target, warn=warn, crit=crit)
		elif check =='vol_files':
			result = plugin.check_vol_files(volume=target, warn=warn, crit=crit)

	# from pprint import pprint
	# pprint(plugin.dump_brain())

	plugin.brain2output()
	plugin.exit()

if __name__ == '__main__':
	main()

#vim: ts=4 sw=4 foldmethod=indent
