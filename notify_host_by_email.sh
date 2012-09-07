#! /bin/bash
#
# Nagios host notification script.
#
# Copyright (C) 2012 Sebastian 'tokkee' Harl <sh@teamix.net>
#                    and teamix GmbH, Nuernberg, Germany
#
# This file is part of "teamix Monitoring Plugins"
# URL: http://oss.teamix.org/projects/monitoringplugins/
#
# This file is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License,
# or (at your option) any later version.
#
# This file is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file. If not, see <http://www.gnu.org/licenses/>.

#
# Sample command line:
# notify_host_by_email.sh -T '$NOTIFICATIONTYPE$' -H '$HOSTNAME$' \
#                         -a '$HOSTALIAS$' -A '$HOSTADDRESS$' \
#                         -s '$HOSTSTATE$' \
#                         -o '$HOSTOUTPUT$' -O '$LONGHOSTOUTPUT$' \
#                         -P '$HOSTPERFDATA$' -D '$LONGDATETIME$' \
#                         -E '$CONTACTEMAIL$'
#

NOTIFICATIONTYPE="UNKNOWN"

HOSTNAME="unknown host"
HOSTALIAS=""
HOSTADDRESS=""
HOSTSTATE="UNKNOWN"
HOSTOUTPUT=""
LONGHOSTOUTPUT=""
HOSTPERFDATA=""

LONGDATETIME=`date`

CONTACTEMAIL=""

GETOPT=$( getopt -o T:H:a:A:s:o:O:P:D:E: \
	--long type,hostname,alias,address,state,output,longoutput,perfdata,datetime,email \
	-n 'notify_host_by_email' -- "$@" )

if test $? -ne 0; then
	echo 'Failed to parse command line options!' >&2
	exit 1
fi

eval set -- "$GETOPT"

while true; do
	case "$1" in
		-T|--type)
			NOTIFICATIONTYPE="$2"
			shift 2
			;;
		-H|--hostname)
			HOSTNAME="$2"
			shift 2
			;;
		-a|--alias)
			HOSTALIAS="$2"
			shift 2
			;;
		-A|--address)
			HOSTADDRESS="$2"
			shift 2
			;;
		-s|--state)
			HOSTSTATE="$2"
			shift 2
			;;
		-o|--output)
			HOSTOUTPUT="$2"
			shift 2
			;;
		-O|--longoutput)
			LONGHOSTOUTPUT="$2"
			shift 2
			;;
		-P|--perfdata)
			HOSTPERFDATA="$2"
			shift 2
			;;
		-D|--datetime)
			LONGDATETIME="$2"
			shift 2
			;;
		-E|--email)
			CONTACTEMAIL="$2"
			shift 2
			;;
		--)
			shift
			break
			;;
	esac
done

if test -z "$CONTACTEMAIL"; then
	echo 'Missing contact email!' >&2
	exit 1
fi

EMAIL=$( mktemp -t )
trap "rm -f $EMAIL" EXIT

function email_append() {
	/usr/bin/printf "%b" "$@" "\n" >> $EMAIL
}

cat <<EOF > $EMAIL
***** Nagios *****

Notification Type: $NOTIFICATIONTYPE

Host: $HOSTNAME ($HOSTALIAS)
EOF

if test -n "$HOSTADDRESS"; then
	email_append "Address: $HOSTADDRESS"
fi

email_append "State: $HOSTSTATE"
if test -n "$HOSTOUTPUT"; then
	email_append "Info: $HOSTOUTPUT"
fi

email_append ""
email_append "Date/Time: $LONGDATETIME"

if test -n "$LONGHOSTOUTPUT"; then
	email_append ""
	email_append "Additional Info:"
	email_append ""
	email_append "$LONGHOSTOUTPUT"
fi

if test -n "$HOSTPERFDATA"; then
	email_append ""
	email_append "Performance Data:"
	email_append ""
	email_append "$HOSTPERFDATA"
fi

cat $EMAIL | /usr/bin/mail -s "** $NOTIFICATIONTYPE Host Alert: $HOSTNAME is $HOSTSTATE **" $CONTACTEMAIL

