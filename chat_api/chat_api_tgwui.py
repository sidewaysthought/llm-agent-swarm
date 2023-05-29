import json
import requests
from .chat_api import ChatApi

class TgwuiApi(ChatApi):

    def __init__(self, host:str = 'http://127.0.0.1', port:int = 5000, user_string:str = '', agent_string:str = ''):

        super().__init__(host, port)

        # Constants
        self.ENDPOINT = '/api/v1/generate'

        # Variables
        self.message_type = self.MESSAGE_TYPE_STRING
        self.message_template = '<from>: <message>'


    def send(self, message:str, max_tokens:int = 200, timeout:int = 120, temp:float= 0.5) -> str:

        response = ''

        uri = f'{self.host}:{self.port}{self.ENDPOINT}'

        post = {
            'prompt': message,
            'temperature': float(temp)
        }
        reply = requests.post(uri, json=post, timeout=timeout)

        if reply.status_code == 200:
            api_response = reply.json()
            response = api_response['results'][0]['text']

        return response