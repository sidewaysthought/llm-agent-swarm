from colorama import Fore, Back, Style

class Agent:

    def __init__(self, chat_api, agent_profile, project:str = '', user_string:str = '', bot_string:str = ''):

        self.chat_api = chat_api

        # Agent information
        self.profile = agent_profile

        # Set-up the template tokens
        self.tokens = {
            'guidance': self.profile['guidance'],
            'name': self.profile['name'],
            'supervisor': self.profile['supervisor'],
            'role': self.profile['role'],
            'project': project,
            'bot_string': bot_string,
            'user_string': user_string
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

    