import os

class ChatApi:

    def __init__(self, host:str, port:int, user_string:str = '', agent_string:str = ''):

        # Constants
        self.MESSAGE_TYPE_STRING = 'str'
        self.MESSAGE_TYPE_LIST = 'list'
        self.USER_STRING = user_string
        self.AGENT_STRING = agent_string

        # Variables
        self.host = host
        self.port = port
        self.message_type = self.MESSAGE_TYPE_STRING
        self.message_template = ''


    def send(self, message:str|list|dict, max_tokens:int = 200, timeout:int = 120) -> str:

        return ''
