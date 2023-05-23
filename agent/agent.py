class Agent:

    def __init__(self, chat_api, name:str = 'Agent', supervisor:str = '', role:str = '', mission:str = '', project:str = ''):

        self.chat_api = chat_api

        # Agent information
        self.name = name
        self.supervisor = supervisor
        self.role = role
        self.mission = mission
        self.project = project

        # Set-up the template tokens
        self.tokens = {
            'name': self.name,
            'supervisor': self.supervisor,
            'role': self.role,
            'mission': self.mission,
            'project': self.project
        }

        # Attributes
        self.history = []


    def sign_on(self,message_template:str = 'Agent <name> has signed on.'):
        """
        Signs on to the chat API.
        """

        message = self.fill_in_script(message_template)
        reply = self.send_to_api(message)
        self.history.append(reply)
        

    def send_to_api(self, message) -> str:
        """
        Send a message to the API and add to history
        
        Args:
            message (str): The message to send.
            
        Returns:
            str: The response from the API.
        """

        self.history.append(message)
        reply = self.chat_api.send(message, self.tokens)

        return reply


    def fill_in_script(self, script) -> str:
        """
        Fills in the template tokens in the script and return the completed script.

        Args:
            script (str): The script to fill in.

        Returns:
            str: The filled in script.
        """

        for token in self.tokens:
            script = script.replace(f'<{token}>', self.tokens[token])

        return script

    