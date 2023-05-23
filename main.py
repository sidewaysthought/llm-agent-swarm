from agent.agent import Agent
from chat_api.chat_api_tgwui import TgwuiApi
from config_manager.config_manager import ConfigManager

def main():

    # Prep for agents
    chat_api = TgwuiApi('http://127.0.0.1', 5000)
    active_agents = []

    # Load configuration
    configuration = ConfigManager('config.yaml')
    
    # Create agents
    agents = configuration.get_agents()
    sign_on_template = str(configuration.get_property('sign_on_template'))
    project = str(configuration.get_property('project'))
    for agent in agents:
        new_agent = Agent(chat_api, agent['name'], agent['supervisor'], agent['role'], agent['mission'], project)
        reply = new_agent.sign_on(sign_on_template)
        active_agents.append(new_agent)
        print(reply)


if __name__ == '__main__':
    main()