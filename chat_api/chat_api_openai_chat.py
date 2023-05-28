import json
import os
import openai
import requests
from .chat_api import ChatApi

class OpenAIApiChat(ChatApi):

    def __init__(self, host:str = 'https://api.openai.com', port:int = 80, model:str = 'gpt-3.5-turbo'):

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

        # Run-time variables

        # Set the API key from the environment variable
        self.api_key = os.environ.get('OPENAI_API_KEY', '')
        self.model = model
        openai.api_key = self.api_key


    def send(self, message:str = '', max_tokens:int = 200, timeout:int = 120, temp:float= 0.5) -> str:
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
                "content": "As an AI, you're collaborating with other AIs on a project, using the following information about your creation and your ongoing dialog with another agent."
            },
            {
                "role": "user",
                "content": f'"{message}"'
            }
        ]

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