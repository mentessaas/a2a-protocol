#!/usr/bin/env python3
"""
A2A Directory Service - MVP
Simple HTTP server for agent registration and discovery.

Run: python a2a_directory.py
"""

import json
import uuid
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# In-memory agent registry
AGENTS = {}


class A2ADirectoryHandler(BaseHTTPRequestHandler):
    """Handle A2A directory requests."""

    def _send_json(self, status: int, data: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else "{}"

        try:
            request = json.loads(body)
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        parsed = urlparse(self.path)

        # Register agent
        if parsed.path == "/a2a/register":
            self._handle_register(request)
        # Discover agents
        elif parsed.path == "/a2a/discover":
            self._handle_discover(request)
        else:
            self._send_json(404, {"error": "Unknown endpoint"})

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)

        # List all agents
        if parsed.path == "/a2a/agents":
            self._handle_list_agents()
        # Get agent info
        elif parsed.path.startswith("/a2a/agents/"):
            agent_id = parsed.path.split("/")[-1]
            self._handle_get_agent(agent_id)
        else:
            self._send_json(404, {"error": "Unknown endpoint"})

    def _handle_register(self, request: dict):
        """Register an agent."""
        required = ["agentId", "name", "capabilities", "endpoint"]
        missing = [f for f in required if f not in request]

        if missing:
            self._send_json(400, {"error": f"Missing fields: {missing}"})
            return

        agent_id = request["agentId"]
        AGENTS[agent_id] = {
            "agentId": agent_id,
            "name": request["name"],
            "capabilities": request["capabilities"],
            "endpoint": request["endpoint"],
            "registeredAt": datetime.utcnow().isoformat() + "Z"
        }

        print(f"📋 Registered agent: {agent_id} ({request['name']})")
        self._send_json(200, {
            "status": "registered",
            "agentId": agent_id
        })

    def _handle_discover(self, request: dict):
        """Discover agents by capabilities."""
        wanted = request.get("capabilities", [])

        if not wanted:
            self._send_json(400, {"error": "No capabilities specified"})
            return

        matches = []
        for agent_id, agent in AGENTS.items():
            agent_caps = set(agent["capabilities"])
            # Check if any of the wanted capabilities match
            if any(cap in agent_caps for cap in wanted):
                matches.append(agent)

        print(f"🔍 Discovery: wanted {wanted}, found {len(matches)} agents")
        self._send_json(200, {"agents": matches})

    def _handle_list_agents(self):
        """List all registered agents."""
        self._send_json(200, {"agents": list(AGENTS.values())})

    def _handle_get_agent(self, agent_id: str):
        """Get specific agent info."""
        if agent_id in AGENTS:
            self._send_json(200, AGENTS[agent_id])
        else:
            self._send_json(404, {"error": "Agent not found"})

    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(port: int = 8080):
    """Start the A2A directory server."""
    server = HTTPServer(("0.0.0.0", port), A2ADirectoryHandler)
    print(f"🚀 A2A Directory Service running on http://localhost:{port}")
    print(f"   Endpoints:")
    print(f"   POST /a2a/register   - Register an agent")
    print(f"   POST /a2a/discover  - Discover agents by capability")
    print(f"   GET  /a2a/agents    - List all agents")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    run_server()
