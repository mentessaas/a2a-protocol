#!/usr/bin/env python3
"""
Demo: Echo Agent
A simple agent that responds to tasks.
"""

import json
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from a2a_sdk import A2AServer


def handle_task(action: str, input_data: dict, sender: str) -> dict:
    """Handle incoming tasks."""
    if action == "echo":
        return {"echoed": input_data.get("message", "no message")}
    elif action == "uppercase":
        text = input_data.get("text", "")
        return {"result": text.upper()}
    elif action == "reverse":
        text = input_data.get("text", "")
        return {"result": text[::-1]}
    elif action == "ping":
        return {"pong": True, "from": "echo-agent"}
    else:
        return {"error": f"Unknown action: {action}"}


if __name__ == "__main__":
    server = A2AServer(
        agent_id="echo-agent",
        name="Echo Agent",
        capabilities=["echo", "transform", "ping"],
        port=9001
    )
    server.handle_task(handle_task)
    server.run()
