# Commands Manual

Commands are the mechanism agents use to interact with the Agent Swarm core, the hardware, the internet and
anything else users might think of.

The command system is built to be bare-bones, and facilitate flexibility as well as facilitate the development
of commands with minimal difficulty.

## How commands work

Commands are intended to be called by agents, who learn of commands by including a reference to the agent in the 
Agent Swarm config.yaml file. In simple swarms of two or three agents, one agent can be put in-charge of making
all command calls. Use the ```<commands>``` symbol to include all registered commands.

```
  - name: SystemAgent
    supervisor: ChiefExecAgent
    role: Interact with the system the swarm is on, interact with the internet, and manage agents.
    guidance: "You are responsible for accepting requests to execute commands by any agent. You can also
      create, delete, and modify agents.
      
      Your commands:
      <commands>"           # list all commands.
```

In swarms that potentially have lots of agents that focus on different things, a list of a subset of commands
can be included in the agent's config.yaml entry.

```
  - name: SystemAgent
    supervisor: ChiefExecAgent
    role: Interact with the system the swarm is on, interact with the internet, and manage agents.
    guidance: "You are responsible for accepting requests to execute commands by any agent. You can also
      create, delete, and modify agents.
      
      Your commands:
      <commands:agents>"    # list commands that are associated with agents.
```

In this example, agents is the "command type".

### Command Types

A command type is one or more keywords that is associated with a command. They are basically ad-hoc (user definable)
but out of the box, commands have one or more of these specific keywords:

* user - Interact with the user in some way
* internet - Send to/receive from the internet
* system - Interact with the system's hardware
* agent - Manage agents

Again, commands can have one or more command type.

```
# Command definition
name: ask_user
description: Ask the system's user for input
command_type:
  - type1
  - type2 
```

## Developing A New Command

1. Make a new folder inside of this one. Best practice: name it after the command you are creating
2. Copy config-template.yaml into your new folder, and rename it config.yaml.
3. Edit config.yaml to match the details of your new command. This information will be shared with the 
   agent, and will define what information is needed to call the command.
4. In the folder, make an ```__init__.py``` file and a ```main.py``` file. 
5. Whatever you place in these files is up to you, but the ```main.py``` file must contain the following:
   ```
   from commands.main import Command

   class YourCommand(Command):
   ```
   A more complete template is below.

That's it! As long as your command returns a result based on this format, the command response will
be sent to the agent that called it:
```
{
    'status': self.STATUS_OK,                       # or self.STATUS_ERROR
    'message': 'This is a summary statement',       # contextualize the response for the agent
    'data': something                               # this can be anything, but must match config.yaml       
}
```
   
