from colorama import Fore, Back, Style

class Agent:

    def __init__(self, chat_api, agent_profile, project:str = '', user_string:str = '', bot_string:str = ''):
        """
        Constructor for Agent

        Args:
            chat_api (ChatApi): The chat API.
            agent_profile (dict): The agent profile.
            project (str, optional): The project name. Defaults to ''.
            user_string (str, optional): The user string. Defaults to ''.
            bot_string (str, optional): The bot string. Defaults to ''.
        """
        
        # Agent Foundation
        self.profile = agent_profile
        self.chat_api = chat_api

        # Constants
        self.RESPONSE_TEMPLATE = {
            "from": self.profile['name'],
            "to": None,
            "message": None
        }

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
        self.message_queue = []

    def sign_on(self,message_template:str = 'Agent <name> has signed on.'):
        """
        Signs on to the chat API.
        """

        message = self.fill_in_script(message_template)
        reply = self.send_to_api(message)
        self.add_to_message_queue(reply, self.profile['supervisor'])
        

    def send_to_api(self, message) -> str:
        """
        Send a message to the API and add to history
        
        Args:
            message (str): The message to send.
            
        Returns:
            str: The response from the API.
        """

        #self.history.append(message)
        print(f"{Fore.GREEN}{self.profile['name']}{Style.RESET_ALL} sending to API")
        reply = self.chat_api.send(message, self.tokens)
        print(f"{Fore.GREEN}{self.profile['name']}{Style.RESET_ALL} received from API")

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
    

    def add_to_message_queue(self, message:str, to:str|None = None):
        """
        Adds a message to the message queue.
        
        Args:
            message (str): The message to add.
        """

        new_message = self.RESPONSE_TEMPLATE.copy()
        new_message['message'] = message
        new_message['to'] = to

        self.message_queue.append(message)

    
    def deliver(self) -> list:
        """
        Return the message queue, clear it, and update history.
        
        Returns:
            list: The message queue.
        """

        messages = self.message_queue
        self.message_queue = []

        for message in messages:
            self.history.append(f"To: {str(message['to'])}, Message: {str(message['message'])}")

        return messages
    

    def receive(self, message:dict):
        """
        Receive a message and add it to the message queue.
        
        Args:
            message (str): The message to receive.
        """

        message = "Sent from " + message['from'] + ": " + message['message']

        self.send_to_api(message)