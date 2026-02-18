# A2A Protocol Examples

Practical examples and integrations for the A2A Protocol.

## Quick Examples

### Python Basic
```python
from a2a_sdk import A2AAgent

agent = A2AAgent("my-agent", "My Agent", ["search"])
agent.register("http://localhost:9001")

# Discover another agent
other = agent.discover(["code"])

# Send task
result = agent.send_task(other["agentId"], "do_something", {"input": "data"})
```

### Multi-Agent Demo
See `demo_multi_agent.py` - Two agents collaborating.

## Integrations

### LangChain
- File: `langchain_integration.md`
- Shows how to:
  - Use A2A delegation from LangChain agents
  - Expose LangChain chains as A2A services

### CrewAI
- File: `crewai_integration.md`
- Shows how to:
  - Create A2A tools for CrewAI agents
  - Mix internal and external agents in a crew
  - Expose CrewAI agents as A2A services

### AutoGen
- File: `autogen_integration.md`
- Shows how to:
  - Delegate to A2A agents from AutoGen
  - Expose AutoGen agents as A2A services
  - Build hybrid multi-agent systems

## Running the Examples

1. Start a directory service:
   ```bash
   python a2a_directory.py
   ```

2. Run examples:
   ```bash
   python examples/demo_multi_agent.py
   ```

## Contributing

More examples welcome! Submit PRs to `github.com/mentessaas/a2a-protocol`
