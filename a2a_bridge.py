#!/usr/bin/env python3
"""
A2A <-> OpenGoat Bridge
Bridges A2A protocol to OpenGoat agent execution.

This lets external A2A clients send tasks to our OpenGoat agents.
"""

import json
import subprocess
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs


class A2ABridgeHandler(BaseHTTPRequestHandler):
    """Handle A2A requests and forward to OpenGoat agents."""

    AGENT_MAP = {
        "researcher": "researcher",
        "writer": "writer",
    }

    def _send_json(self, status: int, data: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode()
        
        try:
            request = json.loads(body)
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        method = request.get("method", "")
        
        if method == "a2a/task":
            self._handle_task(request)
        else:
            self._send_json(404, {"error": f"Unknown method: {method}"})

    def _handle_task(self, request: dict):
        """Forward task to OpenGoat agent."""
        params = request.get("params", {})
        task_id = request.get("id", "unknown")
        
        sender = params.get("sender", "unknown")
        action = params.get("action", "")
        input_data = params.get("input", {})
        
        # Determine target agent from sender (or could be explicit)
        target = self._determine_target_agent(action, input_data)
        
        if not target:
            self._send_json(400, {"error": "Could not determine target agent"})
            return

        print(f"🌉 Bridge: {sender} -> {target['agent_id']} (action: {action})")

        # Execute via OpenGoat
        result = self._execute_agent(target["agent_id"], action, input_data)
        
        response = {
            "jsonrpc": "2.0",
            "id": task_id,
            "result": {
                "taskId": task_id,
                "status": "completed",
                "output": result
            }
        }
        
        self._send_json(200, response)

    def _determine_target_agent(self, action: str, input_data: dict) -> dict:
        """Map action/input to target OpenGoat agent."""
        action_lower = action.lower()
        input_str = str(input_data).lower()
        
        # Map actions to agents (in priority order)
        # Code actions
        if any(kw in action_lower for kw in ["code", "program", "implement", "build", "function"]):
            return {"agent_id": "code", "name": "Code Agent"}
        if "code" in input_str or "program" in input_str:
            return {"agent_id": "code", "name": "Code Agent"}
            
        # Data actions
        if any(kw in action_lower for kw in ["data", "analyze", "analytics", "query", "stats"]):
            return {"agent_id": "data", "name": "Data Agent"}
        if "analyze" in input_str or "analytics" in input_str or "data" in input_str:
            return {"agent_id": "data", "name": "Data Agent"}
            
        # API/integration actions
        if any(kw in action_lower for kw in ["api", "integration", "webhook", "connect"]):
            return {"agent_id": "api", "name": "API Agent"}
            
        # Research actions
        if any(kw in action_lower for kw in ["research", "search", "find"]):
            return {"agent_id": "researcher", "name": "Researcher"}
        if "research" in input_str or "find" in input_str:
            return {"agent_id": "researcher", "name": "Researcher"}
            
        # Writing actions
        if any(kw in action_lower for kw in ["write", "document", "draft", "edit", "create"]):
            return {"agent_id": "writer", "name": "Writer"}
        if "write" in input_str or "document" in input_str:
            return {"agent_id": "writer", "name": "Writer"}
        
        # Default to researcher
        return {"agent_id": "researcher", "name": "Researcher"}

    def _execute_agent(self, agent_id: str, action: str, input_data: dict) -> dict:
        """Execute task via OpenGoat CLI."""
        
        # Build prompt for the agent
        if action == "research":
            prompt = input_data.get("query", input_data.get("topic", ""))
        elif action == "write":
            prompt = f"Write about: {input_data.get('topic', input_data.get('content', ''))}"
        else:
            prompt = f"Action: {action}\nInput: {json.dumps(input_data)}"

        # Run via OpenGoat
        cmd = ["opengoat", "agent", "run", agent_id, "--message", prompt]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                # Parse output - last line is usually the response
                output = result.stdout.strip()
                if output:
                    return {"result": output, "agent": agent_id}
                return {"result": "Task completed", "agent": agent_id}
            else:
                return {"error": result.stderr, "agent": agent_id}
                
        except subprocess.TimeoutExpired:
            return {"error": "Task timed out", "agent": agent_id}
        except Exception as e:
            return {"error": str(e), "agent": agent_id}

    def log_message(self, format, *args):
        print(f"[Bridge] {format % args}")


def run_bridge(port: int = 9101):
    """Start the A2A <-> OpenGoat bridge."""
    server = HTTPServer(("0.0.0.0", port), A2ABridgeHandler)
    print(f"🌉 A2A Bridge running on http://localhost:{port}")
    print(f"   Maps A2A tasks to OpenGoat agents (researcher, writer)")
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Bridge shutting down...")
        server.shutdown()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9101
    run_bridge(port)
