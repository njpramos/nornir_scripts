import sys
import getpass
import pprint
from nornir import InitNornir
from nornir_scrapli.tasks import send_command
from nornir_utils.plugins.functions import print_result
from rich import print as rprint


nr = InitNornir(config_file="inventory/config.yaml")

password = getpass.getpass()

nr.inventory.defaults.password = password
 
def show_command(task):

    show_result = task.run(task=send_command, command="show ip interface brief")
    structured_result = show_result.scrapli_response.textfsm_parse_output()

    for interface in structured_result:

        print(f"{interface['intf']} : {interface['status']}")

    # interfaces = task.host["facts"]["interface"]


    # for interface in interfaces:

    #     link_status = interfaces[interface]['protocol']
        
    #     if link_status == 'up':
    #         rprint(f"{interface} is [green]UP[/green]")

results = nr.run(task=show_command)
