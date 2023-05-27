from agent.agent import Agent
from chat_api.chat_api_tgwui import TgwuiApi
from config_manager.config_manager import ConfigManager

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

        # Utilities and data
        self.chat_api = chat_api
        self.configuration = configuration
        self.user_string = str(self.configuration.get_property('user_string'))
        self.bot_string = str(self.configuration.get_property('bot_string'))
        self.sign_on_template = str(self.configuration.get_property('sign_on_template'))
        self.project = str(self.configuration.get_project())

        # Agents
        self.agents = self.create_agents_fron_config()


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


    def create_agents_fron_config(self) -> list:
        """
        Creates the agents from the configuration file.
                    
        Returns:
            list: The list of agents.
        """

        new_agents = []
        agents = self.configuration.get_agents()
        for agent in agents:
            new_agent = self.create_agent(agent)
            new_agents.append(new_agent)

        return new_agents


if __name__ == '__main__':
    """
    Main entry point for the application.
    """

    chat_api = TgwuiApi()
    configuration = ConfigManager()
    agent_swarm = AgentSwarm(chat_api, configuration)