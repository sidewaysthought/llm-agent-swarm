import datetime
import time
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
        self.SUMMARY_PROMPT = 'Please summarize the below text.\n\n'

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

        self.inbound_queue[self.SYSTEM_USER] = [self.system_prompt]
        

    def send_to_api(self, messages:list) -> str:
        """
        Send a message to the API and add to history
        
        Args:
            message (list): The conversation to send
            
        Returns:
            str: The response from the API.
        """
        
        reply = ''
        api_message = None
        context_size = self.chat_api.get_context_size()

        # If the messages list is not empty...
        if messages:
            
            # Get the token length of the first message only
            token_length = messages[0]['tokens']
            if token_length > context_size:
                raise Exception('Starting prompt is too long to send to API.')
            
            # Get memories based on the last two messages
            if len(messages) > 2:
                # Recall based on the last two messages
                memories = self.memory.recall(messages[-2:])
            elif len(messages) > 1:
                # Recall based on the last message
                memories = self.memory.recall(messages[-1:])
            else:
                memories = []

            # Insert the memories just after the first message
            messages = messages[:1] + memories + messages[1:]
            
            # Get the token length of all remaining messages
            if len(messages) > 1:
                for message in messages[1:]:
                    token_length += message['tokens']
            else:
                token_length = 0
            
            # If the token length is greater than the context size, summarize
            if token_length > context_size:
                if len(messages) > 2:
                    # Get token length of first and last, subtract from context size
                    middle_token_length = self.chat_api.get_context_size() - (messages[0]['tokens'] + messages[-1]['tokens'])
                    api_message = [messages[0]] + self.summarize(messages[1:-2], middle_token_length) + messages[-1:]
                elif len(messages) > 1:
                    # Get the length of the first and last two messages, subtract from context size
                    middle_token_length = self.chat_api.get_context_size() - (messages[0]['tokens'] + messages[-2]['tokens'] + messages[-1]['tokens'])
                    api_message = [messages[0]] + self.summarize(messages[1:-1], middle_token_length) + messages[-2:]
                else:
                    raise Exception('Starting prompt plus last message is too long to send to API.')
            else:
                api_message = messages
                
            # Send the messages to the API
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
        api_message = None

        if messages:

            # IF the model expects a string, concatenate the messages
            if self.chat_api.message_type == self.chat_api.MESSAGE_TYPE_STRING:
                api_message = self.SUMMARY_PROMPT
                for message in messages:
                    api_message += message['message'] + '\n\n'

            # If the model expects a list, create a list of messages
            elif self.chat_api.message_type == self.chat_api.MESSAGE_TYPE_LIST:
                api_message = []
                summary_prompt = self.RESPONSE_TEMPLATE.copy()
                summary_prompt['message'] = self.SUMMARY_PROMPT
                summary_prompt['to'] = self.profile['name']
                summary_prompt['from'] = self.SYSTEM_USER
                api_message.append(summary_prompt)
                for message in messages:
                    api_message.append(message)

            reply = self.chat_api.send(message=api_message, max_tokens=token_length)

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


    def add_to_inbound_queue(self, message:dict, from_name:str, token_length:int):
        """
        Adds a message to the message queue.
        
        Args:
            message (str): The message to add.
            from_name (str): The name of the sender.
        """

        if from_name not in self.inbound_queue:
            self.inbound_queue[from_name] = []

        message['timestamp'] = datetime.datetime.now().strftime(self.TIME_FORMAT)
        if token_length:
            message['tokens'] = token_length
        else:
            message['tokens'] = self.chat_api.get_message_size(message)

        self.inbound_queue[from_name].append(message)

    
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

        if not self.inbound_queue[message['from']]:
            self.inbound_queue[message['from']] = [self.SYSTEM_USER]
        self.remember(message)
        self.add_to_inbound_queue(message)


    def remember(self, message_obj:dict = {}):
        """
        Remember a message.

        Args:
            message_obj (dict): The message object.
        """

        new_memory = message_obj.copy()
        del new_memory['tokens']
        self.memory.remember(new_memory)


    def recall(self, messages:list) -> dict:
        """
        Search memory for related messages and return as a string to be sent.
        
        Args:
            messages (list): The messages to search for.
            
        Returns:
            str: The response.
        """

        response = self.RESPONSE_TEMPLATE.copy()
        search_terms = ''
        recalled_messages = []
        token_count = 0
        search_results = []
        max_tokens = self.chat_api.get_context_size()

        for message in messages:
            search_terms += message['message'] + '\n'
            
        recalled_messages = self.memory.recall(search_terms)

        for message in recalled_messages:
            message['tokens'] = self.chat_api.get_message_size(message['message'])
            if token_count + message['tokens'] < max_tokens - (max_tokens * 0.05):
                token_count += message['tokens']
                search_results.append(message)

        response['message'] = self.summarize(search_results, token_count)
        response['message'] += 'These are messages which might provide important context.\n\n'
        response['from'] = 'Memory'
        response['to'] = self.profile['name']
        response['timestamp'] = datetime.datetime.now().strftime(self.TIME_FORMAT)
        response['tokens'] = self.chat_api.get_message_size(response['message'])
        
        return response


    def interpret(self):
        """
        Interpret the message queue and add responses to the outbound queue.
        """

        ogm = []
        if self.inbound_queue:
            for from_name in self.inbound_queue:
                print(f'...Interpreting {Fore.GREEN}{from_name}{Fore.RESET}\'s conversation...')
                for message in self.inbound_queue[from_name]:
                    ogm.append(message)
            del self.inbound_queue[from_name]
            reply = self.send_to_api(ogm)
            self.add_to_outbound_queue(reply, from_name)

        # Wait for 5 seconds
        time.sleep(5)
        
        