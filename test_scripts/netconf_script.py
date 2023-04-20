import xmltodict
import pprint
from nornir import InitNornir
from nornir_scrapli.tasks import netconf_get_config
from nornir_utils.plugins.functions import print_result

pp = pprint.PrettyPrinter(indent=4)

nr = InitNornir(config_file="inventory/config.yaml")

def pull_netconf_data(task):
    result = task.run(task=netconf_get_config, source="running", filters="/native/interface", filter_type="xpath")
    task.host['facts'] = xmltodict.parse(result.result)

    interfaces = task.host['facts']['rpc-reply']['data']['native']['interface']['GigabitEthernet']['name']

    print(interfaces)

results = nr.run(task=pull_netconf_data)

# print_result(results)