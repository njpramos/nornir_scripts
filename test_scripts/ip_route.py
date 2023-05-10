import getpass
from ipaddress import ip_address, ip_network
from nornir import InitNornir
from nornir_scrapli.tasks import send_command
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file="inventory/config.yaml")

password = getpass.getpass()

ip_add = input("Enter target IP: ")

ip_address(ip_add)

nr.inventory.defaults.password = password

def show_ip_route(task):
	show_result = task.run(task=send_command, command="sh ip route vrf MGMT")
	task.host["facts"] = show_result.scrapli_response.genie_parse_output()
	prefixes = task.host["facts"]["vrf"]["MGMT"]["address_family"]["ipv4"]["routes"]

	for prefix in prefixes:
		if ip_add in prefix:
			print(f"{prefix} : YES")
		print(f"{prefix} NO")
#print(prefix)

results = nr.run(task=show_ip_route)
#print_result(results)
