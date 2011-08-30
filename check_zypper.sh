#!/bin/bash

#############################################################################
# (c) 2011 Sven Velt <sven@velt.de                                          #
#          and team(ix) GmbH, Nuernberg, Germany                            #
#                                                                           #
# This file is part of "team(ix) Monitoring Plugins"                        #
# URL: http://oss.teamix.org/projects/monitoringplugins/                    #
#                                                                           #
# All rights reserved.                                                      #
# Redistribution and use in source and binary forms, with or without        #
# modification, are permitted provided that the following conditions        #
# are met:                                                                  #
# 1. Redistributions of source code must retain the above copyright         #
#    notice, this list of conditions and the following disclaimer.          #
# 2. Redistributions in binary form must reproduce the above copyright      #
#    notice, this list of conditions and the following disclaimer in the    #
#    documentation and/or other materials provided with the distribution.   #
# 3. The name of the copyright owner may not be used to endorse or          #
#    promote products derived from this software without specific prior     #
#    written permission.                                                    #
#                                                                           #
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR      #
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED            #
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE    #
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,        #
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES        #
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR        #
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)        #
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,       #
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING     #
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE        #
# POSSIBILITY OF SUCH DAMAGE.                                               #
#############################################################################

# Works on:
# - SLES 11

# Does NOT work on:
# -

# From "/etc/sudoers" / "visudo":
# nagios ALL = NOPASSWD: /usr/bin/zypper ref,/usr/bin/zypper -q pchk

#
if [ ! -x /usr/bin/zypper ] ; then
	echo 'Zypper CRITICAL - Zypper not found!'
	exit 2
fi

# Refresh repositories
sudo /usr/bin/zypper ref >/dev/null 2>&1

zypper_out=$(sudo LANG=C /usr/bin/zypper -q pchk)
if ( echo "${zypper_out}" | grep -q "needed" ) ; then
	output=$(echo ${zypper_out} | cut -d "." -f 7)
	patches=$(echo ${output} | cut -d " " -f1)
	if [ ${patches} -gt 0 ] ; then
		secpatches=$(echo ${output} | cut -d "(" -f2|cut -d " " -f1)
		if [ -n "${secpatches}" ]; then
			if [ ${secpatches} -gt 0 ] ; then
				echo "Zypper CRITICAL - ${patches}"
				exit 2
			fi
			echo "Zypper WARNING - ${output}"
			exit 1
		fi
	fi
fi

echo "Zypper OK - No updates available"
exit 0
