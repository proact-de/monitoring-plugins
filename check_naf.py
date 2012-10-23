#!/usr/bin/env python
# -*- encoding: utf-8 -*-

#####################################################################
# (c) 2006-2011 by Sven Velt and team(ix) GmbH, Nuernberg, Germany  #
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
import sys

try:
	from monitoringplugin import SNMPMonitoringPlugin
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


class CheckNAF(SNMPMonitoringPlugin):
	OID = {
			'Cluster_Settings': '.1.3.6.1.4.1.789.1.2.3.1.0',
			'Cluster_State': '.1.3.6.1.4.1.789.1.2.3.2.0',
			'Cluster_InterconnectStatus': '.1.3.6.1.4.1.789.1.2.3.8.0',
			'Cluster_CannotTakeOverCause': '.1.3.6.1.4.1.789.1.2.3.3.0',

			'CIFS_Connected_Users': '.1.3.6.1.4.1.789.1.7.2.9.0',
			'CIFS_Total_Ops': '.1.3.6.1.4.1.789.1.7.3.1.1.1.0',
			'CIFS_Total_Calls': '.1.3.6.1.4.1.789.1.7.3.1.1.2.0',
			'CIFS_Bad_Calls': '.1.3.6.1.4.1.789.1.7.3.1.1.3.0',
			'CIFS_Get_Attrs': '.1.3.6.1.4.1.789.1.7.3.1.1.4.0',
			'CIFS_Reads': '.1.3.6.1.4.1.789.1.7.3.1.1.5.0',
			'CIFS_Writes': '.1.3.6.1.4.1.789.1.7.3.1.1.6.0',
			'CIFS_Locks': '.1.3.6.1.4.1.789.1.7.3.1.1.7.0',
			'CIFS_Opens': '.1.3.6.1.4.1.789.1.7.3.1.1.8.0',
			'CIFS_DirOps': '.1.3.6.1.4.1.789.1.7.3.1.1.9.0',
			'CIFS_Others': '.1.3.6.1.4.1.789.1.7.3.1.1.10.0',

			'CP': '.1.3.6.1.4.1.789.1.2.6',

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

			'ExtCache_Type': '.1.3.6.1.4.1.789.1.26.1.0',
			'ExtCache_SubType': '.1.3.6.1.4.1.789.1.26.2.0',
			'ExtCache_Size': '.1.3.6.1.4.1.789.1.26.4.0',
			'ExtCache_Usedsize': '.1.3.6.1.4.1.789.1.26.5.0',
			'ExtCache_Options': '.1.3.6.1.4.1.789.1.26.7.0',
			'ExtCache_Hits': '.1.3.6.1.4.1.789.1.26.8.0',
			'ExtCache_Misses': '.1.3.6.1.4.1.789.1.26.9.0',
			'ExtCache_Inserts': '.1.3.6.1.4.1.789.1.26.10.0',
			'ExtCache_Evicts': '.1.3.6.1.4.1.789.1.26.11.0',
			'ExtCache_Invalidates': '.1.3.6.1.4.1.789.1.26.12.0',
			'ExtCache_MetaData': '.1.3.6.1.4.1.789.1.26.15.0',

			'Global_Status': '.1.3.6.1.4.1.789.1.2.2.4.0',
			'Global_Status_Message': '.1.3.6.1.4.1.789.1.2.2.25.0',

			'Net_ifIndex': '.1.3.6.1.4.1.789.1.22.1.2.1.1',
			'Net_ifDescr': '.1.3.6.1.4.1.789.1.22.1.2.1.2',
			'Net_InBytes': ['.1.3.6.1.4.1.789.1.22.1.2.1.25', '.1.3.6.1.4.1.789.1.22.1.2.1.4', '.1.3.6.1.4.1.789.1.22.1.2.1.3',],
			'Net_OutBytes': ['.1.3.6.1.4.1.789.1.22.1.2.1.31', '.1.3.6.1.4.1.789.1.22.1.2.1.16', '.1.3.6.1.4.1.789.1.22.1.2.1.15',],
			'Net_InDiscards': ['.1.3.6.1.4.1.789.1.22.1.2.1.28', '.1.3.6.1.4.1.789.1.22.1.2.1.10', '.1.3.6.1.4.1.789.1.22.1.2.1.9',],
			'Net_OutDiscards': ['.1.3.6.1.4.1.789.1.22.1.2.1.34', '.1.3.6.1.4.1.789.1.22.1.2.1.22', '.1.3.6.1.4.1.789.1.22.1.2.1.21',],
			'Net_InErrors': ['.1.3.6.1.4.1.789.1.22.1.2.1.29', '.1.3.6.1.4.1.789.1.22.1.2.1.12', '.1.3.6.1.4.1.789.1.22.1.2.1.11',],
			'Net_OutErrors': ['.1.3.6.1.4.1.789.1.22.1.2.1.35', '.1.3.6.1.4.1.789.1.22.1.2.1.24', '.1.3.6.1.4.1.789.1.22.1.2.1.23',],

			'IO_DiskReadBy': ['.1.3.6.1.4.1.789.1.2.2.32.0', '.1.3.6.1.4.1.789.1.2.2.16.0', '.1.3.6.1.4.1.789.1.2.2.15.0',],
			'IO_DiskWriteBy': ['.1.3.6.1.4.1.789.1.2.2.33.0', '.1.3.6.1.4.1.789.1.2.2.18.0', '.1.3.6.1.4.1.789.1.2.2.17.0',],
			'IO_NetInBy': ['.1.3.6.1.4.1.789.1.2.2.30.0', '.1.3.6.1.4.1.789.1.2.2.12.0', '.1.3.6.1.4.1.789.1.2.2.11.0',],
			'IO_NetOutBy': ['.1.3.6.1.4.1.789.1.2.2.31.0', '.1.3.6.1.4.1.789.1.2.2.14.0', '.1.3.6.1.4.1.789.1.2.2.13.0',],
			'IO_TapeReadBy': ['.1.3.6.1.4.1.789.1.2.2.34.0', '.1.3.6.1.4.1.789.1.2.2.20.0', '.1.3.6.1.4.1.789.1.2.2.19.0',],
			'IO_TapeWriteBy': ['.1.3.6.1.4.1.789.1.2.2.35.0', '.1.3.6.1.4.1.789.1.2.2.22.0', '.1.3.6.1.4.1.789.1.2.2.21.0',],
			'IO_FCPReadBy': ['.1.3.6.1.4.1.789.1.17.20.0', '.1.3.6.1.4.1.789.1.17.3.0', '.1.3.6.1.4.1.789.1.17.4.0',],
			'IO_FCPWriteBy': ['.1.3.6.1.4.1.789.1.17.21.0', '.1.3.6.1.4.1.789.1.17.5.0', '.1.3.6.1.4.1.789.1.17.6.0',],
			'IO_iSCSIReadBy': ['.1.3.6.1.4.1.789.1.17.22.0', '.1.3.6.1.4.1.789.1.17.7.0', '.1.3.6.1.4.1.789.1.17.8.0',],
			'IO_iSCSIWriteBy': ['.1.3.6.1.4.1.789.1.17.23.0', '.1.3.6.1.4.1.789.1.17.9.0', '.1.3.6.1.4.1.789.1.17.10.0',],

			'NVRAM_Status': '.1.3.6.1.4.1.789.1.2.5.1.0',

			'OPs_NFS': ['.1.3.6.1.4.1.789.1.2.2.27.0', '.1.3.6.1.4.1.789.1.2.2.6.0', '.1.3.6.1.4.1.789.1.2.2.5.0',],
			'OPs_CIFS': ['.1.3.6.1.4.1.789.1.2.2.28.0', '.1.3.6.1.4.1.789.1.2.2.8.0', '.1.3.6.1.4.1.789.1.2.2.7.0',],
			'OPs_HTTP': ['.1.3.6.1.4.1.789.1.2.2.29.0', '.1.3.6.1.4.1.789.1.2.2.10.0', '.1.3.6.1.4.1.789.1.2.2.9.0',],
			'OPs_FCP': ['.1.3.6.1.4.1.789.1.17.25.0', '.1.3.6.1.4.1.789.1.17.14.0', '.1.3.6.1.4.1.789.1.17.13.0',],
			'OPs_iSCSI': ['.1.3.6.1.4.1.789.1.17.24.0', '.1.3.6.1.4.1.789.1.17.12.0', '.1.3.6.1.4.1.789.1.17.11.0',],

			'Snapmirror_On': '.1.3.6.1.4.1.789.1.9.1.0',
			'Snapmirror_License': '.1.3.6.1.4.1.789.1.9.19.0',
			'Snapmirror_Index': '.1.3.6.1.4.1.789.1.9.20.1.1',
			'Snapmirror_Src': '.1.3.6.1.4.1.789.1.9.20.1.2',
			'Snapmirror_Dst': '.1.3.6.1.4.1.789.1.9.20.1.3',
			'Snapmirror_Status': '.1.3.6.1.4.1.789.1.9.20.1.4',
			'Snapmirror_State': '.1.3.6.1.4.1.789.1.9.20.1.5',
			'Snapmirror_Lag': '.1.3.6.1.4.1.789.1.9.20.1.6',

			'Snapvault_On': '.1.3.6.1.4.1.789.1.19.1.0',
			'Snapvault_LicensePrimary': '.1.3.6.1.4.1.789.1.19.9.0',
			'Snapvault_LicenseSecondary': '.1.3.6.1.4.1.789.1.19.10.0',
			'Snapvault_Index': '.1.3.6.1.4.1.789.1.19.11.1.1',
			'Snapvault_Src': '.1.3.6.1.4.1.789.1.19.11.1.2',
			'Snapvault_Dst': '.1.3.6.1.4.1.789.1.19.11.1.3',
			'Snapvault_Status': '.1.3.6.1.4.1.789.1.19.11.1.4',
			'Snapvault_State': '.1.3.6.1.4.1.789.1.19.11.1.5',
			'Snapvault_Lag': '.1.3.6.1.4.1.789.1.19.11.1.6',

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
			'Cluster_InterconnectStatus': ( (4,), (3,), (1,2,), ),
			'Cluster_Settings': ( (2,), (1,3,4,), (5,), ),
			'Cluster_State': ( (2,4,), (), (1,3,), ),
			'Global_Status': ( (3,), (4,), (5,6), ),
			'NVRAM_Status': ( (1,9), (2,5,8), (3,4,6), ),
			'Snapmirror_State': ( (2,5,), (1,4,6,), (3,), ),
			'Snapvault_State': ( (2,5,7,), (1,3,4,6,), (None,), ),
			}

	Status2String = {
			'Cluster_CannotTakeOverCause': { '1' : 'ok', '2' : 'unknownReason', '3' : 'disabledByOperator', '4' : 'interconnectOffline', '5' : 'disabledByPartner', '6' : 'takeoverFailed', },
			'Cluster_InterconnectStatus': { '1' : 'notPresent', '2' : 'down', '3' : 'partialFailure', '4' : 'up', },
			'Cluster_Settings': { '1' : 'notConfigured', '2' : 'enabled', '3' : 'disabled', '4' : 'takeoverByPartnerDisabled', '5' : 'thisNodeDead', },
			'Cluster_State': { '1' : 'dead', '2' : 'canTakeover', '3' : 'cannotTakeover', '4' : 'takeover', },
			'CPU_Arch' : { '1' : 'x86', '2' : 'alpha', '3' : 'mips', '4' : 'sparc', '5' : 'amd64', },
			'NVRAM_Status' : { '1' : 'ok', '2' : 'partiallyDischarged', '3' : 'fullyDischarged', '4' : 'notPresent', '5' : 'nearEndOfLife', '6' : 'atEndOfLife', '7' : 'unknown', '8' : 'overCharged', '9' : 'fullyCharged', },
			'df_FS_Status' : { '1' : 'unmounted', '2' : 'mounted', '3' : 'frozen', '4' : 'destroying', '5' : 'creating', '6' : 'mounting', '7' : 'unmounting', '8' : 'nofsinfo', '9' : 'replaying', '10': 'replayed', },
			'df_FS_Type' : { '1' : 'traditionalVolume', '2' : 'flexibleVolume', '3' : 'aggregate', },
			'Snapmirror_Status': { '1' : 'idle', '2' : 'transferring', '3' : 'pending', '4' : 'aborting', '5' : 'migrating', '6' : 'quiescing', '7' : 'resyncing', '8' : 'waiting', '9' : 'syncing', '10': 'in-sync', },
			'Snapmirror_State': { '1' : 'uninitialized', '2' : 'snapmirrored', '3' : 'broken-off', '4' : 'quiesced', '5' : 'source', '6' : 'unknown', },
			'Snapvault_Status': { '1' : 'idle', '2' : 'transferring', '3' : 'pending', '4' : 'aborting', '5' : 'unknown_5', '6' : 'quiescing', '7' : 'resyncing', '8' : 'unknown_8', '9' : 'unknown_9', '10': 'unknown_10', '11': 'unknown_11', '12': 'paused', },
			'Snapvault_State': { '1' : 'uninitialized', '2' : 'snapvaulted', '3' : 'brokenOff', '4' : 'quiesced', '5' : 'source', '6' : 'unknown', '7' : 'restoring', },
		}


	def map_status_to_returncode(self, value, mapping):
		for returncode in xrange(0,3):
			if value in mapping[returncode]:
				return returncode
		return 3


	def check_cifs(self, target='', warn='', crit=''):
		if target == 'users':
			cifsConnectedUsers = long(self.SNMPGET(self.OID['CIFS_Connected_Users']))
			returncode = self.value_wc_to_returncode(cifsConnectedUsers, warn, crit)
			output = "%s connected users" % cifsConnectedUsers
			perfdata = [{'label':'nacifs_users', 'value':cifsConnectedUsers, 'unit':'', 'warn':warn, 'crit':crit, 'min':0},]

		elif target == 'stats':
			cifsTotalOps = self.SNMPGET(self.OID['CIFS_Total_Ops'])
			cifsTotalCalls = self.SNMPGET(self.OID['CIFS_Total_Calls'])
			cifsBadCalls = self.SNMPGET(self.OID['CIFS_Bad_Calls'])
			cifsGetAttrs = self.SNMPGET(self.OID['CIFS_Get_Attrs'])
			cifsReads = self.SNMPGET(self.OID['CIFS_Reads'])
			cifsWrites = self.SNMPGET(self.OID['CIFS_Writes'])
			cifsLocks = self.SNMPGET(self.OID['CIFS_Locks'])
			cifsOpens = self.SNMPGET(self.OID['CIFS_Opens'])
			cifsDirOps = self.SNMPGET(self.OID['CIFS_DirOps'])
			cifsOthers = self.SNMPGET(self.OID['CIFS_Others'])

			returncode = self.RETURNCODE['OK']
			output = 'CIFS statistics'
			perfdata = []
			perfdata.append({'label':'nacifs_totalcalls', 'value':cifsTotalCalls, 'unit':'c', 'min':'0'})
			perfdata.append({'label':'nacifs_badcalls', 'value':cifsBadCalls, 'unit':'c', 'min':'0'})
			perfdata.append({'label':'nacifs_getattrs', 'value':cifsGetAttrs, 'unit':'c', 'min':'0'})
			perfdata.append({'label':'nacifs_reads', 'value':cifsReads, 'unit':'c', 'min':'0'})
			perfdata.append({'label':'nacifs_writes', 'value':cifsWrites, 'unit':'c', 'min':'0'})
			perfdata.append({'label':'nacifs_locks', 'value':cifsLocks, 'unit':'c', 'min':'0'})
			perfdata.append({'label':'nacifs_opens', 'value':cifsOpens, 'unit':'c', 'min':'0'})
			perfdata.append({'label':'nacifs_dirops', 'value':cifsDirOps, 'unit':'c', 'min':'0'})
			perfdata.append({'label':'nacifs_others', 'value':cifsOthers, 'unit':'c', 'min':'0'})

		else:
			returncode = self.RETURNCODE['UNKNOWN']
			output = 'Unknown CIFS check/target: "%s"' % target
			perfdata = []

		return self.remember_check('cifs', returncode, output, perfdata=perfdata, target=target)


	def check_cp(self):
		cp = self.SNMPWALK(self.OID['CP'])
		output = 'Consistency Point (in progress %s seconds), Ops: Total(%s) ' % (float(cp[0])/100, cp[7])
		output += 'Snapshot(%s) LowWaterMark(%s) HighWaterMark(%s) LogFull(%s) CP-b2b(%s) ' % tuple(cp[2:7])
		output += 'Flush(%s) Sync(%s) LowVBuf(%s) CpDeferred(%s) LowDatavecs(%s)' % tuple(cp[8:13])
		returncode = self.RETURNCODE['OK']
		perfdata = []
		perfdata.append({'label':'nacp_progress', 'value':float(cp[0])/100, 'unit':'s'})
		perfdata.append({'label':'nacp_total', 'value':cp[7], 'unit':'c'})
		perfdata.append({'label':'nacp_snapshot', 'value':cp[2], 'unit':'c'})
		perfdata.append({'label':'nacp_lowwatermark', 'value':cp[3], 'unit':'c'})
		perfdata.append({'label':'nacp_highwatermark', 'value':cp[4], 'unit':'c'})
		perfdata.append({'label':'nacp_logfull', 'value':cp[5], 'unit':'c'})
		perfdata.append({'label':'nacp_b2b', 'value':cp[6], 'unit':'c'})
		perfdata.append({'label':'nacp_flush', 'value':cp[8], 'unit':'c'})
		perfdata.append({'label':'nacp_sync', 'value':cp[9], 'unit':'c'})
		perfdata.append({'label':'nacp_lowvbuf', 'value':cp[10], 'unit':'c'})
		perfdata.append({'label':'nacp_cpdeferred', 'value':cp[11], 'unit':'c'})
		perfdata.append({'label':'nacp_lowdatavecs', 'value':cp[12], 'unit':'c'})

		return self.remember_check('cp', returncode, output, perfdata=perfdata)


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


	def check_cluster(self):
		cl_settings = int(self.SNMPGET(self.OID['Cluster_Settings']))
		if cl_settings == 1: # notConfigured
			return self.remember_check('cluster', self.RETURNCODE['WARNING'], 'No cluster configured!')

		cl_state = int(self.SNMPGET(self.OID['Cluster_State']))
		cl_interconnectstatus = int(self.SNMPGET(self.OID['Cluster_InterconnectStatus']))

		returncode = []
		returncode.append(self.map_status_to_returncode(cl_settings, self.OWC['Cluster_Settings']))
		returncode.append(self.map_status_to_returncode(cl_state, self.OWC['Cluster_State']))
		returncode.append(self.map_status_to_returncode(cl_interconnectstatus, self.OWC['Cluster_InterconnectStatus']))
		returncode = max(returncode)

		output = 'Settings: ' + self.Status2String['Cluster_Settings'][str(cl_settings)] + ', '
		output += 'state: ' + self.Status2String['Cluster_State'][str(cl_state)] + ', '
		output += 'interconnect state: ' + self.Status2String['Cluster_InterconnectStatus'][str(cl_interconnectstatus)]

		if cl_state == 4: # cannotTakeover
			cl_cannottakeovercause = self.SNMPGET(self.OID['Cluster_CannotTakeOverCause'])
			output = 'Cannot takeover, reason: ' + self.Status2String['Cluster_CannotTakeOverCause'][cl_cannottakeovercause] + '! ' + output

		return self.remember_check('cluster', returncode, output)


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


	def check_extcache(self):
		if self.options.snmpversion in [1, '1']:
			return self.remember_check('extcache', self.RETURNCODE['UNKNOWN'], 'Need SNMP v2c/v3 for "extcache" check!',)

		ec_size = long(self.SNMPGET(self.OID['ExtCache_Size']))
		ec_usedsize = long(self.SNMPGET(self.OID['ExtCache_Usedsize']))
		ec_hits = long(self.SNMPGET(self.OID['ExtCache_Hits']))
		# ec_meta = long(self.SNMPGET(self.OID['ExtCache_MetaData']))
		ec_miss = long(self.SNMPGET(self.OID['ExtCache_Misses']))
		ec_evict = long(self.SNMPGET(self.OID['ExtCache_Evicts']))
		ec_inval = long(self.SNMPGET(self.OID['ExtCache_Invalidates']))
		ec_insert = long(self.SNMPGET(self.OID['ExtCache_Inserts']))

		ec_usage = float(ec_usedsize) / float(ec_size) * 100.0
		ec_hitpct = float(ec_hits) / float(ec_hits + ec_miss) * 100.0
		ec_size_human = self.value_to_human_binary(ec_size, unit='B')

		output = 'Cache size %s, cache usage %5.2f%%, total hits %5.2f%% ' % (ec_size_human, ec_usage, ec_hitpct)
		returncode = self.RETURNCODE['OK']
		perfdata = []
		perfdata.append({'label':'nacache_usage', 'value':float('%5.2f' % ec_usage), 'unit':'%'})
		perfdata.append({'label':'nacache_hits', 'value':ec_hits, 'unit':'c'})
		perfdata.append({'label':'nacache_miss', 'value':ec_miss, 'unit':'c'})
		perfdata.append({'label':'nacache_evict', 'value':ec_evict, 'unit':'c'})
		perfdata.append({'label':'nacache_inval', 'value':ec_inval, 'unit':'c'})
		perfdata.append({'label':'nacache_insert', 'value':ec_insert, 'unit':'c'})

		return self.remember_check('extcache', returncode, output, perfdata=perfdata)


	def check_extcache_info(self):
		ec_type = self.SNMPGET(self.OID['ExtCache_Type'])
		ec_subtype = self.SNMPGET(self.OID['ExtCache_SubType'])
		ec_size = long(self.SNMPGET(self.OID['ExtCache_Size']))
		ec_options = self.SNMPGET(self.OID['ExtCache_Options'])

		ec_size_human = self.value_to_human_binary(ec_size, unit='B')

		output = 'Cache type: "' + ec_type + '/' + ec_subtype + '", size: ' + ec_size_human + ', options: "' + ec_options + '"'
		returncode = 0

		return self.remember_check('extcache_info', returncode, output)


	def check_global(self):
		model = self.SNMPGET(self.OID['Model'])
		globalstatus = int(self.SNMPGET(self.OID['Global_Status']))
		globalstatusmsg = self.SNMPGET(self.OID['Global_Status_Message'])[:255]

		returncode = self.map_status_to_returncode(globalstatus, self.OWC['Global_Status'])
		output = model + ': ' + globalstatusmsg

		return self.remember_check('global', returncode, output)


	def check_ifstat(self, nic):
		idx = self.find_in_table(self.OID['Net_ifIndex'], self.OID['Net_ifDescr'] , nic)

		if idx == None:
			return self.remember_check('ifstat:'+nic, self.RETURNCODE['UNKNOWN'], 'NIC "' + nic + '" not found!')

		n_bytes_in = self.SNMPGET(self.OID['Net_InBytes'], idx)
		n_bytes_out = self.SNMPGET(self.OID['Net_OutBytes'], idx)
		n_discards_in = self.SNMPGET(self.OID['Net_InDiscards'], idx)
		n_discards_out = self.SNMPGET(self.OID['Net_OutDiscards'], idx)
		n_errors_in = self.SNMPGET(self.OID['Net_InErrors'], idx)
		n_errors_out = self.SNMPGET(self.OID['Net_OutErrors'], idx)

		returncode = self.RETURNCODE['OK']
		output = 'Network statistics for %s' % nic
		perfdata = []
		perfdata.append({'label':'naifbyin_'+nic, 'value':n_bytes_in, 'unit':'c'})
		perfdata.append({'label':'naifbyout_'+nic, 'value':n_bytes_out, 'unit':'c'})
		perfdata.append({'label':'naifdiscin_'+nic, 'value':n_discards_in, 'unit':'c'})
		perfdata.append({'label':'naifdiscout_'+nic, 'value':n_discards_out, 'unit':'c'})
		perfdata.append({'label':'naiferrin_'+nic, 'value':n_errors_in, 'unit':'c'})
		perfdata.append({'label':'naiferrout_'+nic, 'value':n_errors_out, 'unit':'c'})

		return self.remember_check('ifstat:'+nic, returncode, output, perfdata=perfdata)


	def check_io(self):
		disk_read = self.SNMPGET(self.OID['IO_DiskReadBy'])
		disk_write = self.SNMPGET(self.OID['IO_DiskWriteBy'])
		net_in = self.SNMPGET(self.OID['IO_NetInBy'])
		net_out = self.SNMPGET(self.OID['IO_NetOutBy'])
		tape_read = self.SNMPGET(self.OID['IO_TapeReadBy'])
		tape_write = self.SNMPGET(self.OID['IO_TapeWriteBy'])
		fcp_read = self.SNMPGET(self.OID['IO_FCPReadBy'])
		fcp_write = self.SNMPGET(self.OID['IO_FCPWriteBy'])
		iscsi_read = self.SNMPGET(self.OID['IO_iSCSIReadBy'])
		iscsi_write = self.SNMPGET(self.OID['IO_iSCSIWriteBy'])

		output = 'I/O statistics'
		returncode = self.RETURNCODE['OK']
		perfdata = []
		perfdata.append({'label':'naio_netin', 'value':net_in, 'unit':'c'})
		perfdata.append({'label':'naio_netout', 'value':net_out, 'unit':'c'})
		perfdata.append({'label':'naio_diskread', 'value':disk_read, 'unit':'c'})
		perfdata.append({'label':'naio_diskwrite', 'value':disk_write, 'unit':'c'})
		perfdata.append({'label':'naio_taperead', 'value':tape_read, 'unit':'c'})
		perfdata.append({'label':'naio_tapewrite', 'value':tape_write, 'unit':'c'})
		perfdata.append({'label':'naio_fcpread', 'value':fcp_read, 'unit':'c'})
		perfdata.append({'label':'naio_fcpwrite', 'value':fcp_write, 'unit':'c'})
		perfdata.append({'label':'naio_iscsiread', 'value':iscsi_read, 'unit':'c'})
		perfdata.append({'label':'naio_iscsiwrite', 'value':iscsi_write, 'unit':'c'})

		return self.remember_check('io', returncode, output, perfdata=perfdata)


	def check_nvram(self):
		nvramstatus = int(self.SNMPGET(self.OID['NVRAM_Status']))

		returncode = self.map_status_to_returncode(nvramstatus, self.OWC['NVRAM_Status'])
		output = 'NVRAM battery status is "' + self.Status2String['NVRAM_Status'].get(str(nvramstatus)) + '"'

		return self.remember_check('nvram', returncode, output)


	def check_ops(self):
		ops_nfs = self.SNMPGET(self.OID['OPs_NFS'])
		ops_cifs = self.SNMPGET(self.OID['OPs_CIFS'])
		ops_http = self.SNMPGET(self.OID['OPs_HTTP'])
		ops_fcp = self.SNMPGET(self.OID['OPs_FCP'])
		ops_iscsi = self.SNMPGET(self.OID['OPs_iSCSI'])

		output = 'Total ops statistics'
		returncode = self.RETURNCODE['OK']
		perfdata = []
		perfdata.append({'label':'naops_nfs', 'value':ops_nfs, 'unit':'c'})
		perfdata.append({'label':'naops_cifs', 'value':ops_cifs, 'unit':'c'})
		perfdata.append({'label':'naops_http', 'value':ops_http, 'unit':'c'})
		perfdata.append({'label':'naops_fcp', 'value':ops_fcp, 'unit':'c'})
		perfdata.append({'label':'naops_iscsi', 'value':ops_iscsi, 'unit':'c'})

		return self.remember_check('ops', returncode, output, perfdata=perfdata)


	def common_sm_sv(self, what, idx, **kwa):
		if not 'lag' in kwa:
			kwa['lag'] = long(self.SNMPGET(self.OID[what+'_Lag'], idx)) / 100
		if not 'rc_lag' in kwa:
			kwa['rc_lag'] = self.value_wc_to_returncode(kwa['lag'], kwa['warn'], kwa['crit'])
		if not 'state' in kwa:
			kwa['state'] = int(self.SNMPGET(self.OID[what+'_State'], idx))
		if not 'rc_state' in kwa:
			kwa['rc_state'] = self.map_status_to_returncode(int(kwa['state']), self.OWC[what+'_State'])
		if not 'src' in kwa:
			kwa['src'] = self.SNMPGET(self.OID[what+'_Src'], idx)
		if not 'dst' in kwa:
			kwa['dst'] = self.SNMPGET(self.OID[what+'_Dst'], idx)
		if not 'status' in kwa:
			kwa['status'] = int(self.SNMPGET(self.OID[what+'_Status'], idx))

		returncode = self.max_returncode([kwa['rc_state'], kwa['rc_lag']])

		if kwa['rc_lag'] in [1,2]:
			max_lag = [None, kwa['warn'], kwa['crit']][kwa['rc_lag']]
			output = 'Lag too high (%s (%s) > %s (%s))! ' % (kwa['lag'], self.seconds_to_hms(kwa['lag']), max_lag, self.seconds_to_hms(max_lag))
		else:
			output = ''

		output += 'Source: "' + kwa['src'] + '", Destination: "' + kwa['dst'] + '", '
		output += 'State: ' + self.Status2String[what+'_State'].get(str(kwa['state'])) + ', '
		output += 'Status: ' + self.Status2String[what+'_Status'].get(str(kwa['status']))

		return (returncode, output)


	def check_sm_sv_all(self, what, target, warn, crit):
		verbose = 'VERB' in target
		debug = 'DEBUG' in target

		tagtarget = what.lower() + ':ALL'

		idxs = self.SNMPWALK(self.OID[what+'_Index'])
		lags = self.SNMPWALK(self.OID[what+'_Lag'])
		for i in xrange(0, len(lags)):
			lags[i] = long(lags[i]) / 100
		states = self.SNMPWALK(self.OID[what+'_State'])

		rcs_lag = []
		for lag in lags:
			rcs_lag.append(self.value_wc_to_returncode(lag, warn, crit))
		rcs_state = []
		for state in states:
			rcs_state.append(self.map_status_to_returncode(int(state), self.OWC[what+'_State']))

		rc_lag = self.max_returncode(rcs_lag)
		rc_state = self.max_returncode(rcs_state)

		returncode = self.max_returncode([rc_lag, rc_state])

		if returncode == self.RETURNCODE['OK'] and not debug:
			return self.remember_check(tagtarget, returncode, 'All ' + what + ' OK')

		srcs = self.SNMPWALK(self.OID[what+'_Src'])
		dsts = self.SNMPWALK(self.OID[what+'_Dst'])
		statuss = self.SNMPWALK(self.OID[what+'_Status'])

		if not( len(idxs) == len(lags) == len(states) == len(srcs) == len(dsts) == len(statuss) ):
			return self.remember_check(tagtarget, returncode, 'Wrong number of status informations, but sure an error!')

		output = []

		for i in xrange(0, len(idxs)):
			if rcs_lag[i] != self.RETURNCODE['OK'] or rcs_state != self.RETURNCODE['OK'] or (verbose or debug):
				(rc_thissv, output_thissv) = self.common_sm_sv(what, idxs[i], src=srcs[i], dst=dsts[i], lag=lags[i], state=states[i], status=statuss[i], rc_lag=rcs_lag[i], rc_state=rcs_state[i], warn=warn, crit=crit)

				if rc_thissv != self.RETURNCODE['OK'] or debug:
					output.append(output_thissv)

		output = ' / '.join(output)
		return self.remember_check(tagtarget, returncode, output)


	def check_sm_sv_one(self, what, target, warn, crit):
		idx = self.find_in_table(self.OID[what+'_Index'], self.OID[what+'_Src'], target)
		if idx == None:
			idx = self.find_in_table(self.OID[what+'_Index'], self.OID[what+'_Dst'], target)

		if idx == None:
			return self.remember_check(what.lower(), self.RETURNCODE['UNKNOWN'], 'No ' + what + ' with source or destination "' + target + '" found!')

		(returncode, output) = self.common_sm_sv(what, idx, warn=warn, crit=crit)

		return self.remember_check(what.lower() + ':' + target, returncode, output)


	def check_snapmirror(self, target, warn, crit):
		if self.SNMPGET(self.OID['Snapmirror_License']) != '2':
			return self.remember_check('snapmirror', self.RETURNCODE['CRITICAL'], 'No license for Snapmirror')

		if self.SNMPGET(self.OID['Snapmirror_On']) != '2':
			return self.remember_check('snapmirror', self.RETURNCODE['CRITICAL'], 'Snapmirror is turned off!')

		if not target:
			return self.remember_check('snapmirror', self.RETURNCODE['OK'], 'Snapmirror is turned on!')

		if target.startswith('ALL'):
			return self.check_sm_sv_all('Snapmirror', target, warn, crit)
		else:
			return self.check_sm_sv_one('Snapmirror', target, warn, crit)


	def check_snapvault(self, target, warn, crit):
		if self.SNMPGET(self.OID['Snapvault_LicensePrimary']) != '2' and self.SNMPGET(self.OID['Snapvault_LicenseSecondary']) != '2':
			return self.remember_check('snapvault', self.RETURNCODE['CRITICAL'], 'No license for Snapvault')

		if self.SNMPGET(self.OID['Snapvault_On']) != '2':
			return self.remember_check('snapvault', self.RETURNCODE['CRITICAL'], 'Snapvault is turned off!')

		if not target:
			return self.remember_check('snapvault', self.RETURNCODE['OK'], 'Snapvault is turned on!')

		if target.startswith('ALL'):
			return self.check_sm_sv_all('Snapvault', target, warn, crit)
		else:
			return self.check_sm_sv_one('Snapvault', target, warn, crit)


	def check_version(self):
		model = self.SNMPGET(self.OID['Model'])
		ontapversion = self.SNMPGET(self.OID['ONTAP_Version'])

		return self.remember_check('version', 0, model + ': ' + ontapversion)


	def common_vol_idx(self, volume):
		if volume.endswith('.snapshot') or volume.endswith('.snapshot/'):
			return (None, None)

		idx = self.find_in_table(self.OID['df_FS_Index'], self.OID['df_FS_Name'] , volume)

		if idx == None:
			# Retry without/with Slash
			if volume[-1] == '/':
				idx = self.find_in_table(self.OID['df_FS_Index'], self.OID['df_FS_Name'] , volume[:-1])
			else:
				idx = self.find_in_table(self.OID['df_FS_Index'], self.OID['df_FS_Name'] , volume + '/')

		if idx != None:
			sn_idx = int(idx) + 1
			sn_name = self.SNMPGET(self.OID['df_FS_Name'], sn_idx)
			if not (sn_name.endswith('.snapshot') or sn_name.endswith('.snapshot/')):
				sn_idx = None
		else:
			sn_idx = None

		return (idx, sn_idx)


	def common_vol_shorten_target(self, target):
		target = target.replace('/vol/', '')
		if target[-1] == "/":
			target = target[:-1]

		return target


	def check_vol_data_one(self, volume, warn, crit):
		(idx, sn_idx) = self.common_vol_idx(volume)

		if idx == None:
			return self.remember_check('vol_data', self.RETURNCODE['UNKNOWN'], '"' + volume + '" not found!')

		fs_total = long(self.SNMPGET(self.OID['df_FS_kBTotal'], idx)) * 1024L
		fs_used = long(self.SNMPGET(self.OID['df_FS_kBUsed'], idx)) * 1024L
		# fs_avail = long(self.SNMPGET(self.OID['df_FS_kBAvail'], idx)) * 1024L
		if sn_idx != None:
			sn_total = long(self.SNMPGET(self.OID['df_FS_kBTotal'], sn_idx)) * 1024L
			sn_used = long(self.SNMPGET(self.OID['df_FS_kBUsed'], sn_idx)) * 1024L
			# sn_avail = long(self.SNMPGET(self.OID['df_FS_kBAvail'], sn_idx)) * 1024L
		else:
			sn_total = 0L
			sn_used = 0L
			# sn_avail = 0L

		mountedon = self.SNMPGET(self.OID['df_FS_Mounted_On'] + "." + idx)
		status = self.Status2String['df_FS_Status'].get(self.SNMPGET(self.OID['df_FS_Status'] + "." + idx))
		fstype = self.Status2String['df_FS_Type'].get(self.SNMPGET(self.OID['df_FS_Type'] + "." + idx))

		fs_pctused = float(fs_used) / float(fs_total) * 100.0

		warn = self.range_dehumanize(warn, fs_total, unit=['b',])
		crit = self.range_dehumanize(crit, fs_total, unit=['b',])

		returncode = self.value_wc_to_returncode(fs_used, warn, crit)
		output = volume + ': Used ' + self.value_to_human_binary(fs_used, 'B')
		output += ' (' + '%3.1f' % fs_pctused + '%)'+ ' out of ' + self.value_to_human_binary(fs_total, 'B')
		target = self.common_vol_shorten_target(volume)
		perfdata = []
		perfdata.append({'label':'navdu_' + target, 'value':fs_used, 'unit':'B', 'warn':warn, 'crit':crit, 'min':0})
		perfdata.append({'label':'navdt_' + target, 'value':fs_total, 'unit':'B'})
		perfdata.append({'label':'navsu_' + target, 'value':sn_used, 'unit':'B', 'min':0})
		perfdata.append({'label':'navst_' + target, 'value':sn_total, 'unit':'B'})

		return self.remember_check('vol_data', returncode, output, perfdata=perfdata, target=target)


	def check_vol_data(self, volume, warn, crit):
		if volume.startswith('ALL'):
			volumes = self.SNMPWALK(self.OID['df_FS_Name'])
			for vol in volumes:
				if vol.endswith('.snapshot') or vol.endswith('.snapshot/'):
					continue

				self.check_vol_data_one(vol, warn, crit)
		else:
			return self.check_vol_data_one(volume, warn, crit)


	def check_vol_snap_one(self, volume, warn, crit):
		(idx, sn_idx) = self.common_vol_idx(volume)

		if idx == None:
			return self.remember_check('vol_snap', self.RETURNCODE['UNKNOWN'], '"' + volume + '" not found!')

		# fs_total = long(self.SNMPGET(self.OID['df_FS_kBTotal'], idx)) * 1024L
		# fs_used = long(self.SNMPGET(self.OID['df_FS_kBUsed'], idx)) * 1024L
		# fs_avail = long(self.SNMPGET(self.OID['df_FS_kBAvail'], idx)) * 1024L
		if sn_idx != None:
			sn_total = long(self.SNMPGET(self.OID['df_FS_kBTotal'], sn_idx)) * 1024L
			sn_used = long(self.SNMPGET(self.OID['df_FS_kBUsed'], sn_idx)) * 1024L
			# sn_avail = long(self.SNMPGET(self.OID['df_FS_kBAvail'], sn_idx)) * 1024L
		else:
			sn_total = 0L
			sn_used = 0L
			# sn_avail = 0L

		warn = self.range_dehumanize(warn, sn_total, unit=['b',])
		crit = self.range_dehumanize(crit, sn_total, unit=['b',])
		if sn_total != 0:
			# Snap reserve
			sn_pctused = float(sn_used) / float(sn_total) * 100.0
		else:
			# No snap reserve
			sn_pctused = 0.0

		returncode = self.value_wc_to_returncode(sn_used, warn, crit)
		output = volume + '.snapshot: Used ' + self.value_to_human_binary(sn_used, 'B')
		output += ' (' + '%3.1f' % sn_pctused + '%)'+ ' out of ' + self.value_to_human_binary(sn_total, 'B')
		target = self.common_vol_shorten_target(volume)
		perfdata = []
		perfdata.append({'label':'navsu_' + target, 'value':sn_used, 'unit':'B', 'warn':warn, 'crit':crit, 'min':0})
		perfdata.append({'label':'navst_' + target, 'value':sn_total, 'unit':'B'})

		return self.remember_check('vol_snap', returncode, output, perfdata=perfdata, target=target)


	def check_vol_snap(self, volume, warn, crit):
		if volume.startswith('ALL'):
			volumes = self.SNMPWALK(self.OID['df_FS_Name'])
			for vol in volumes:
				if vol.endswith('.snapshot') or vol.endswith('.snapshot/'):
					continue

				self.check_vol_snap_one(vol, warn, crit)
		else:
			return self.check_vol_snap_one(volume, warn, crit)


	def check_vol_inode_one(self, volume, warn, crit):
		(idx, sn_idx) = self.common_vol_idx(volume)

		if idx == None:
			return self.remember_check('vol_inode', self.RETURNCODE['UNKNOWN'], '"' + volume + '" not found!')

		in_used = long(self.SNMPGET(self.OID['df_FS_INodeUsed'] + '.' + idx))
		in_free = long(self.SNMPGET(self.OID['df_FS_INodeFree'] + '.' + idx))
		in_total = in_used + in_free

		in_pctused = float(in_used) / float(in_total) * 100.0

		warn = self.range_dehumanize(warn, in_total)
		crit = self.range_dehumanize(crit, in_total)

		returncode = self.value_wc_to_returncode(in_used, warn, crit)
		output = volume + ': Used inodes ' + self.value_to_human_si(in_used)
		output += ' (' + '%3.1f' % in_pctused + '%)'+ ' out of ' + self.value_to_human_si(in_total)
		target = self.common_vol_shorten_target(volume)
		perfdata = []
		perfdata.append({'label':'naviu_' + target, 'value':in_used, 'unit':None, 'warn':warn, 'crit':crit, 'min':0})
		perfdata.append({'label':'navit_' + target, 'value':in_total, 'unit':None})

		return self.remember_check('vol_inode', returncode, output, perfdata=perfdata, target=target)


	def check_vol_inode(self, volume, warn, crit):
		if volume.startswith('ALL'):
			volumes = self.SNMPWALK(self.OID['df_FS_Name'])
			for vol in volumes:
				if vol.endswith('.snapshot') or vol.endswith('.snapshot/'):
					continue

				self.check_vol_inode_one(vol, warn, crit)
		else:
			return self.check_vol_inode_one(volume, warn, crit)


	def check_vol_files_one(self, volume, warn, crit):
		(idx, sn_idx) = self.common_vol_idx(volume)

		if idx == None:
			return self.remember_check('vol_files', self.RETURNCODE['UNKNOWN'], '"' + volume + '" not found!')

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
		target = self.common_vol_shorten_target(volume)
		perfdata = []
		perfdata.append({'label':'navfu_' + target, 'value':fi_used, 'unit':None, 'warn':warn, 'crit':crit, 'min':0})
		perfdata.append({'label':'navft_' + target, 'value':fi_total, 'unit':None})

		return self.remember_check('vol_files', returncode, output, perfdata=perfdata, target=target)


	def check_vol_files(self, volume, warn, crit):
		if volume.startswith('ALL'):
			volumes = self.SNMPWALK(self.OID['df_FS_Name'])
			for vol in volumes:
				if vol.endswith('.snapshot') or vol.endswith('.snapshot/'):
					continue

				self.check_vol_files_one(vol, warn, crit)
		else:
			return self.check_vol_files_one(volume, warn, crit)






def main():
	plugin = CheckNAF(pluginname='check_naf', tagforstatusline='NAF', description=u'Monitoring NetApp(tm) FAS systems', version='0.9')

	plugin.add_cmdlineoption('', '--separator', 'separator', 'Separator for check/target/warn/crit', metavar=',', default=',')
	plugin.add_cmdlineoption('', '--subseparator', 'subseparator', 'Separator for multiple checks or targets', metavar='+', default='+')

	plugin.add_cmdlineoption('', '--check', 'check', 'OBSOLETE - use new syntax!', default='')
	plugin.add_cmdlineoption('', '--target', 'target', 'OBSOLETE - use new syntax!', default='')
	plugin.add_cmdlineoption('-w', '', 'warn', 'OBSOLETE - use new syntax!', default='')
	plugin.add_cmdlineoption('-c', '', 'crit', 'OBSOLETE - use new syntax!', default='')

	plugin.add_cmdlineoption('', '--snmpwalk', 'snmpwalkoid', 'DEBUG: "list" OIDs or SNMPWALK it', default=None)

	plugin.parse_cmdlineoptions()

	plugin.prepare_snmp()

	if plugin.options.snmpwalkoid != None:
		if not plugin.options.snmpwalkoid in plugin.OID:
			print 'List of OIDs:'
			oids = plugin.OID.keys()
			oids.sort()
			for key in oids:
				print '- %s' % key
			sys.exit(0)

		print 'Walking "%s"...' % plugin.options.snmpwalkoid
		result = plugin.SNMPWALK(plugin.OID[plugin.options.snmpwalkoid], exitonerror=False)
		if result == None:
			result = plugin.SNMPGET(plugin.OID[plugin.options.snmpwalkoid], exitonerror=False)
		for value in result:
			print '=> %s' % value
		sys.exit(0)


	if plugin.options.check or plugin.options.target:
		arguments = plugin.options.check
		for s in [plugin.options.target, plugin.options.warn, plugin.options.crit]:
			arguments += plugin.options.separator + s
		plugin.back2nagios(3, 'Obsolete syntax - please use new syntax: "%s %s"' % (sys.argv[0], arguments))


	checks = []

	for quad in plugin.args:
		quad = quad.split(plugin.options.separator)
		quad = (quad + ['', '', ''])[:4] # Fix length to 4, fill with ''

		# Convert list of checks to list
		if plugin.options.subseparator in quad[0]:
			quad[0] = quad[0].split(plugin.options.subseparator)
		else:
			quad[0] = [quad[0],]

		# Convert list of targets to list
		if plugin.options.subseparator in quad[1]:
			quad[1] = quad[1].split(plugin.options.subseparator)
		else:
			quad[1] = [quad[1],]

		for target in quad[1]:
			for check in quad[0]:
				checks.append(tuple([check, target, quad[2], quad[3]]))

	if len(checks) == 0:
		checks = [('global','','','')]

	for quad in checks:
		(check, target, warn, crit) = tuple(quad)

		if check == 'global' or check == 'environment':
			result = plugin.check_global()
		elif check == 'cluster':
			result = plugin.check_cluster()
		elif check == 'cifs':
			result = plugin.check_cifs(target=target, warn=warn, crit=crit)
		elif check == 'cp':
			result = plugin.check_cp()
		elif check == 'cpu':
			result = plugin.check_cpu(warn=warn, crit=crit)
		elif check == 'disk':
			result = plugin.check_disk(target=target, warn=warn, crit=crit)
		elif check == 'extcache':
			result = plugin.check_extcache()
		elif check == 'extcache_info':
			result = plugin.check_extcache_info()
		elif check == 'ifstat':
			result = plugin.check_ifstat(target)
		elif check == 'io':
			result = plugin.check_io()
		elif check == 'nvram':
			result = plugin.check_nvram()
		elif check == 'ops':
			result = plugin.check_ops()
		elif check == 'snapmirror':
			result = plugin.check_snapmirror(target, warn=warn, crit=crit)
		elif check == 'snapvault':
			result = plugin.check_snapvault(target, warn=warn, crit=crit)
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
		else:
			result = plugin.remember_check(check, plugin.RETURNCODE['UNKNOWN'], 'Unknown check "' + check + '"!')


	# from pprint import pprint
	# pprint(plugin.dump_brain())

	plugin.brain2output()
	plugin.exit()

if __name__ == '__main__':
	main()

#vim: ts=4 sw=4 foldmethod=indent
