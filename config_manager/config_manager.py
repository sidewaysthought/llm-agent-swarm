import yaml

class ConfigManager:
    """Class to manage the configuration of the AI swarm."""

    def __init__(self, config_file:str = 'config.yaml'):
        """
        Constructor for ConfigManager

        Args:
            config_file (str, optional): Path to the configuration file. Defaults to 'config.yaml'.
        """

        self.config_file = config_file
        self.config = self.load_config()


    def load_config(self) -> dict:
        """
        Loads the configuration file.
        
        Returns:
            dict: Configuration file as a dictionary.
        """

        config = {}

        with open(self.config_file, 'r') as f:
            config = yaml.load(f, Loader = yaml.FullLoader)

        return config
    

    def get_agents(self) -> list:
        """
        Returns the list of agents.
        
        Returns:
            list: List of agents.
        """

        response = self.get_property('agents')
        if isinstance(response, list):
            return response
        else:
            return []
    

    def get_property(self, identifier:str) -> str|int|list|dict|bool|None:
        """
        Pull a property from the config
        
        Args:
            identifier (str): The identifier of the property to pull.
            
        Returns:
            str: The property.
        """

        if identifier in self.config:
            return self.config[identifier]
        else:
            return None