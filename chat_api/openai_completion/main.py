import os
import openai
import tiktoken
import time
from chat_api.main import ChatApi

class OpenAIApiCompletion(ChatApi):

    def __init__(self, host:str = 'https://api.openai.com', port:int = 80, model_string='text-ada-001'):

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
        self.RETRIES = 5

        # Run-time variables
        self.model = model_string
        self.message_type = self.MESSAGE_TYPE_STRING
        self.message_template = '<from>: <message>\n\n'

        # Set the API key from the environment variable
        self.api_key = os.environ.get('OPENAI_API_KEY', '')
        openai.api_key = self.api_key


    def send(self, message:str, max_tokens:int = 200, temp:float= 0.5) -> str:
        """
        Send a chat message to the OpenAI API and return the response.
        
        Args:
            message (str): The message to send to the API.
            max_tokens (int): The maximum number of tokens to generate.
            temp (float): The temperature to use for the response.
            
        Returns:
            str: The response from the API.
        """

        super().send(message, max_tokens, temp)

        response = ''

        incomplete = True
        retries = 0
        while incomplete:
            try:
                reply = openai.Completion.create(
                    engine=self.model,
                    prompt=message,
                    max_tokens=max_tokens
                )
                incomplete = False
            except:
                time.sleep(3)
                retries += 1
                if retries > self.RETRIES:
                    raise Exception('OpenAI API call failed after {} retries.'.format(self.RETRIES))

        # Save the first text response to reply
        try:
            response = reply['choices'][0]['text'] # type: ignore
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