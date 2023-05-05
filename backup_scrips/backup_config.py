from nornir import InitNornir
from nornir_scrapli.tasks import send_command
from nornir_utils.plugins.functions import print_result
from nornir_utils.plugins.tasks.files import write_file
from datetime import date
import pathlib

nr = InitNornir(config_file="inventory/config.yaml")

def backup_config(task):
	cmds =  ["sh run", "sh ver", "sh cdp neighbor"]
	for cmd in cmds:
		config_dir = "config-archive"
		date_dir = config_dir + "/" + str(date.today())
		command_dir = date_dir + "/" + cmd.replace(" ", "-")
		pathlib.Path(config_dir).mkdir(exist_ok=True)
		pathlib.Path(date_dir).mkdir(exist_ok=True)
		pathlib.Path(command_dir).mkdir(exist_ok=True)
		r = task.run(task=send_command, command=cmd)
		task.run(
			task=write_file, 
			content=r.result, 
			filename=str(command_dir) + f"/{task.host}.txt")

results = nr.run(name="Creating Backup Archive", task=backup_config)
print_result(results)
