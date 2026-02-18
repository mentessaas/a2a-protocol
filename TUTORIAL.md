# A2A Protocol - Getting Started Tutorial

A step-by-step guide to building multi-agent systems with A2A Protocol.

---

## What We'll Build

Two agents that work together:
1. **Research Agent** - Searches for information
2. **Writer Agent** - Writes articles based on research

By the end, you'll understand how to make agents communicate!

---

## Prerequisites

```bash
# Install Python SDK
pip install a2a-protocol

# Or clone the repo
git clone https://github.com/mentessaas/a2a-protocol.git
cd a2a-protocol
```

---

## Step 1: Start the Directory Service

The directory helps agents discover each other.

```bash
python a2a_directory.py
```

You should see:
```
📂 A2A Directory running on http://localhost:8080
```

Leave this terminal open!

---

## Step 2: Create the Research Agent

Create `research_agent.py`:

```python
from a2a_sdk import A2AServer

def main():
    agent = A2AServer(
        agent_id="research-agent",
        name="Research Agent",
        capabilities=["search", "research"],
        port=9001
    )

    @agent.handle_task
    def handle_search(action, input_data, sender):
        query = input_data.get("query", "")
        print(f"🔍 Researching: {query}")
        
        # Simulate research (replace with real API calls)
        return {
            "findings": [
                f"Source 1 about {query}",
                f"Source 2 about {query}",
            ]
        }

    print("📚 Research Agent ready on port 9001")
    agent.run()

if __name__ == "__main__":
    main()
```

Run it:
```bash
python research_agent.py
```

---

## Step 3: Create the Writer Agent

Create `writer_agent.py`:

```python
from a2a_sdk import A2AServer

def main():
    agent = A2AServer(
        agent_id="writer-agent",
        name="Writer Agent",
        capabilities=["write", "summarize"],
        port=9002
    )

    @agent.handle_task
    def handle_write(action, input_data, sender):
        topic = input_data.get("topic", "")
        findings = input_data.get("findings", [])
        
        print(f"✍️ Writing about: {topic}")
        
        article = f"# {topic}\n\n"
        for finding in findings:
            article += f"- {finding}\n"
        
        return {"article": article, "word_count": len(article.split())}

    print("✍️ Writer Agent ready on port 9002")
    agent.run()

if __name__ == "__main__":
    main()
```

Run it:
```bash
python writer_agent.py
```

---

## Step 4: Create the Coordinator

Create `coordinator.py`:

```python
from a2a_sdk import A2AAgent

def main():
    coordinator = A2AAgent(
        agent_id="coordinator",
        name="Coordinator",
        capabilities=["coordinate"],
        directory_url="http://localhost:8080"
    )
    
    # Register with directory
    coordinator.register("http://localhost:9003", "http://localhost:8080")
    
    # Discover agents
    print("\n🔍 Finding Research Agent...")
    researcher = coordinator.discover(["research"])
    print(f"   Found: {researcher['name']}")
    
    print("🔍 Finding Writer Agent...")
    writer = coordinator.discover(["write"])
    print(f"   Found: {writer['name']}")
    
    # Step 1: Ask Research Agent
    print("\n📚 Asking Research Agent to research 'AI agents'...")
    research_result = coordinator.send_task(
        researcher["agentId"],
        "search",
        {"query": "AI agents"}
    )
    print(f"   Findings: {research_result['output']['findings']}")
    
    # Step 2: Ask Writer Agent
    print("\n✍️ Asking Writer Agent to write article...")
    writer_result = coordinator.send_task(
        writer["agentId"],
        "write",
        {
            "topic": "AI Agents",
            "findings": research_result["output"]["findings"]
        }
    )
    print(f"   Article: {writer_result['output']['article'][:100]}...")
    
    print("\n🎉 Workflow complete!")

if __name__ == "__main__":
    main()
```

Run it:
```bash
python coordinator.py
```

---

## Expected Output

```
🔍 Finding Research Agent...
   Found: Research Agent
🔍 Finding Writer Agent...
   Found: Writer Agent

📚 Asking Research Agent to search 'AI agents'...
   Findings: ['Source 1 about AI agents', 'Source 2 about AI agents']

✍️ Asking Writer Agent to write article...
   Article: # AI Agents

- Source 1 about AI agents
- Source 2 about AI agents
...

🎉 Workflow complete!
```

---

## What Just Happened?

1. **Discovery** - Coordinator found agents by capability, not hardcoded IDs
2. **Communication** - Agents exchanged tasks via JSON-RPC over HTTP
3. **Collaboration** - Research → Writer workflow completed

This is the power of A2A Protocol!

---

## Next Steps

### Add More Agents
- Code Agent
- Data Analysis Agent
- Translation Agent

### Try Integrations
- [LangChain Integration](./langchain_integration.md)
- [CrewAI Integration](./crewai_integration.md)
- [AutoGen Integration](./autogen_integration.md)

### Deploy
- Use in production with HTTPS
- Add authentication
- Scale with message queues

---

## Resources

- 📖 [Specification](./SPEC.md)
- 💻 [GitHub](https://github.com/mentessaas/a2a-protocol)
- 🐦 [Twitter](https://twitter.com/mentessa)

---

*Built with 🔥 by Mentessa*
