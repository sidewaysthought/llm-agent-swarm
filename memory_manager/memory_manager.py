import uuid
from rdflib import Graph, URIRef, Literal, Namespace

class MemoryManager:

    def __init__(self, agent_name:str = '', session_id:str = ''):
        
        # I'm using two database styles because I'm greedy and want the best of both worlds where graph can
        # be used for triples and rapid subject searches, and the vector database can be used for detailed
        # semantic searches that the graph database can't do.
        self.graph = Graph()
        self.namespace = Namespace(session_id + '-' + agent_name)


    def remember(self, message_obj:dict = {}):
        """
        Remember a message.

        Args:
            message (str, optional): The message to remember. Defaults to ''.

        Returns:
            bool: True if successful, False otherwise.
        """

        if 'message' in message_obj and 'from' in message_obj and 'to' in message_obj and 'timestamp' in message_obj:
            memory_id = str(uuid.uuid4())
            memory_uri = URIRef(self.namespace + memory_id)
            self.graph.add((memory_uri, self.namespace.from_name, Literal(message_obj["from"])))
            self.graph.add((memory_uri, self.namespace.to_name, Literal(message_obj["to"])))
            self.graph.add((memory_uri, self.namespace.datetime, Literal(message_obj["datetime"])))
            self.graph.add((memory_uri, self.namespace.message, Literal(message_obj["message"])))
    

    def recall(self, search_term:str = '') -> list:
        """
        Recall a message.

        Args:
            search_term (str, optional): The search term. Defaults to ''.

        Returns:
            str: The message if found, empty string otherwise.
        """

        results = []

        for memory_uri in self.graph.subjects(predicate=self.namespace.message, object=Literal(search_term)):
            memory = {}
            memory["from"] = str(self.graph.value(subject=memory_uri, predicate=self.namespace.from_name))
            memory["to"] = str(self.graph.value(subject=memory_uri, predicate=self.namespace.to_name))
            memory["datetime"] = str(self.graph.value(subject=memory_uri, predicate=self.namespace.datetime))
            memory["message"] = str(self.graph.value(subject=memory_uri, predicate=self.namespace.message))
            results.append(memory)

        return results
    

    def forget(self, search_term:str = '') -> bool:
        """
        Forget a message.

        Args:
            search_term (str, optional): The search term. Defaults to ''.

        Returns:
            bool: True if successful, False otherwise.
        """

        data_removed = False

        memories_to_remove = []
        for memory_uri in self.graph.subjects(predicate=self.namespace.message, object=Literal(search_term)):
            memories_to_remove.append(memory_uri)

        if len(memories_to_remove) > 0:
            data_removed = True
            
        for memory_uri in memories_to_remove:
            self.graph.remove((memory_uri, None, None))
            self.graph.remove((None, None, memory_uri))

        return data_removed
    

    def prune(self):
        """
        Prune the memory.
        """

        return True