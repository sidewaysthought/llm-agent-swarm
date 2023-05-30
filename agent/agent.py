import datetime
import json
import re
from colorama import Fore, Back, Style
from memory_manager.memory_manager import MemoryManager

class Agent:

    def __init__(self, chat_api, agent_profile, project:str = '', session_id:str = ''):
        """
        Constructor for Agent

        Args:
            chat_api (ChatApi): The chat API.
            agent_profile (dict): The agent profile.
            project (str, optional): The project name. Defaults to ''.
            user_string (str, optional): The user string. Defaults to ''.
            bot_string (str, optional): The bot string. Defaults to ''.
        """

        super().__init__()
        
        # Agent Foundation
        self.profile = agent_profile
        self.chat_api = chat_api
        self.session_id = session_id

        # Constants
        self.RESPONSE_TEMPLATE = {
            "from": self.profile['name'],
            "to": None,
            "message": None,
            'timestamp': None,
            'tokens': 0
        }
        self.SYSTEM_USER = 'System'
        self.TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

        # Set-up the template tokens
        self.replacement_strings = {
            'guidance': self.profile['guidance'],
            'name': self.profile['name'],
            'supervisor': self.profile['supervisor'],
            'role': self.profile['role'],
            'project': project
        }

        # Attributes
        self.name = self.profile['name']
        self.memory = MemoryManager(self.session_id + '-' + self.name)
        self.outbound_queue = {}
        self.inbound_queue = {}
        self.system_prompt = self.RESPONSE_TEMPLATE.copy()


    def sign_on(self,message_template:str = 'Agent <name> has signed on.'):
        """
        Signs on to the chat API.
        """

        self.system_prompt['message'] = self.fill_in_template(message_template, self.replacement_strings)
        self.system_prompt['to'] = self.profile['name']
        self.system_prompt['from'] = self.SYSTEM_USER
        self.system_prompt['timestamp'] = datetime.datetime.now().strftime(self.TIME_FORMAT)
        self.system_prompt['tokens'] = self.chat_api.get_message_size(self.system_prompt['message'])

        self.add_to_inbound_queue(self.system_prompt['message'], self.profile['supervisor'])
        

    def send_to_api(self, messages:list) -> str:
        """
        Send a message to the API and add to history
        
        Args:
            message (list): The conversation to send
            
        Returns:
            str: The response from the API.
        """
        
        api_message = None

        context_size = self.chat_api.get_context_size()
        tokens_used = 0
        for message in messages:
            tokens_used += message['tokens']

        # If more tokens are being used than available, summarize
        if tokens_used > (context_size - (context_size * 0.05)):
            all_messages = []
            all_messages.append(messages[0])
            middle_msg = {}
            middle_token_count = 0
            if len(messages) > 3:
                # Keep the first, the last two, and summarize everything in the middle
                for middle_msg in messages[1:-2]:
                    middle_token_count = middle_msg['tokens']
                middle_msg = self.summarize(messages[1:-2], middle_token_count)
            else:
                # Keep the first and last, summarize everything in the middle
                for middle_msg in messages[1:-1]:
                    middle_token_count = middle_msg['tokens']
                middle_msg = self.summarize(messages[1:-1], middle_token_count)
            all_messages.append(middle_msg)
            all_messages.append(messages[-2:])
            messages = all_messages

        # Template all messages and send end-to-end
        for message in messages:
            templated_message = self.fill_in_template(self.chat_api.message_template, message)
            if self.chat_api.message_type == self.chat_api.MESSAGE_TYPE_STRING:
                api_message = templated_message + '\n\n'
            elif self.chat_api.message_type == self.chat_api.MESSAGE_TYPE_LIST:
                api_message = []
                for message in messages:
                    api_message.append(templated_message)

        reply = self.chat_api.send(message=api_message)
        return reply
    

    def summarize(self, messages:list, token_length:int) -> str:
        """
        Use an API call to summarize a list of messages.
        
        Args:
            messages (list): The messages to summarize.
        
        Returns:
            str: The summarized messages.
        """

        reply = ''

        api_message = 'Please summarize the following message. No need to be polite.\n\n'

        for message in messages:
            api_message += message['message'] + '\n\n'

        reply = self.chat_api.send(message=api_message)

        return reply
    

    def fill_in_template(self, script, replacement_tokens:dict) -> str:
        """
        Fills in the template tokens in the script and return the completed script.

        Args:
            script (str): The script to fill in.

        Returns:
            str: The filled in script.
        """

        for symbol in replacement_tokens:
            new_value = str(replacement_tokens[symbol])
            script = script.replace(f'<{symbol}>', new_value)

        return script
    

    def add_to_outbound_queue(self, message:str, to:str|None = None):
        """
        Adds a message to the message queue.
        
        Args:
            message (str): The message to add.
        """

        new_message = self.RESPONSE_TEMPLATE.copy()
        new_message['message'] = message
        new_message['to'] = to
        new_message['from'] = self.profile['name']
        new_message['timestamp'] = datetime.datetime.now().strftime(self.TIME_FORMAT)

        if to not in self.outbound_queue:
            self.outbound_queue[to] = []

        self.outbound_queue[to].append(new_message)


    def add_to_inbound_queue(self, message:str, from_name:str):
        """
        Adds a message to the message queue.
        
        Args:
            message (str): The message to add.
            from_name (str): The name of the sender.
        """

        new_message = self.RESPONSE_TEMPLATE.copy()
        new_message['message'] = message
        new_message['from'] = from_name
        new_message['to'] = self.profile['name']
        new_message['timestamp'] = datetime.datetime.now().strftime(self.TIME_FORMAT)
        new_message['tokens'] = self.chat_api.get_message_size(message)

        if from_name not in self.inbound_queue:
            self.inbound_queue[from_name] = []

        self.inbound_queue[from_name].append(new_message)

    
    def deliver(self) -> list:
        """
        Return the message queue, clear it, and update history.
        
        Returns:
            list: The message queue.
        """

        response = []

        for to_name in self.outbound_queue:
            for message in self.outbound_queue[to_name]:
                ogm = self.RESPONSE_TEMPLATE.copy()
                ogm['message'] = message['message']
                ogm['to'] = to_name
                ogm['from'] = self.profile['name']
                ogm['timestamp'] = message['timestamp']
                self.memory.remember(ogm) # type: ignore
                response.append(ogm)
            self.outbound_queue[to_name] = []

        return response
    

    def receive(self, message:dict):
        """
        Receive a message and add it to the message queue.
        
        Args:
            message (str): The message to receive.
        """

        to_remember = message.copy()
        del to_remember['tokens']
        self.remember(to_remember)
        self.add_to_inbound_queue(message['message'], message['from'])


    def remember(self, message_obj:dict = {}):
        """
        Remember a message.

        Args:
            message_obj (dict): The message object.
        """

        new_memory = message_obj.copy()
        del new_memory['tokens']
        self.memory.remember(new_memory)


    def interpret(self):
        """
        Interpret the message queue and add responses to the outbound queue.
        """

        ogm = []
        for from_name in self.inbound_queue:
            print(f'...Interpreting {Fore.GREEN}{from_name}{Fore.RESET}\'s conversation...')
            ogm.append(self.system_prompt)
            for message in self.inbound_queue[from_name]:
                ogm.append(message)
            self.inbound_queue[from_name] = []
            reply = self.send_to_api(ogm)
            self.add_to_outbound_queue(reply, from_name)
        
        