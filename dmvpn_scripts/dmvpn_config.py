'''

Automates the deployment of HUB and SPOKES in a DMVPN topology using iBGP

'''

from nornir import InitNornir
from nornir_scrapli.tasks import send_configs
from nornir_utils.plugins.functions import print_result
from nornir_utils.plugins.tasks.data import load_yaml
from nornir_jinja2.plugins.tasks import template_file


nr = InitNornir(config_file="inventory/config.yaml")


def load_vars(task):
	
	'''
		Load host and group variables as dictionaries
	'''

	data = task.run(task=load_yaml, file=f"./host_vars/{task.host}.yaml")
	task.host["facts"] = data.result
	group_data = task.run(task=load_yaml, file=f"./group_vars/all.yaml")
	task.host["group_facts"] = group_data.result
	config_vrf(task)

def config_vrf(task):

	''' 
		Generate VRF template and push configs
	'''

	vrf_template = task.run(
		task=template_file, 
		name="Building VRF Configuration",
		template="vrf.j2",
		path="./templates"
	)
	task.host["vrf"] = vrf_template.result
	vrf_output = task.host["vrf"]
	vrf_send = vrf_output.splitlines()
	task.run(task=send_configs, name="Pushing VRF Configs", configs=vrf_send)
	config_dmvpn(task)

def config_dmvpn(task):

	'''
		Generate DMVPN template and push configs
	'''

	dmvpn_template = task.run(
		task=template_file,
		name="Building DMVPN Configuration",
		template="dmvpn.j2",
		path="./templates"
	)
	task.host["dmvpn"] = dmvpn_template.result
	dmvpn_output = task.host["dmvpn"]
	dmvpn_send = dmvpn_output.splitlines()
	task.run(task=send_configs, name="Pushing DMVPN Configs", configs=dmvpn_send)
	config_bgp(task)

def config_bgp(task):
	'''
		Generate BGP routing template and push configs
	'''

	bgp_template = task.run(
		task=template_file,
		name="Building BGP template",
		template="bgp.j2",
		path="./templates"
	)
	task.host["bgp"] = bgp_template.result
	bgp_output = task.host["bgp"]
	print(bgp_output)
	bgp_send = bgp_output.splitlines()
	task.run(task=send_configs, name="Pushing BGP Configs", configs=bgp_send)

results = nr.run(task=load_vars)
print_result(results)
