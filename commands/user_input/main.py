from commands.command import Command

class UserInputCommand(Command):

    def __init__(self, config:str = 'config.yaml'):
        super().__init__(config)
        self.config = self.parse_config(config)

    
    def call(self, asking_agent:str, arguments:dict) -> dict:
        """
        Ask the user for input and return the response.
        
        Args:
            asking_agent (str): The name of the agent asking for input
            arguments (dict): The arguments for the command
            
        Returns:
            dict: The response from the command
        """

        response = self.create_response(asking_agent)
        is_valid = self.validate_arguments(arguments)

        if is_valid:
            user_input = input(arguments['message'])
            response['data'] = user_input
            response['status'] = self.STATUS_SUCCESS
            response['message'] = 'The user has responded with this message.'
        else:
            response['status'] = self.STATUS_ERROR
            response['message'] = 'Invalid arguments'

        return response
