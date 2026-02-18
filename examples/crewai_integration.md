# A2A Protocol Integration: CrewAI

This example shows how to use A2A Protocol with CrewAI crews.

## Installation

```bash
pip install a2a-protocol crewai crewai-tools
```

## Example: CrewAI Crew with A2A Agents

```python
"""
CrewAI + A2A Integration
========================
A CrewAI crew where agents can delegate to external A2A agents.
"""

from crewai import Agent, Task, Crew, Process
from a2a_sdk import A2AAgent
import json


class A2AAgentTool:
    """
    Tool for CrewAI agents to interact with A2A agents.
    """
    
    def __init__(self, directory_url: str = "http://localhost:8080"):
        self.directory_url = directory_url
        self.name = "a2a_delegate"
        self.description = """
        Delegate tasks to external AI agents via A2A Protocol.
        
        Args:
            capabilities: List of capabilities needed (e.g., ['code', 'research'])
            action: The action to perform
            input_data: Task input as dict
        
        Returns:
            Task result from the external agent
        """
    
    def run(self, capabilities: list, action: str, input_data: dict) -> str:
        """Execute task via A2A Protocol."""
        # Create delegator agent
        delegator = A2AAgent(
            agent_id="crewai-delegator",
            name="CrewAI Delegator",
            capabilities=["delegate"],
            directory_url=self.directory_url
        )
        
        # Discover agent with needed capabilities
        agent = delegator.discover(capabilities)
        if not agent:
            return f"No agent found with capabilities: {capabilities}"
        
        # Send task
        result = delegator.send_task(
            agent["agentId"],
            action,
            input_data
        )
        
        return json.dumps(result, indent=2)


# Create A2A tool
a2a_tool = A2AAgentTool()

# Define a researcher agent that can use A2A
researcher = Agent(
    role="Researcher",
    goal="Find the best information on any topic",
    backstory="""
    You are an expert researcher with access to external AI agents.
    When you need specialized research, you can delegate to 
    external agents via A2A Protocol.
    """,
    verbose=True,
    tools=[a2a_tool]
)

# Define a writer agent
writer = Agent(
    role="Writer",
    goal="Create engaging content based on research",
    backstory="""
    You are a skilled writer who creates compelling content.
    You work with the researcher to produce high-quality articles.
    """,
    verbose=True
)

# Define tasks
research_task = Task(
    description="Research the latest developments in AI agents",
    agent=researcher,
    expected_output="A comprehensive research report"
)

write_task = Task(
    description="Write an article based on the research",
    agent=writer,
    expected_output="A well-written article"
)

# Create crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
    verbose=True
)

# Execute
result = crew.kickoff()
print(result)
```

## CrewAI Agent as A2A Service

```python
"""
Expose a CrewAI agent as an A2A service.
"""

from crewai import Agent, Task, Crew
from a2a_sdk import A2AServer
from langchain_openai import ChatOpenAI

# Create CrewAI agent
llm = ChatOpenAI(model="gpt-4")

coder = Agent(
    role="Senior Coder",
    goal="Write high-quality code",
    backstory="You are an expert programmer.",
    llm=llm
)

# Wrap as A2A agent
a2a_server = A2AServer(
    agent_id="crewai-coder",
    name="CrewAI Coder Agent",
    capabilities=["code", "debug", "review"],
    port=9001
)

@a2a_server.handle_task
def handle_code(action, input_data, sender):
    if action == "write_code":
        # Create a task for the CrewAI agent
        task = Task(
            description=input_data.get("prompt", ""),
            agent=coder
        )
        crew = Crew(agents=[coder], tasks=[task])
        result = crew.kickoff()
        return {"code": str(result)}
    
    elif action == "debug":
        code = input_data.get("code", "")
        task = Task(
            description=f"Debug and fix this code:\n{code}",
            agent=coder
        )
        crew = Crew(agents=[coder], tasks=[task])
        result = crew.kickoff()
        return {"fixed": str(result)}
    
    return {"error": "Unknown action"}

# Run
print("Starting CrewAI Coder Agent on port 9001...")
a2a_server.run()
```

## Hybrid Crew: Internal + A2A Agents

```python
"""
Mix CrewAI agents with external A2A agents in one crew.
"""

from crewai import Agent, Task, Crew, Process
from a2a_sdk import A2AAgent

# Internal CrewAI agent
internal_researcher = Agent(
    role="Internal Researcher",
    goal="Conduct basic research",
    backstory="You research topics thoroughly."
)

# Task that uses external A2A agent
def research_with_a2a(topic: str) -> str:
    """Use external agent for specialized research."""
    agent = A2AAgent(
        agent_id="hybrid-delegator",
        name="Hybrid Delegator",
        capabilities=["deep-research"]
    )
    
    external = agent.discover(["deep-research"])
    if external:
        result = agent.send_task(
            external["agentId"],
            "research",
            {"topic": topic}
        )
        return result.get("output", {})
    return {"error": "No external agent found"}

# Use in a task
research_task = Task(
    description="Research AI safety using both internal and external agents",
    agent=internal_researcher,
    expected_output="Comprehensive research report"
)

crew = Crew(
    agents=[internal_researcher],
    tasks=[research_task],
    process=Process.sequential
)

result = crew.kickoff()
```

## See Also

- [A2A Protocol Specification](../SPEC.md)
- [CrewAI Documentation](https://docs.crewai.com/)
