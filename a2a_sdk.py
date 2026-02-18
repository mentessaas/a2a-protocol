#!/usr/bin/env python3
"""
A2A Python SDK - MVP (stdlib only, no external deps)
Simple library for building A2A-enabled agents.

Usage:
    from a2a_sdk import A2AAgent
    
    agent = A2AAgent(
        agent_id="my-agent",
        name="My Agent",
        capabilities=["search", "summarize"]
    )
    agent.register("http://localhost:8081")
    
    # Find another agent
    other = agent.discover(["code"])
    
    # Send task
    result = agent.send_task(other["agentId"], "do something", {"input": "..."})
"""

import json
import uuid
import urllib.request
import urllib.error
from typing import Optional, Callable


def _post(url: str, data: dict) -> dict:
    """Make POST request."""
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "message": e.read().decode()}


def _get(url: str) -> dict:
    """Make GET request."""
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}"}


class A2AAgent:
    """A2A-enabled agent."""

    def __init__(
        self,
        agent_id: str,
        name: str,
        capabilities: list,
        directory_url: str = "http://localhost:8080"
    ):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.directory_url = directory_url.rstrip("/")
        self.endpoint = None

    def register(self, endpoint: str):
        """Register this agent with the directory."""
        self.endpoint = endpoint
        result = _post(
            f"{self.directory_url}/a2a/register",
            {
                "agentId": self.agent_id,
                "name": self.name,
                "capabilities": self.capabilities,
                "endpoint": endpoint
            }
        )
        if "error" in result:
            raise RuntimeError(f"Registration failed: {result}")
        print(f"✅ Registered: {self.agent_id}")
        return result

    def discover(self, wanted_capabilities: list) -> Optional[dict]:
        """Discover agents with specified capabilities."""
        result = _post(
            f"{self.directory_url}/a2a/discover",
            {"capabilities": wanted_capabilities}
        )
        agents = result.get("agents", [])
        if not agents:
            return None
        return agents[0]

    def send_task(self, target_agent_id: str, action: str, input_data: dict) -> dict:
        """Send a task to another agent."""
        task_id = str(uuid.uuid4())
        
        # Get target agent's endpoint
        target = _get(f"{self.directory_url}/a2a/agents/{target_agent_id}")
        if "error" in target:
            raise ValueError(f"Agent not found: {target_agent_id}")
        
        target_endpoint = target["endpoint"]
        
        # Send task to target agent
        task_request = {
            "jsonrpc": "2.0",
            "id": task_id,
            "method": "a2a/task",
            "params": {
                "taskId": task_id,
                "action": action,
                "sender": self.agent_id,
                "input": input_data
            }
        }
        
        return _post(target_endpoint, task_request)


class A2AServer:
    """Simple HTTP server for A2A agents."""

    def __init__(self, agent_id: str, name: str, capabilities: list, port: int):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.port = port
        self._task_handler = None
        self.endpoint = f"http://localhost:{port}"

    def handle_task(self, func: Callable):
        """Decorator to register a task handler."""
        self._task_handler = func
        return func

    def run(self):
        """Run the agent server."""
        from http.server import HTTPServer, BaseHTTPRequestHandler
        
        task_handler = self._task_handler  # Capture for closure
        
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode()
                request = json.loads(body)
                
                jsonrpc_method = request.get("method", "")
                task_id = request.get("id")
                
                if jsonrpc_method == "a2a/task":
                    params = request.get("params", {})
                    task_action = params.get("action")
                    input_data = params.get("input", {})
                    sender = params.get("sender")
                    
                    # Call task handler
                    if task_handler:
                        result = task_handler(
                            action=task_action,
                            input_data=input_data,
                            sender=sender
                        )
                        
                        response = {
                            "jsonrpc": "2.0",
                            "id": task_id,
                            "result": {
                                "taskId": params.get("taskId"),
                                "status": "completed",
                                "output": result
                            }
                        }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "id": task_id,
                            "error": {
                                "code": -32001,
                                "message": "No handler registered"
                            }
                        }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": task_id,
                        "error": {
                            "code": -32601,
                            "message": "Method not found"
                        }
                    }
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            
            def log_message(self, format, *args):
                pass  # Suppress logging

        server = HTTPServer(("0.0.0.0", self.port), Handler)
        print(f"🤖 Agent '{self.agent_id}' running on port {self.port}")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.shutdown()


if __name__ == "__main__":
    print("📦 A2A Python SDK loaded")
    print("   Classes: A2AAgent, A2AServer")
