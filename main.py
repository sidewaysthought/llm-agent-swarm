import argparse
import datetime
import json
import logging
import os
import threading
import queue
import secrets
import spacy
import time
import string
from agent.main import Agent
from chat_api.tgwui.main import TgwuiApi
from chat_api.openai_completion.main import OpenAIApiCompletion
from chat_api.openai_chat.main import OpenAIApiChat
from commands.main import Commands
from config_manager.main import ConfigManager
from colorama import Fore, Back, Style
from dotenv import load_dotenv
from logger.main import LoggerConfig

class AgentSwarm():
    """
    AgentSwarm is a collection of agents designed to complete a project or achieve a goal.
    """

    def __init__(self, configuration = ConfigManager()):
        
        """
        Constructor for AgentSwarm
        
        Args:
            chat_api (TgwuiApi, optional): The chat API. Defaults to TgwuiApi()
            configuration (ConfigManager, optional): The configuration manager. Defaults to ConfigManager()
        """

        # Constants
        self.CMD_EXIT = 'exit'
        self.CHAT_API_TGWUI = 'tgwui'
        self.CHAT_API_OPENAI_COMPLETION = 'openai_completion'
        self.CHAT_API_OPENAI_CHAT = 'openai_chat'
        self.SYSTEM_NAME = 'System'

        # Variables
        self.debug_enabled = False

        # Arguments
        self.setup_arg_parser()

        # Logging
        self.debug_enabled = False
        logger_config = LoggerConfig(self.debug_enabled)
        self.logger = logger_config.setup_logger()

        # Configuration
        load_dotenv()
        self.configuration = configuration
        self.msg_no_agent_named = str(self.configuration.get_property('redirect_failure_string'))
        self.user_string = str(self.configuration.get_property('user_string'))
        self.bot_string = str(self.configuration.get_property('bot_string'))
        self.sign_on_template = str(self.configuration.get_property('sign_on_template'))
        self.project = str(self.configuration.get_project())

        # Utilities and data
        self.session_id = self.generate_session_id()
        self.lang_processor = spacy.load("en_core_web_sm")

        # Command management
        self.command_controller = Commands()

        # Agents
        self.agents = self.create_agents_fron_config()
        self.dialog_queue = []

        # Message queue management
        self.message_queue = queue.Queue()
        self.should_continue = True

        self.start_loop()


    def setup_arg_parser(self):

        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", help="Enable debug logging", action="store_true")
        args = parser.parse_args()

        if args.debug:
            self.debug_enabled = True


    def generate_session_id(self) -> str:
        """
        Generate a session ID for the agents.
        
        Returns:
            str: The session ID.
        """

        # Generate a session ID, 8 alphanumeric characters
        

        alphabet = string.ascii_letters + string.digits
        session_id = ''.join(secrets.choice(alphabet) for i in range(8))
        return session_id


    def start_loop(self):

        """
        Loop through all agents and retrieve messages to deliver. If the user is the recipient, 
        add to the dialog queue. If the user presses ESC, exit the loop.
        """

        ui_thread = threading.Thread(target=self.user_interface)
        ui_thread.start()

        while self.should_continue:

            # Check for messages to deliver
            for _, agent in self.agents.items():
                messages = agent.deliver()
                if messages:
                    for message in messages:
                        # If the message is sent to system, redirect to other agents
                        if message['to'] == self.SYSTEM_NAME:
                            redirected_msgs = self.redirect_system_msg(message)
                            if redirected_msgs:
                                # Messaages are sent to every named agent.
                                # TODO: get more granular on who to send messages to
                                # TODO: handle "everyone" and "anyone" to go to agent subordinates
                                for msg in redirected_msgs:
                                    self.message_queue.put(msg)
                        # The message is going to a named agent
                        else:
                            self.message_queue.put(message)
            
            # Deliver messages to the agent
            while not self.message_queue.empty():
                message = self.message_queue.get()
                recipient_name = message['to']
                self.display_message(message)
                if recipient_name in self.agents:
                    self.agents[recipient_name].receive(message)

            # Process messages from agents
            for _, agent in self.agents.items():
                print(f'Processing message queue for {Fore.YELLOW}{agent.profile["name"]}{Style.RESET_ALL}...')
                messages = agent.interpret()
            
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


    def display_message(self, message_package):
        """
        Display a message to the user.
        
        Args:
            message (dict): The message to display.
        """
        print(f'{Fore.GREEN}{message_package["from"]}{Style.RESET_ALL} -> {Fore.YELLOW}{message_package["to"]}{Style.RESET_ALL}: {message_package["message"]}')


    def create_agent(self, agent_definition) -> Agent:
        """
        Creates an agent from the agent definition.
        
        Args:
            agent_definition (dict): The agent definition.
            
        Returns:
            Agent: The agent.
        """

        # Deal with Chat API
        chat_driver = self.configuration.get_property('chat_api')
        openai_model_agent = str(self.configuration.get_property('openai_model_chat'))
        openai_model_completion = str(self.configuration.get_property('openai_model_completion'))
        if chat_driver == self.CHAT_API_OPENAI_CHAT:
            self.chat_api = OpenAIApiChat(model_string=openai_model_agent)
        elif chat_driver == self.CHAT_API_OPENAI_COMPLETION:
            self.chat_api = OpenAIApiCompletion(model_string=openai_model_completion)
        else:
            self.chat_api = TgwuiApi(user_string=self.user_string, agent_string=self.bot_string)
            
        # Create the agent
        new_agent = Agent(chat_api=self.chat_api, agent_profile=agent_definition, project=self.project, 
                          session_id=self.session_id, commands=self.command_controller.command_strings)
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
    

    def redirect_system_msg(self, message_to_review) -> list:
        """
        Redirects system messages to the appropriate agent.
        
        Args:
            message_package (dict): The message package to interpret.
            
        Returns:
            dict: The redirected message package.
        """

        # Starting stuff
        response = []
        named_agents = []

        # Cut the message into language chunks
        document = self.lang_processor(message_to_review['message'])

        # Find named entities
        for entity in document.ents:
            if entity.text in self.agents.keys() and entity.text != message_to_review['from']:
                named_agents.append(entity.text)

        # Remove duplicates from named_agents
        named_agents = list(dict.fromkeys(named_agents))

        # Redirect the message based on the named entities.
        if len(named_agents) > 0:
            # Send to every named agent in the message
            for agent in named_agents:
                ogm = message_to_review.copy()
                ogm['to'] = agent
                response.append(ogm)
        # Bounce the message back to the agent to direct it at another agent
        else:
            ogm = message_to_review.copy()
            ogm['to'] = message_to_review['from']
            ogm['from'] = self.SYSTEM_NAME
            ogm['message'] = self.msg_no_agent_named + message_to_review['message']
            response.append(ogm)

        return response


if __name__ == '__main__':
    """
    Main entry point for the application.
    """

    # Get the full path of config.yaml, in the same directory as this Python script
    config_file = os.path.join(os.path.dirname(__file__), 'config.yaml')

    configuration = ConfigManager(config_file)
    agent_swarm = AgentSwarm(configuration)