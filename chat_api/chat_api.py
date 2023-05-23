class ChatApi:

    def __init__(self, host:str, port:int):

        self.host = host
        self.port = port
        pass


    def send(self, message:str = '', max_tokens:int = 200, timeout:int = 120) -> str:

        return ''
