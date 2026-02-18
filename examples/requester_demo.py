#!/usr/bin/env python3
"""
Demo: Task Requester Agent
Discovers and sends tasks to other agents.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from a2a_sdk import A2AAgent


def demo():
    """Run a demo of discovering and sending tasks."""
    
    # Create our agent
    agent = A2AAgent(
        agent_id="requester-demo",
        name="Requester Demo",
        capabilities=["request", "delegate"],
        directory_url="http://localhost:8080"
    )
    
    # Register (we don't need a server for this demo)
    # Just use the directory for discovery
    
    print("\n🔍 Discovering agents with 'echo' capability...")
    echo_agent = agent.discover(["echo"])
    
    if echo_agent:
        print(f"   Found: {echo_agent['name']} ({echo_agent['agentId']})")
        
        print("\n📤 Sending 'echo' task...")
        result = agent.send_task(
            target_agent_id=echo_agent["agentId"],
            action="echo",
            input_data={"message": "Hello from A2A!"}
        )
        print(f"   Result: {result}")
        
        print("\n📤 Sending 'uppercase' task...")
        result = agent.send_task(
            target_agent_id=echo_agent["agentId"],
            action="uppercase",
            input_data={"text": "hello a2a"}
        )
        print(f"   Result: {result}")
        
        print("\n📤 Sending 'ping' task...")
        result = agent.send_task(
            target_agent_id=echo_agent["agentId"],
            action="ping",
            input_data={}
        )
        print(f"   Result: {result}")
        
    else:
        print("   No echo agent found!")
    
    print("\n🔍 Discovering agents with 'transform' capability...")
    transform_agent = agent.discover(["transform"])
    
    if transform_agent:
        print(f"   Found: {transform_agent['name']}")
        
        print("\n📤 Sending 'reverse' task...")
        result = agent.send_task(
            target_agent_id=transform_agent["agentId"],
            action="reverse",
            input_data={"text": "a2a is working"}
        )
        print(f"   Result: {result}")
    else:
        print("   No transform agent found!")


if __name__ == "__main__":
    demo()
