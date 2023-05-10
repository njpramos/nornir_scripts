import getpass
from ipaddress import ip_address, ip_network
from nornir import InitNornir
from nornir_scrapli.tasks import send_command
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file="inventory/config.yaml")

password = getpass.getpass()
#ip_add = input("Enter target IP: ")

#ip_address(ip_add)

nr.inventory.defaults.password = password

ip_list = []
unreachable_list = []

def get_ip(task):
	response = task.run(task=send_command, command="show ip interface brief")
	task.host["facts"] = response.scrapli_response.genie_parse_output()
	interfaces =  task.host["facts"]["interface"]
	
	for interface in interfaces:
		if interface == "GigabitEthernet0/0":
			continue
		ip_add = interfaces[interface]["ip_address"]
		if ip_add != "unassigned":
			if interface.startswith("Loop"):		
				ip_list.append(ip_add)
				#print(interface)	
		#print(inteface)
#print(ip_addresses)

def ping_test(task):
	for ip in sorted_list:
		result = task.run(task=send_command, command=f"ping {ip}")
		response = result.result
		if not "!!!" in response:
			unreachable_list.append(f"{task.host} cannot reach {ip}")

nr.run(task=get_ip)

sorted_list = sorted(ip_list)

results = nr.run(task=ping_test)

print_result(results)

if unreachable_list:
	sorted_unreachable_list = sorted(unreachable_list)
	for i in sorted_unreachable_list:
		print(i)
else:
	print("All the hosts are reachable")
