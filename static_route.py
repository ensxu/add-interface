#!/usr/bin/python

from ipaddress import IPv4Address, IPv4Network
from ciscoconfparse import CiscoConfParse 
from ciscoconfparse.ccp_util import IPv4Obj
#from ciscoconfparse.ccp_util import str

#for printing ping commands
print_ping = 0

#define interface array with interface name and ip address
interface_array = []

#define ping destination address with source of interface array
ping_dest_ip_with_interface = []

#define match ip route with interface array
match_with_interface = []

#define no matchip route with interface array
no_match_with_interface = []

#counting of lines for later use
with open('./ip_route.txt') as ip_route_file:
	for number_of_ip_route_lines, l in enumerate(ip_route_file):
		pass
number_of_ip_route_lines = number_of_ip_route_lines + 1

 
confparse = CiscoConfParse('config.txt')

# extract the interface name and ip address
# first, we get all interface commands from the configuration without shutdown
interface_cmds = confparse.find_objects_wo_child(r'^interface ', r'shutdown')

# iterate over the resulting IOSCfgLine objects
for interface_cmd in interface_cmds:
	
	# extract IP addresses
	#IPv4_REGEX = r'ip\saddress\s(\S+\s+\S+)'
	#IPv4_REGEX = r'ip\saddress\s(.+4+\s+\.+4)'

	#print(interface_cmd)
	#This can be optimised. No time.
	IPv4_REGEX = r'ip\saddress\s(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s+\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$)'
	#IPv4_REGEX = r'ip\saddress\s1\.1\.1'

	#initial for ipv4_network
	ipv4_network = '127.0.0.1/32'

	for cmd in interface_cmd.re_search_children(IPv4_REGEX):

		#print(interface_cmd.text.strip('interface '))

		#get ipv4 address in IPv4obj format
		ipv4_addr = interface_cmd.re_match_iter_typed(IPv4_REGEX, result_type=IPv4Obj)

		ipv4_network = str(ipv4_addr.network)
		#print(interface_with_ip)

		#make interface array
		#interface_array.append(interface_with_ip)

#print(interface_array)
	#inital for vrf-name
	vrf_name = 'empty'

	VRF_REGEX = r'vrf\sforwarding\s\S+'
	for cmd in interface_cmd.re_search_children(VRF_REGEX):

		#print (interface_cmd.text)
		#get vrf name
		vrf = interface_cmd.re_match_iter_typed(VRF_REGEX, group=0, result_type=str)

		vrf_name = vrf.split(' ')[2]

		#print (vrf_name.split(' ')[3])

	#interface name with ip address, network is an attribute of IPv40obj
	#interface name is the second word of interface command. this is to avoid something like "interface atm0/1.99 point-to-point"
	interface_with_ip_vrf = (interface_cmd.text.split(' ')[1], ipv4_network, vrf_name)

	#print(interface_with_ip_vrf)

	#make interface array
	interface_array.append(interface_with_ip_vrf)


#get the number of rows of the interface array
number_of_rows = len(interface_array)

#for x in range(0, number_of_rows):
#	print(interface_array[x][0], interface_array[x][1])


with open('./ip_route.txt') as ip_route_file:

	for ip_route_lines in ip_route_file:
		#split the the ip route txt file each line into a list
		each_ip_route_line = ip_route_lines.split()
		#print(each_ip_route_line)
		
		if each_ip_route_line[2] != 'vrf':
			#destination ip address is number 5 in the list
			dest_ipaddress = each_ip_route_line[4]
			#print(dest_ipaddress)

		if each_ip_route_line[2] == 'vrf':
			#destination ip address is number 7 in the list
			dest_ipaddress = each_ip_route_line[6]
			#print(dest_ipaddress)
		
		#print(dest_ipaddress)

		#if dest_ipaddress == 'Null0':
		#	print('There is Null0 route. Fix it first')
		#	quit


		#initial for match
		match = 'false'

		#Range starts from 0 to number_of_rows
		for x in range(0, number_of_rows):
			#print (interface_array[x][1])
			#print (len(each_ip_route_line))
			#ip route without vrf

			#should be able to optimse by inserting interface name rather than reconstruct with [0]. No time.

			if each_ip_route_line[2] != 'vrf':
				#print (interface_array[x][2])
				#print (IPv4Address(dest_ipaddress), IPv4Network(interface_array[x][1]), IPv4Address(dest_ipaddress) in IPv4Network(interface_array[x][1]))
				#ip route with name at the end, check whether the destination is in the range of network of the interface
				if IPv4Address(dest_ipaddress) in IPv4Network(interface_array[x][1])  and interface_array[x][2] == 'empty':
					match = 'true'
					#print(interface_array[x][0])
					#print(each_ip_route_line)
					each_ip_route_line.insert(4, interface_array[x][0])
					ip_route_with_interface = (' '.join(each_ip_route_line))
					match_with_interface.append(ip_route_with_interface)

					#ping destination IP with interface as source
					ping_with_interface = ('ping ' + each_ip_route_line[4] + ' source ' + interface_array[x][0])
					ping_dest_ip_with_interface.append(ping_with_interface)	

			#ip route with vrf and with name at the end, and check whether the destination is in the range of network of the interface
			elif IPv4Address(dest_ipaddress) in IPv4Network(interface_array[x][1]) and interface_array[x][2] ==  each_ip_route_line[3]:
				#print (int_dest_ipaddress, interface_array[x][1], interface_array[x][0])
				match = 'true'
				
				each_ip_route_line.insert(6, interface_array[x][0])
				ip_route_with_interface = (' '.join(each_ip_route_line))
				match_with_interface.append(ip_route_with_interface)


				#ping vrf destination IP with interface as source
				ping_with_interface = ('ping vrf ' + each_ip_route_line[3] + ' ' + each_ip_route_line[6] + ' source ' + interface_array[x][0])
				ping_dest_ip_with_interface.append(ping_with_interface)	

				#ip route with no name at the end, and check whether the destination is in the range of network of the interface
				
		if match == 'false':
			no_match_with_interface.append(ip_route_lines.strip())
			#print ('No Match for ' + ip_route_lines)

	
	print ()
	print ('*****************')
	print (str(len(match_with_interface)) + ' matches')
	print ('*****************')

	for each_line in range (0, len(match_with_interface)):
		print (match_with_interface[each_line])

	
	if print_ping == 1:
		print()
		print ('*************************************')
		print ('Test with pings before pasting')
		print ('*************************************')

		for each_line in range (0, len(ping_dest_ip_with_interface)):
			print (ping_dest_ip_with_interface[each_line])

	print ()
	print ('*****************')
	print (str(len(no_match_with_interface)) + ' unmatches')
	print ('*****************')
	
	for each_line in range (0, len(no_match_with_interface)):
		print (no_match_with_interface[each_line])

	print()
	print ('************************************')
	print ('Summary:')
	print (str(number_of_ip_route_lines) + ' ip route statements')
	print ( str(len(match_with_interface)) + ' matches' + ' and ' + str(len(no_match_with_interface)) + ' unmatches')
	print ('************************************')
