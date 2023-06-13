import json
import os
import openai
import tiktoken
import time
from chat_api.main import ChatApi

class OpenAIApiChat(ChatApi):

    def __init__(self, host:str = 'https://api.openai.com', port:int = 80, model_string:str = 'gpt-3.5-turbo'):

        super().__init__(host, port)

        # Constants
        self.ENDPOINT = '/v1/chat/completions'
        self.MODELS = [
            {
                'name': 'gpt-4',
                'context': 8192
            },
            {
                'name': 'gpt-3.5-turbo',
                'context': 4096
            }
        ]
        self.API_MSG = {
            "role": "user",
            "content": ''
        }
        self.END_STATEMENT = 'With the information you have received about the project, please initiate the conversation.'
        self.RETRIES = 5

        # Run-time variables
        self.model = model_string
        self.message_type = self.MESSAGE_TYPE_LIST
        self.message_template = '<from>: <message>'

        # Set the API key from the environment variable
        self.api_key = os.environ.get('OPENAI_API_KEY', '')
        openai.api_key = self.api_key


    def send(self, message:list = [], max_tokens:int = 200, timeout:int = 120, temp:float= 0.5) -> str:
        """
        Send a chat message to the OpenAI API and return the response.
        
        Args:
            message (str): The message to send to the API.
            max_tokens (int): The maximum number of tokens to generate.
            timeout (int): The maximum number of seconds to wait for a response.
            temp (float): The temperature to use for the response.
            
        Returns:
            str: The response from the API.
        """

        super().send(message, max_tokens, timeout, temp)
        
        response = ''
        api_package = []

        system_msg = self.API_MSG.copy()
        system_msg['role'] = 'system'
        system_msg['content'] = message[0]['message']
        api_package.append(system_msg)

        for msg in message[1:]:
            new_msg = self.API_MSG.copy()
            new_msg['content'] = msg
            api_package.append(new_msg)
        
        end_message = self.API_MSG.copy()
        end_message['content'] = self.END_STATEMENT
        api_package.append(end_message)

        incomplete = True
        retries = 0
        while incomplete:
            try:
                reply = openai.ChatCompletion.create(
                    model=self.model,
                    messages=api_package,
                    timeout=int(timeout),
                    temperature=float(temp)
                )
                incomplete = False
            except:
                time.sleep(3)
                retries += 1
                if retries > self.RETRIES:
                    raise Exception('OpenAI API call failed after {} retries.'.format(self.RETRIES))

        # Save the first text response to reply
        try:
            response = reply['choices'][0]['message']['content'] # type: ignore
        except:
            pass

        
        return response
    

    def get_context_size(self) -> int:
        """
        Returns the context size of the LLM.

        Returns:
            int: The context size of the LLM.
        """

        for model in self.MODELS:
            if model['name'] == self.model:
                return model['context']
        
        return -1


    def get_message_size(self, message:str = '', timeout:int = 120) -> int:
        """
        Returns the tokens taken by the message.
        """

        result = 0

        encoder = tiktoken.encoding_for_model(self.model)
        msg_as_tokens = encoder.encode(message)
        result = len(msg_as_tokens)

        return result