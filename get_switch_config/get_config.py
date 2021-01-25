import os
import csv
from napalm import get_network_driver

path = os.getcwd()

if not (os.path.exists(path+'/switch_config')):
	os.mkdir(path+'/switch_config')

# switches.txt is something like this: IP address of switch,
# Username to log in, Password, and transport (SSH or Telnet)
# separated by ,
switch_file = open('switches.txt')

switch_detail = csv.reader(switch_file)

switch_number = len(list(switch_detail))
print('There are {} switches to get config.'.format(switch_number))

# reset file pointer to the top row
switch_file.seek(0)

count = 1

for row in switch_detail:
	switch_ip = row[0].strip()
	username = row[1].strip()
	password = row[2].strip()
	switch_transport = row[3].strip()

	# compose driver
	driver = get_network_driver('ios')
	device_optional_args = {'transport': switch_transport}
	device = driver(switch_ip, username, password, optional_args=device_optional_args)

	print('Getting config of switch: {}...'.format(switch_ip))

	# connect to routers and get config
	device.open()
	config = device.get_config()
	run_conf = config['running']

	facts = device.get_facts()
	hostname = facts['hostname']

	# write config
	file = open(path + '/switch_config/' + hostname + '.txt', 'w')
	file.write(run_conf)
	file.close()
	device.close()

	print('Switch {}: {} ({} of {}) is done.'.format(switch_ip, hostname, count, switch_number))
	count += 1

switch_file.close()
