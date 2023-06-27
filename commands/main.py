import os
import importlib
import inspect
from commands.command import Command
from pathlib import Path

class Commands:

    def __init__(self, config:dict = {}):

        self.config = config
        self.commands = self.load_commands()
        self.command_strings = self.get_command_list()
        

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
    

    def get_command_list(self, tag:str = '') -> dict:
        """
        Get a list of commands that have been registered. Optionally limit the response by tag
        
        Args:
            tag (str): The tag to limit the response by
            
        Return:
            list: A list of Command objects
        """

        response = {}

        for command in self.commands:
            for tag in command.tags:
                if tag not in response:
                    response[tag] = []
                response[tag].append(command.command_string)

        return response