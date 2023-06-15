import json
import os
import importlib
import inspect
import pkgutil
from commands.command import Command

class Commands:

    def __init__(self, config:dict = None):

        self.config = config
        self.commands = self.load_commands()
        print(json.dumps(self.commands, indent=4))


    def load_commands(self) -> list:
        """
        Look through this directory for modules that inheits the Command class, initializes them,
        then returns them as a list 
        
        Return:
            list: A list of Command objects
        """

        command_list = []
        directory = os.path.dirname(__file__)
    
        # Iterate over each subdirectory in the directory.
        for _, package_name, _ in pkgutil.iter_modules([directory]):
            module = importlib.import_module(f"{package_name}.main")
            for _, obj in inspect.getmembers(module):
                # Check if the object is a class and if it descends from the base class.
                if inspect.isclass(obj) and issubclass(obj, Command):
                    command_list.append(obj)

        return command_list

