import sys
import getpass
from nornir import InitNornir
from nornir_scrapli.tasks import send_command
from nornir_utils.plugins.functions import print_result


nr = InitNornir(config_file="inventory/config.yaml")

password = getpass.getpass()

nr.inventory.defaults.password = password

# parse the username in the CLI

# username = sys.argv[1]

# nr.inventory.defaults.username = username

results = nr.run(task=send_command, command="show run")

print_result(results)