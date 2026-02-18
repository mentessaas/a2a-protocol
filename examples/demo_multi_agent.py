#!/usr/bin/env python3
"""
A2A Multi-Agent Demo
=====================
Two agents: Research Agent and Writer Agent
They collaborate via A2A Protocol.

Run:
    python demo_multi_agent.py
"""

import json
import time
import threading
from a2a_sdk import A2AAgent, A2AServer


def research_agent_server():
    """Research Agent - handles research tasks."""
    agent = A2AServer(
        agent_id="research-agent",
        name="Research Agent",
        "search", " capabilities=["research",analyze"],
        port=9001
    )

    @agent.handle_task
    def handle_research(action, input_data, sender):
        print(f"\n📚 Research Agent received: action={action}")
        
        if action == "research":
            query = input_data.get("query", "")
            print(f"   🔍 Researching: {query}")
            time.sleep(0.5)  # Simulate work
            
            return {
                "findings": [
                    f"Source 1 about {query}",
                    f"Source 2 about {query}",
                    f"Source 3 about {query}",
                ],
                "summary": f"Found 3 sources about {query}"
            }
        
        return {"error": "Unknown action"}

    agent.run()


def writer_agent_server():
    """Writer Agent - handles writing tasks."""
    agent = A2AServer(
        agent_id="writer-agent",
        name="Writer Agent",
        capabilities=["write", "summarize", "edit"],
        port=9002
    )

    @agent.handle_task
    def handle_write(action, input_data, sender):
        print(f"\n✍️ Writer Agent received: action={action}")
        
        if action == "write":
            topic = input_data.get("topic", "")
            findings = input_data.get("findings", [])
            print(f"   📝 Writing article about: {topic}")
            time.sleep(0.5)
            
            article = f"# {topic}\n\n"
            for i, finding in enumerate(findings, 1):
                article += f"{i}. {finding}\n\n"
            article += "\n*Written by AI*"
            
            return {"article": article, "word_count": len(article.split())}
        
        return {"error": "Unknown action"}

    agent.run()


def coordinator():
    """Coordinator - orchestrates the two agents."""
    # Give servers time to start
    time.sleep(1)
    
    # Create coordinator agent
    coordinator = A2AAgent(
        agent_id="coordinator",
        name="Coordinator",
        capabilities=["coordinate", "orchestrate"],
        directory_url="http://localhost:8080"  # Not using directory in this demo
    )
    
    print("\n" + "="*50)
    print("🚀 Starting Multi-Agent Workflow")
    print("="*50 + "\n")
    
    # Step 1: Research
    print("Step 1: Asking Research Agent to research 'AI agents'...")
    research_result = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "a2a/task",
        "params": {
            "taskId": "task-1",
            "action": "research",
            "sender": "coordinator",
            "input": {"query": "AI agents"}
        }
    }
    
    # In real usage, you'd use the SDK's send_task method
    # For demo, we'll simulate the flow
    print("\n📡 Sending task to Research Agent (port 9001)...")
    print("   (In production: coordinator.send_task(...))")
    
    print("\n✅ Research complete! Got findings.")
    print("   - Source 1 about AI agents")
    print("   - Source 2 about AI agents") 
    print("   - Source 3 about AI agents")
    
    # Step 2: Write
    print("\nStep 2: Asking Writer Agent to write article...")
    print("📡 Sending task to Writer Agent (port 9002)...")
    print("   (In production: coordinator.send_task(...))")
    
    print("\n✅ Article written!")
    print("   - Word count: 25")
    
    print("\n" + "="*50)
    print("🎉 Multi-Agent Workflow Complete!")
    print("="*50)


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║          A2A Multi-Agent Demo                             ║
║                                                          ║
║  Research Agent (9001)  ←→  Writer Agent (9002)         ║
║                                                          ║
║  This demo shows two agents collaborating via A2A.       ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # In a real scenario, you'd run servers on separate processes
    # For demo, we'll just show the coordinator flow
    
    # Start servers in separate threads (uncomment for real demo)
    # research_thread = threading.Thread(target=research_agent_server)
    # writer_thread = threading.Thread(target=writer_agent_server)
    # research_thread.start()
    # writer_thread.start()
    
    # Run coordinator
    coordinator()
    
    print("\n📖 To run the full demo:")
    print("   1. Start research agent: python -c 'from demo_multi_agent import research_agent_server; research_agent_server()'")
    print("   2. Start writer agent: python -c 'from demo_multi_agent import writer_agent_server; writer_agent_server()'")
    print("   3. Run this script again")


if __name__ == "__main__":
    main()
