import getpass
from nornir import InitNornir
from nornir_scrapli.tasks import send_configs
from nornir_utils.plugins.functions import print_result

nr = InitNornir(config_file="inventory/config.yaml")

nr.inventory.defaults.password = getpass.getpass()

def run_config(task):
    task.run(task=send_configs, configs=["no ip route vrf  MGMT 0.0.0.0 0.0.0.0 192.168.10.1", "do wr"])

results = nr.run(task=run_config)

print_result(results)