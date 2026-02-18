# A2A Protocol Integration: LangChain

This example shows how to use A2A Protocol with LangChain agents.

## Installation

```bash
pip install a2a-protocol langchain langchain-openai
```

## Example: LangChain Agent calling external A2A agent

```python
"""
LangChain + A2A Integration
==========================
A LangChain agent that can delegate tasks to A2A-enabled agents.
"""

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from a2a_sdk import A2AAgent
import json


class A2ADelegateTool:
    """
    A LangChain tool that delegates to external A2A agents.
    """
    
    def __init__(self, directory_url: str = "http://localhost:8080"):
        self.directory_url = directory_url
        self.name = "delegate_to_agent"
        self.description = """
        Delegate a task to an external AI agent via A2A Protocol.
        Use when you need specialized capabilities (code, research, etc.).
        
        Input should be a JSON string with:
        - capabilities: list of needed capabilities (e.g., ['code', 'research'])
        - task: the task description
        - task_type: type of task (e.g., 'write_code', 'analyze_data')
        """
    
    def _run(self, query: str) -> str:
        """Execute delegation synchronously."""
        import json
        
        try:
            params = json.loads(query)
        except json.JSONDecodeError:
            return "Error: Input must be JSON string with capabilities, task, and task_type"
        
        capabilities = params.get("capabilities", [])
        task = params.get("task", "")
        task_type = params.get("task_type", "general")
        
        # Find an agent with the needed capabilities
        a2a_agent = A2AAgent(
            agent_id="langchain-delegator",
            name="LangChain Delegator",
            capabilities=["delegate"]
        )
        
        agent = a2a_agent.discover(capabilities)
        if not agent:
            return f"No agent found with capabilities: {capabilities}"
        
        # Send task to discovered agent
        result = a2a_agent.send_task(
            agent["agentId"],
            task_type,
            {"task": task}
        )
        
        return json.dumps(result, indent=2)
    
    async def _arun(self, query: str) -> str:
        """Execute delegation asynchronously."""
        return self._run(query)


# Create the tool
a2a_delegate_tool = A2ADelegateTool()

# Define prompt with A2A delegation
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful AI assistant with access to external agents.
    
    When you need specialized capabilities (coding, research, etc.), use the 
    delegate_to_agent tool to call external A2A-enabled agents.
    
    Available capabilities:
    - code: for writing or debugging code
    - research: for finding information
    - analyze: for data analysis
    - write: for content creation"""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create LLM
llm = ChatOpenAI(model="gpt-4")

# Create tools
tools = [a2a_delegate_tool]

# Create agent
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# Usage Example
if __name__ == "__main__":
    # Example: Ask agent to write code using external coder agent
    result = agent_executor.invoke({
        "input": "Write a function that calculates fibonacci numbers. Use an external coder agent."
    })
    print(result["output"])
```

## LangChain Agent as A2A Service

```python
"""
Expose a LangChain agent as an A2A service.
"""

from a2a_sdk import A2AServer
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

# Create LangChain chain
llm = ChatOpenAI(model="gpt-4")
prompt = ChatPromptTemplate.from_template("Explain {topic} in simple terms")
chain = LLMChain(llm=llm, prompt=prompt)

# Wrap as A2A agent
a2a_server = A2AServer(
    agent_id="langchain-explainer",
    name="LangChain Explainer Agent",
    capabilities=["explain", "summarize"],
    port=9000
)

@a2a_server.handle_task
def handle_explain(action, input_data, sender):
    if action == "explain":
        topic = input_data.get("topic", "")
        result = chain.run(topic=topic)
        return {"explanation": result}
    return {"error": "Unknown action"}

# Run the A2A server
print("Starting LangChain Explainer Agent on port 9000...")
a2a_server.run()
```

## See Also

- [A2A Protocol Specification](../SPEC.md)
- [LangChain Documentation](https://python.langchain.com/)
