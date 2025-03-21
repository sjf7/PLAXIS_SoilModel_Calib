
import yaml
from yaml.loader import SafeLoader
import os













def Read_command_sheet_NorSand_v3(Command_sheet_name, Command_sheet_location):

    command_file = os.path.join(Command_sheet_location, Command_sheet_name)

    with open(command_file, 'r') as f:
        yaml_data = list(yaml.load_all(f, Loader=SafeLoader))


    return yaml_data




