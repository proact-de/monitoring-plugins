#!/usr/bin/python

from monitoringplugin import MonitoringPlugin

import fcntl
import socket
import struct

def get_ipv4_address(iface):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(sock.fileno(), 0x8915, struct.pack('256s', iface[:15]))[20:24])


plugin = MonitoringPlugin(pluginname='check_iface-dns', tagforstatusline='IFACE-DNS', description='Check interface address vs. DNS', version='0.1')

plugin.add_cmdlineoption('-i', '', 'iface', 'Interface to get IP from', default='lo')
plugin.add_cmdlineoption('-d', '', 'dns', 'DNS object(s) to check, comma separated list', default='localhost')
#plugin.add_cmdlineoption('-4', '', 'v4', 'Use IPv4', action='store_true')
#plugin.add_cmdlineoption('-6', '', 'v6', 'Use IPv6', action='store_true')

plugin.parse_cmdlineoptions()

#if not plugin.options.v4 and not plugin.options.v6:
#	plugin.options.v4 = True
#
#if plugin.options.v4:
#	plugin.verbose(1, 'Using IPv4')
#
#if plugin.options.v6:
#	plugin.verbose(1, 'Using IPv6')


# Get IP from interface
try:
	ip_iface = get_ipv4_address(plugin.options.iface)
except IOError, (errno, strerror):
	if errno == 19:
		plugin.back2nagios(2, 'Interface "%s" does not exist!' % plugin.options.iface)
	elif errno == 99:
		plugin.back2nagios(2, 'Interface "%s" has no IP!' % plugin.options.iface)

	plugin.back2nagios(2, 'I/O error(%s): %s, interface "%s"' % (errno, strerror, plugin.options.iface))

plugin.verbose(1, 'Found IP "%s" on interface "%s"' % (ip_iface, plugin.options.iface))

# Get IP(s) from DNS
if not ',' in plugin.options.dns:
	# Only one DNS object
	try:
		ip_dns = socket.gethostbyname(plugin.options.dns)
	except socket.gaierror:
		ip_dns = None
		plugin.back2nagios(1, 'Could not find "%s" in DNS!' % plugin.options.dns)

	if ip_iface == ip_dns:
		plugin.back2nagios(0, 'Found %s for "%s" in DNS and on interface "%s"' % (ip_dns, plugin.options.dns, plugin.options.iface))
	else:
		plugin.back2nagios(2, 'Found %s for "%s" in DNS, but %s for interface "%s"' % (ip_dns, plugin.options.dns, ip_iface, plugin.options.iface))

else:
	# Multiple DNS objects
	plugin.add_returncode(0)
	failed_dns = []

	for dns in plugin.options.dns.split(','):
		try:
			ip_dns = socket.gethostbyname(dns)
		except socket.gaierror:
			ip_dns = None

		if ip_dns:
			plugin.verbose(1, 'Found IP "%s" as DNS object "%s"' % (ip_dns, dns))
		else:
			plugin.verbose(1, 'Did not find IP for "%s"' % dns)

		if ip_iface != ip_dns:
			plugin.add_multilineoutput('CRITICAL - "%s" has unexpected IP "%s"' % (dns, ip_dns))
			failed_dns.append(dns)
		else:
			plugin.add_multilineoutput('OK - "%s" resolves to "%s"' % (dns, ip_dns))

		
	if len(failed_dns) == 0:
		plugin.add_returncode(0)
		plugin.add_output('All DNS objects have a correct IP')
	else:
		plugin.add_returncode(2)
		plugin.add_output('Following DNS objects did not resolve as expected: "%s"' % '", "'.join(failed_dns))

	plugin.exit()


