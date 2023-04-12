import getpass
from nornir import InitNornir
from nornir_scrapli.tasks import send_command
from nornir_scrapli.tasks import send_configs
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file="inventory/config.yaml")

# prompt for the SSH password

password = getpass.getpass()

nr.inventory.defaults.password = password
 
def add_description(task):

    # run show cdp neighbor

    show_result = task.run(task=send_command, command="show cdp neighbor")
    task.host["facts"] = show_result.scrapli_response.genie_parse_output()
    neighbors = task.host["facts"]["cdp"]["index"]

    for neighbor in neighbors:

        # extract the device info for each router to generate description

        device_id = neighbors[neighbor]['device_id']
        local_int = neighbors[neighbor]['local_interface']
        port_id = neighbors[neighbor]['port_id']

        # configure the description for each router interface

        description = f"*** {local_int} is connected to {port_id} of {device_id} ***"
        config_commands = [f"interface {local_int}", f"description {description}"]
        task.run(task=send_configs, configs=config_commands)

results = nr.run(task=add_description)
print_result(results)