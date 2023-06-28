import requests
from chat_api.main import ChatApi

class TgwuiApi(ChatApi):

    def __init__(self, host:str = 'http://127.0.0.1', port:int = 5000, user_string:str = '', agent_string:str = ''):

        super().__init__(host, port)

        # Constants
        self.ENDPOINT_GENERATE = '/api/v1/generate'
        self.ENDPOINT_TOKENCOUNT = '/api/v1/token-count'

        # Variables
        self.message_type = self.MESSAGE_TYPE_STRING
        self.message_template = '<from>: <message>'


    def send(self, messages:list, max_tokens:int = 200, timeout:int = 120, temp:float= 0.5) -> str:

        super().send(messages, max_tokens, timeout)

        response = ''

        uri = f'{self.host}:{self.port}{self.ENDPOINT_GENERATE}'

        prompt = ''
        for message in messages:
            prompt += f"{message['message']}\n\n"

        post = {
            'prompt': prompt,
            'temperature': float(temp)
        }
        reply = requests.post(uri, json=post, timeout=timeout)

        if reply.status_code == 200:
            api_response = reply.json()
            response = api_response['results'][0]['text']

        return response
    

    def get_context_size(self) -> int:
        """
        Returns the context size of the LLM.
        """

        return 2048


    def get_message_size(self, message:str = '', timeout:int = 120) -> int:
        """
        Returns the tokens taken by the message.
        """

        result = 0

        uri = f'{self.host}:{self.port}{self.ENDPOINT_TOKENCOUNT}'

        post = {
            'prompt': message
        }
        reply = requests.post(uri, json=post, timeout=timeout)

        if reply.status_code == 200:
            api_response = reply.json()
            try:
                result = api_response['results'][0]['tokens']
            except:
                pass

        return result