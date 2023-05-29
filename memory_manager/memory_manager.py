import uuid
from rdflib import Graph, URIRef, Literal, Namespace

class MemoryManager:

    def __init__(self, sys_namespace:str):

        # Constants
        self.SEARCH_THRESHOLD = 50
        
        # I'm using two database styles because I'm greedy and want the best of both worlds where graph can
        # be used for triples and rapid subject searches, and the vector database can be used for detailed
        # semantic searches that the graph database can't do.
        self.graph = Graph()
        self.namespace = Namespace(sys_namespace)
        self.usage_counter = {}


    def remember(self, message_obj:dict = {}):
        """
        Remember a message.

        Args:
            message (str, optional): The message to remember. Defaults to ''.

        Returns:
            bool: True if successful, False otherwise.
        """

        #if 'message' in message_obj and 'from' in message_obj and 'to' in message_obj and 'timestamp' in message_obj:
        memory_id = str(uuid.uuid4())
        memory_uri = URIRef(self.namespace + memory_id)

        for key in message_obj:
            predicate = URIRef(str(self.namespace) + key)
            self.graph.add((memory_uri, predicate, Literal(message_obj[key])))
            self.usage_counter[memory_id] = 0

        self.prune()
    

    def recall(self, search_term:str = '') -> list:
        """
        Recall a message.

        Args:
            search_term (str, optional): The search term. Defaults to ''.

        Returns:
            str: The message if found, empty string otherwise.
        """

        results = []

        for memory_uri, predicate, _ in self.graph.triples((None, None, Literal(search_term))):
            memory_id = str(memory_uri).split("/")[-1]
            self.usage_counter[memory_id] += 1
            memory = {}
            keys = [str(predicate).split("/")[-1] for predicate in self.graph.predicates(subject=memory_uri)]
            for key in keys:
                predicate = URIRef(str(self.namespace) + key)
                memory[key] = str(self.graph.value(subject=memory_uri, predicate=predicate))
            results.append(memory)

        self.prune()

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
            memory_id = str(memory_uri).split("/")[-1]
            del self.usage_counter[memory_id]
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

        memories_to_remove = []

        for memory_id, usage_count in self.usage_counter.items():
            if usage_count >= self.SEARCH_THRESHOLD:
                memory_uri = URIRef(self.namespace + memory_id)
                memories_to_remove.append(memory_uri)

        for memory_uri in memories_to_remove:
            self.graph.remove((memory_uri, None, None))
            self.graph.remove((None, None, memory_uri))
            memory_id = memory_uri.split("/")[-1]
            del self.usage_counter[memory_id] 