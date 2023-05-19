# nornir_scripts
A compilation of network automation and programmability code projects using Nornir

Packages installed:
- nornir
- nornir_scrapli
- nornir_utils
- scrapli[genie]
- pyats
- ipdb
- ipaddress

'''
    OSPF configuration error detection for Cisco IOS-XE using RESTCONF via Nornir Python Libary

'''

import requests
import ipaddress
from collections import defaultdict
from rich import print as rprint
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file="config.yaml")

headers = {"Accept": "application/yang-data+json"}
requests.packages.urllib3.disable_warnings()

config_dict = defaultdict(dict)
facts_dict = defaultdict(dict)

network_error = []
area_error = []
timer_error = []

def get_ospf_facts(task):
    ospf_url = f"https://{task.host.hostname}:{task.host['port']}/restconf/data/ospf-oper-data"
    interface_url = f"https://{task.host.hostname}:{task.host['port']}/restconf/data/native/interface"
    #print(url)
    ospf_response = requests.get(url=ospf_url, headers=headers, auth=(f"{task.host.username}", f"{task.host.password}"), verify=False)

    interface_response = requests.get(url=interface_url, headers=headers, auth=(f"{task.host.username}", f"{task.host.password}"), verify=False)

    ospf_facts = ospf_response.json()
    interface_facts = interface_response.json()

    interfaces = interface_facts['Cisco-IOS-XE-native:interface']['GigabitEthernet']

    for interface in interfaces:
        try:
            int_name = f"GigabitEthernet" + interface['name']
            ip = interface['ip']['address']['primary']['address']
            mask = interface['ip']['address']['primary']['mask']

            config_dict[f"{task.host}"][int_name] = [ip, mask]
        
        except KeyError:
            pass

    ospf_instances = ospf_facts['Cisco-IOS-XE-ospf-oper:ospf-oper-data']['ospf-state']['ospf-instance']

    for ospf_instance in ospf_instances:

        ospf_areas = ospf_instance['ospf-area']

        for ospf_area in ospf_areas:

            try:

                area_id = ospf_area['area-id']
                ospf_intfs = ospf_area['ospf-interface']

                for ospf_intf in ospf_intfs:

                    ospf_int = ospf_intf['name'] 
                    hello = ospf_intf['hello-interval']
                    dead = ospf_intf['dead-interval']

                    facts_dict[f"{task.host}"][ospf_int] = [area_id, hello, dead]

            except KeyError:
                pass

def get_cdp(task):
    cdp_url = f"https://{task.host.hostname}:{task.host['port']}/restconf/data/cdp-neighbor-details"
    cdp_response = requests.get(url=cdp_url, headers=headers, auth=(f"{task.host.username}", f"{task.host.password}"), verify=False)

    cdp_facts = cdp_response.json()

    cdp_neighbors = cdp_facts['Cisco-IOS-XE-cdp-oper:cdp-neighbor-details']['cdp-neighbor-detail']

    for cdp_neighbor in cdp_neighbors:
        device_name = cdp_neighbor['device-name'][2:4]
        local_int = cdp_neighbor['local-intf-name']
        port_id = cdp_neighbor['port-id']

        if local_int.startswith("Gig"):

            try:
                
                # Local interface

                local_ip = config_dict[f"{task.host}"][local_int][0]
                local_mask = config_dict[f"{task.host}"][local_int][1]
                local_net = ipaddress.ip_network(local_ip + "/" + local_mask, strict=False)

                # Remote interface

                remote_ip = config_dict[device_name][port_id][0]
                remote_mask = config_dict[device_name][port_id][1]
                remote_net = ipaddress.ip_network(remote_ip + "/" + remote_mask, strict=False)

                # OSPF configs

                local_area = facts_dict[f"{task.host}"][local_int][0]
                remote_area = facts_dict[device_name][port_id][0]
                local_hello = facts_dict[f"{task.host}"][local_int][1]
                remote_hello = facts_dict[device_name][port_id][1]
                local_dead = facts_dict[f"{task.host}"][local_int][2]
                remote_dead = facts_dict[device_name][port_id][2]

                #rprint(f"{task.host} is connected to {port_id} of {device_name}")

                if not local_net == remote_net:
                    network_error.append(
                        (f"NETWORK MISMATCH: {task.host}'s {local_int} is {local_net} - {device_name}'s {port_id} is {remote_net}")
                    )

                if not local_area == remote_area:
                    area_error.append(
                        (f"AREA MISMATCH: {task.host} on area {local_area} - {device_name} on area {remote_area}")
                    )
                    
                if not local_hello == remote_hello:
                    timer_error.append(
                        (f"HELLO TIMER MISMATCH: {task.host}'s hello-interval {local_hello}s - {device_name}'s hello-interval {remote_hello}s")
                    )

                if not local_dead == remote_dead:
                    timer_error.append(
                        (f"DEAD TIMER MISMATCH: {task.host}'s dead-interval {local_dead}s - {device_name}'s dead-interval {remote_dead}s")
                    )

            except KeyError:
                pass

        # print(task.host, device_name, local_int, port_id)


nr.run(task=get_ospf_facts)

nr.run(task=get_cdp)

if network_error:
    network_fails = sorted(network_error)
    rprint(network_fails)

if area_error:
    area_fails = sorted(area_error)
    rprint(area_fails)

if timer_error:
    timer_fails = sorted(timer_error)
    rprint(timer_fails)

rprint(f"\n\n{'*'*20} SCAN COMPLETED {'*'*20}")
