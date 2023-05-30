import json
import os
import openai
import requests
import tiktoken
from .chat_api import ChatApi

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

        response = ''

        messages = [
            {
                "role": "system",
                "content": "As an AI, you're collaborating with other AIs on a project. Information about your purpose, and an active conversation follow."
            }
        ]

        for msg in message:
            new_msg = self.API_MSG.copy()
            new_msg['content'] = msg
            messages.append(new_msg)

        print(json.dumps(messages, indent=4))

        reply = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            timeout=int(timeout),
            temperature=float(temp)
        )

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