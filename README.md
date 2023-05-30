# llm-agent-swarm
A framework to create an army of text-based AI agents whose goal is to accomplish a mission.

## Introduction
Agent Swarm is a collection of Python scripts that are intended to act as a versatile, extensible framework for creating a swarm of autonomous AI agents, each with their own distinct roles, to complete a given project. This is a passion project that is inspired by Auto-GPT and babyAGI. I felt I could write something that was in the spirit of both of those amazing and groundbreaking projects, but with a different spin, where the user has full control over the agents, what they do, how they behave, how many, and using which interfaces.

### Agent Swarm can currently:
* Generate a starter collection of two or more AI agents to accomplish a common task. (At lesat two must exist to provide feedback to one another.)
* Articulate agents in an administrative heirchy where the user is the apex (optionally).
* Give each agent it's own independent graph database memory.
* Each agent tracks conversations between other agents independently. But the agent has the power to discover information about a given topic from any conversation had with it by another agent (or the user).
* Basic expandability to use any model. A driver currently exists for the Text Generator WebUI API, and the OpenAI API.

### Agent Swarm will shortly:
* Expand the agent's memory to a dual RDF-Vector structure. Initiate a semantic search in the vector database and pick top 3 results, then back-track to RDF to discover additional details. Organize chronologically and summarize to be included in the conversation history between agents. By using this approach, details on a topic from *any* agent are included in one agent's conversation, lowering the need for the agent to remember details between agents. By taking nearest neighbors in both the RDF and vector, a broad net is cast. By enabling chronological order, sequence of events and cause-effect details are retained.
* Enable model driver configuration by agent. For example: use the default local LLM driver for agents, then add a summarizer agent that relies on GPT-3 Ada, a coding agent that relies on a codex model, while another agent relies on a storyteller agent for creativity.
* Implement a plugin-based command framework. Use an agent to interpret command orders from other agents, then leverage that agent to interpret the results.
* Implement the memory module (after extensive test driving) in Chat APIs to enable large pseudo-contexts.
* Convert the existing memory module into a plugin, and enable the addition of other memory plugins. Allow each agent to be assigned a memory type.
* Cap the number of agents, and the number of organizational layers
* Move user console information to an API that can stream details of what is happening to anything--web, desktop, database, logger, etc. Support more than one destination at a time so people can BYOI (bring your own interface)

## Getting Started
Coming after I create templates and have code that won't eat your homework.