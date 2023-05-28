class ChatApi:

    def __init__(self, host:str, port:int):

        # Constants
        self.MESSAGE_TYPE_STRING = 'str'
        self.MESSAGE_TYPE_LIST = 'list'

        # Variables
        self.host = host
        self.port = port
        self.message_type = self.MESSAGE_TYPE_STRING
        self.message_template = ''


    def send(self, message:str|list|dict, max_tokens:int = 200, timeout:int = 120) -> str:

        return ''
