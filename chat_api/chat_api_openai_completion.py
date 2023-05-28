import json
import os
import openai
import requests
from .chat_api import ChatApi

class OpenAIApiCompletion(ChatApi):

    def __init__(self, host:str = 'https://api.openai.com', port:int = 80, model='text-ada-001'):

        super().__init__(host, port)

        # Constants
        self.ENDPOINT = '/v1/completions'
        self.MODELS = [
            {
                'name': 'gpt-4',
                'context': 8192
            },
            {
                'name': 'gpt-4-32k',
                'context': 32768
            },
            {
                'name': 'text-davinci-003',
                'context': 4097
            },
            {
                'name': 'text-curie-001',
                'context': 2049
            },
            {
                'name': 'text-babbage-001',
                'context': 2049
            },
            {
                'name': 'text-ada-001',
                'context': 2049
            }
        ]

        # Run-time variables

        # Set the API key from the environment variable
        self.api_key = os.environ.get('OPENAI_API_KEY', '')
        openai.api_key = self.api_key


    def send(self, message:str = '', max_tokens:int = 200, temp:float= 0.5, model:str = 'gpt-3.5-turbo') -> str:
        """
        Send a chat message to the OpenAI API and return the response.
        
        Args:
            message (str): The message to send to the API.
            max_tokens (int): The maximum number of tokens to generate.
            temp (float): The temperature to use for the response.
            
        Returns:
            str: The response from the API.
        """

        response = ''

        reply = openai.ChatCompletion.create(
            model=model,
            prompt=message,
            max_tokens=max_tokens,
            temperature=temp
        )

        # Save the first text response to reply
        try:
            response = reply['choices'][0]['text'] # type: ignore
        except:
            pass

        
        return response
    
