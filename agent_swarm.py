import threading
import queue
from agent.agent import Agent
from chat_api.chat_api_tgwui import TgwuiApi
from config_manager.config_manager import ConfigManager
from colorama import Fore, Back, Style

class AgentSwarm():
    """
    AgentSwarm is a collection of agents designed to complete a project or achieve a goal.
    """

    def __init__(self, chat_api = TgwuiApi(), configuration = ConfigManager()):
        
        """
        Constructor for AgentSwarm
        
        Args:
            chat_api (TgwuiApi, optional): The chat API. Defaults to TgwuiApi()
            configuration (ConfigManager, optional): The configuration manager. Defaults to ConfigManager()
        """

        # Constants
        self.CMD_EXIT = 'exit'

        # Utilities and data
        self.chat_api = chat_api
        self.configuration = configuration
        self.user_string = str(self.configuration.get_property('user_string'))
        self.bot_string = str(self.configuration.get_property('bot_string'))
        self.sign_on_template = str(self.configuration.get_property('sign_on_template'))
        self.project = str(self.configuration.get_project())

        # Agents
        self.agents = self.create_agents_fron_config()
        self.dialog_queue = []

        # Message queue management
        self.message_queue = queue.Queue()
        self.should_continue = True

        self.start_loop()


    def start_loop(self):

        """
        Loop through all agents and retrieve messages to deliver. If the user is the recipient, 
        add to the dialog queue. If the user presses ESC, exit the loop.
        """

        ui_thread = threading.Thread(target=self.user_interface)
        ui_thread.start()

        while self.should_continue:
            # Loop through agents in a dictionary and deliver messages
            for name, agent in self.agents.items():
                messages = agent.deliver()
                if messages:
                    for message in messages:
                        self.message_queue.put(message)
                        
            while not self.message_queue.empty():
                message = self.message_queue.get()
                print(
                    f"{Fore.LIGHTYELLOW_EX}{message['from']}{Style.RESET_ALL}"
                    f" -> {Fore.LIGHTBLUE_EX}{message['to']}{Style.RESET_ALL}:"
                     " {message['text']}"
                )
                recipient_name = message['to']
                if recipient_name in self.agents:
                    self.agents[recipient_name].receive(message)
            
        ui_thread.join()


    def user_interface(self):
        """
        Handle user input from the main loop.
        """

        while self.should_continue:
            line = input()
            clean_line = line.strip()
            clean_line = clean_line.lower()
            if clean_line == self.CMD_EXIT:
                self.should_continue = False


    def create_agent(self, agent_definition) -> Agent:
        """
        Creates an agent from the agent definition.
        
        Args:
            agent_definition (dict): The agent definition.
            
        Returns:
            Agent: The agent.
        """

        new_agent = {}
        new_agent = Agent(self.chat_api, agent_definition, self.project, self.user_string, self.bot_string)
        new_agent.sign_on(self.sign_on_template)

        return new_agent


    def create_agents_fron_config(self) -> dict:
        """
        Creates the agents from the configuration file.
                    
        Returns:
            list: The list of agents.
        """

        new_agents = {}
        agents = self.configuration.get_agents()
        for agent in agents:
            new_agent = self.create_agent(agent)
            new_agents[new_agent.profile['name']] = new_agent

        return new_agents


if __name__ == '__main__':
    """
    Main entry point for the application.
    """

    chat_api = TgwuiApi()
    configuration = ConfigManager()
    agent_swarm = AgentSwarm(chat_api, configuration)