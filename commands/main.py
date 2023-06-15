import os
import importlib
import inspect
from commands.command import Command
from pathlib import Path

class Commands:

    def __init__(self, config:dict = None):

        self.config = config
        self.commands = self.load_commands()
        for command in self.commands:
            print(command._name)
        

    def load_commands(self) -> list:
        """
        Look through this directory for modules that inheits the Command class, initializes them,
        then returns them as a list 
        
        Return:
            list: A list of Command objects
        """

        command_list = []
        directory = Path(__file__).parent

        # Iterate over all Python files in the directory and its subdirectories.
        for file_path in directory.rglob('*.py'):
            module_path = file_path.relative_to(directory).with_suffix('')
            module_name = 'commands.' + '.'.join(module_path.parts)
            module = importlib.import_module(module_name)
            for _, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, Command) and obj is not Command and obj.__module__ == module.__name__:
                    directory = os.path.dirname(file_path)
                    config_path = os.path.join(directory, 'config.yaml')
                    command_list.append(obj(config=config_path))

        return command_list

