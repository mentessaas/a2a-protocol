# A2A Protocol Integration: AutoGen

This example shows how to use A2A Protocol with AutoGen agents.

## Installation

```bash
pip install a2a-protocol pyautogen
```

## Example: AutoGen Agent calling external A2A agent

```python
"""
AutoGen + A2A Integration
=========================
AutoGen agents that can delegate to external A2A agents.
"""

from autogen import ConversableAgent, Agent
from a2a_sdk import A2AAgent
import json


class A2AAgentWrapper:
    """
    Wrapper to use A2A agents within AutoGen.
    """
    
    def __init__(self, directory_url: str = "http://localhost:8080"):
        self.directory_url = directory_url
    
    def create_delegation_function(self, capabilities: list, action: str):
        """
        Create a function that delegates to an A2A agent.
        """
        def delegate(task_input: dict) -> str:
            # Create delegator
            delegator = A2AAgent(
                agent_id="autogen-delegator",
                name="AutoGen Delegator",
                capabilities=["delegate"],
                directory_url=self.directory_url
            )
            
            # Discover agent
            agent = delegator.discover(capabilities)
            if not agent:
                return f"No agent found with capabilities: {capabilities}"
            
            # Send task
            result = delegator.send_task(
                agent["agentId"],
                action,
                task_input
            )
            
            return json.dumps(result, indent=2)
        
        return delegate


# Create A2A wrapper
a2a_wrapper = A2AAgentWrapper()

# Create delegation function
delegate_to_researcher = a2a_wrapper.create_delegation_function(
    capabilities=["research"],
    action="research"
)

delegate_to_coder = a2a_wrapper.create_delegation_function(
    capabilities=["code"],
    action="write_code"
)

# AutoGen agent with A2A delegation
assistant = ConversableAgent(
    name="assistant",
    system_message="""You are a helpful assistant.
    
    You have access to external AI agents via A2A Protocol:
    - delegate_to_researcher(topic): Delegate research tasks
    - delegate_to_coder(prompt): Delegate coding tasks
    
    Use these functions when you need specialized capabilities.""",
    llm_config={
        "model": "gpt-4",
        "api_key": "YOUR_OPENAI_API_KEY"
    },
    function_map={
        "delegate_to_researcher": delegate_to_researcher,
        "delegate_to_coder": delegate_to_coder
    }
)

# Example conversation
response = assistant.generate_reply(
    messages=[{
        "role": "user",
        "content": "Research the latest in AI agents and then write code for a simple agent."
    }]
)
print(response)
```

## AutoGen Agent as A2A Service

```python
"""
Expose an AutoGen agent as an A2A service.
"""

from autogen import ConversableAgent, Agent
from a2a_sdk import A2AServer
from langchain_openai import ChatOpenAI

# Create AutoGen agent
llm_config = {
    "model": "gpt-4",
    "api_key": "YOUR_OPENAI_API_KEY"
}

coder_agent = ConversableAgent(
    name="autogen-coder",
    system_message="You are an expert programmer. Write clean, efficient code.",
    llm_config=llm_config
)

# Wrap as A2A agent
a2a_server = A2AServer(
    agent_id="autogen-coder-a2a",
    name="AutoGen Coder Agent",
    capabilities=["code", "debug", "review"],
    port=9002
)

@a2a_server.handle_task
def handle_code(action, input_data, sender):
    if action == "write_code":
        prompt = input_data.get("prompt", "")
        # Use AutoGen to generate code
        response = coder_agent.generate_reply(
            messages=[{"role": "user", "content": prompt}]
        )
        return {"code": str(response)}
    
    elif action == "debug":
        code = input_data.get("code", "")
        response = coder_agent.generate_reply(
            messages=[{
                "role": "user",
                "content": f"Debug this code:\n\n{code}\n\nExplain any issues."
            }]
        )
        return {"debugged": str(response)}
    
    return {"error": "Unknown action"}

# Run
print("Starting AutoGen Coder Agent on port 9002...")
a2a_server.run()
```

## Multi-Agent Setup: AutoGen + A2A

```python
"""
Complete setup: AutoGen agents working with external A2A agents.
"""

from autogen import ConversableAgent, GroupChat, GroupChatManager
from a2a_sdk import A2AAgent

# Internal AutoGen agents
assistant = ConversableAgent(
    name="Assistant",
    system_message="You coordinate tasks and delegate to specialists.",
    llm_config={"model": "gpt-4", "api_key": "YOUR_KEY"}
)

coder = ConversableAgent(
    name="Coder",
    system_message="You write code. Use external agents for testing.",
    llm_config={"model": "gpt-4", "api_key": "YOUR_KEY"}
)

writer = ConversableAgent(
    name="Writer",
    system_message="You write documentation.",
    llm_config={"model": "gpt-4", "api_key": "YOUR_KEY"}
)

# Function to call external A2A agents
def call_external_a2a(capabilities: list, task: str, action: str):
    """Call external A2A agent."""
    agent = A2AAgent(
        agent_id="autogen-coordinator",
        name="AutoGen Coordinator",
        capabilities=["coordinate"]
    )
    
    external = agent.discover(capabilities)
    if external:
        result = agent.send_task(
            external["agentId"],
            action,
            {"task": task}
        )
        return result
    return {"error": "No external agent found"}

# Register the function with coder
coder.register_for_llm(
    name="call_external_tester",
    description="Call external A2A agent for testing"
)(lambda task: call_external_a2a(["test"], task, "test"))

# Create group chat
group_chat = GroupChat(
    agents=[assistant, coder, writer],
    messages=[],
    max_round=10
)

manager = GroupChatManager(groupchat=group_chat)

# Start conversation
assistant.initiate_chat(
    manager,
    message="Create a simple Python function and test it using external agents."
)
```

## Using A2A for Agent Discovery in AutoGen

```python
"""
Use A2A capability discovery to find the right AutoGen agent.
"""

from autogen import ConversableAgent
from a2a_sdk import A2AAgent

def find_agent_by_capability(capability: str, directory_url: str = "http://localhost:8080"):
    """Find an A2A agent with the needed capability."""
    finder = A2AAgent(
        agent_id="capability-finder",
        name="Capability Finder",
        capabilities=["find"]
    )
    
    agents = finder.discover([capability])
    return agents

# In your AutoGen agent:
def my_autogen_agent(llm_config):
    agent = ConversableAgent(
        name="Dynamic Agent",
        system_message="You dynamically find and use agents with needed capabilities."
    )
    
    # When you need a coder:
    coder = find_agent_by_capability("code")
    if coder:
        # Use the discovered coder
        pass
    
    return agent
```

## See Also

- [A2A Protocol Specification](../SPEC.md)
- [AutoGen Documentation](https://microsoft.github.io/autogen/)
