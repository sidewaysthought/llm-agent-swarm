import datetime 
import yaml

class Command:

    def __init__(self, config:str = 'config.yaml'):
        self.SYSTEM_USER = 'System'
        self.REPLY_TEMPLATE = {
            'from': self.SYSTEM_USER,
            'to': None,
            'timestamp': None,
            'message': {
                'status': None,
                'response': None,
                'data': None
            }
        }
        self.STATUS_OK = 'OK'
        self.STATUS_ERROR = 'ERROR'
        self.TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
        self.config = self.parse_config(config)
        self.name = self.config['name']
        self.description = self.config['description']
        self.tags = self.config['command_types']
        self.arguments = self.config['arguments']
        self.return_type = self.config['returns']
        self.command_string = self.build_command_string(self.config)


    def parse_config(self, config:str) -> dict:
        """
        Parse config file and return a dict
        """

        response = {}

        try:
            with open(config, 'r') as f:
                response = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            raise Exception(f'Error parsing config file: {e}')

        return response
    

    def validate_arguments(self, arguments:dict) -> bool:
        """
        Validate the inboud arguments against the config file
        """

        validated = False

        try:
            for key, value in arguments.items():
                if key not in self.config['arguments']:
                    break
                arg_type = self.config['arguments'][key]['type']
                if isinstance(value, arg_type):
                    break
            validated = True
        except Exception as e:
            pass

        return validated


    def create_response(self, asking_agent:str) -> dict:

        response = self.REPLY_TEMPLATE.copy()
        self.REPLY_TEMPLATE.copy()
        response['to'] = asking_agent
        response['timestamp'] = datetime.datetime.now().strftime(self.TIME_FORMAT)

        return response
    

    def build_command_string(self, config:dict) -> str:
        """
        Create the command string for use by agents.
        
        Returns:
            str: The command string
        """
    
        response = ''
        documentation = ''

        documentation += f'\n"""\n{config["description"]}\n'
        response += f'{config["name"]}('
        arguments = []
        for argument in config['arguments']:
            new_argument = ''
            new_argument += f"{argument['name']}: {argument['type']}"
            documentation += f"  {argument['name']} - {argument['description']}\n"
            if not argument['required']:
                new_argument += f" = {argument['default']}"
            arguments.append(new_argument)
        documentation += f"Returns {config['returns']['description']}.\n"
        documentation += '"""\n'
        response = documentation + response
        response += ', '.join(arguments)
        response += f") -> {config['returns']['type']}"
    
        return response


    def call(self, asking_agent:str, arguments:dict) -> dict:
        return {}
    
