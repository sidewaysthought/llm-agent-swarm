from commands.command import Command

class UserInputCommand(Command):

    def __init__(self, config:str = 'config.yaml'):
        super().__init__(config)

    
    def call(self, asking_agent:str, arguments:dict) -> dict:

        response = self.create_response(asking_agent)
        is_valid = self.validate_arguments(arguments)

        if is_valid:
            # Your code here
            pass
        else:
            response['status'] = self.STATUS_ERROR
            response['message'] = 'Invalid arguments'

        return response
