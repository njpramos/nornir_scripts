import requests
import json
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir.core.task import Result

nr = InitNornir(config_file="inventory/config.yaml")

requests.packages.urllib3.disable_warnings()

headers = {"Accept": "application/yang-data+json"}

def get_facts(task):
	url = f"https://{task.host.hostname}:{task.host['port']}/restconf/data/openconfig-interfaces:interfaces?content=nonconfig"

	response = requests.get(url=url, headers=headers, auth=(f"{task.host.username}", f"{task.host.password}"), verify=False)
	return Result(host=task.host, result=response.text)
	
	#print(response.json())

results = nr.run(task=get_facts)
print_result(results)
