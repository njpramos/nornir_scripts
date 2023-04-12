import sys
import getpass
import pprint
from nornir import InitNornir
from nornir_scrapli.tasks import send_command
from nornir_utils.plugins.functions import print_result


nr = InitNornir(config_file="inventory/config.yaml")

password = getpass.getpass()

nr.inventory.defaults.password = password
 
def show_command(task):

    show_result = task.run(task=send_command, command="show ip interface brief")
    task.host["facts"] = show_result.scrapli_response.genie_parse_output()


    interfaces = task.host["facts"]["interface"]


    for interface in interfaces:

        link_status = interfaces[interface]['protocol']
        
        if link_status == 'up':
            print(f"{interface} is UP")

results = nr.run(task=show_command)
