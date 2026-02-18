#!/usr/bin/env python3
"""
A2A Protocol CLI
=================
Command-line interface for A2A Protocol.

Usage:
    a2a register <agent-id> <name> <capabilities> <endpoint> [--directory URL]
    a2a discover <capabilities> [--directory URL]
    a2a list [--directory URL]
    a2a send <agent-id> <action> <input-json> [--directory URL]
    a2a serve <agent-id> <name> <capabilities> <port>
"""

import argparse
import json
import sys
from a2a_sdk import A2AAgent, A2AServer


def cmd_register(args):
    """Register an agent with the directory."""
    capabilities = args.capabilities.split(',')
    
    agent = A2AAgent(
        agent_id=args.agent_id,
        name=args.name,
        capabilities=capabilities,
        directory_url=args.directory
    )
    
    agent.register(args.endpoint, args.directory)
    print(f"✅ Registered {args.agent_id}")


def cmd_discover(args):
    """Discover agents by capability."""
    capabilities = args.capabilities.split(',')
    
    # Use a temporary agent for discovery
    agent = A2AAgent(
        agent_id="cli-discover",
        name="CLI Discover",
        capabilities=[],
        directory_url=args.directory
    )
    
    result = agent.discover(capabilities)
    
    if result:
        print(json.dumps(result, indent=2))
    else:
        print("No agents found")


def cmd_list(args):
    """List all registered agents."""
    import urllib.request
    
    url = f"{args.directory}/a2a/agents"
    try:
        with urllib.request.urlopen(url) as response:
            agents = json.loads(response.read().decode())
            print(json.dumps(agents, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_send(args):
    """Send a task to an agent."""
    try:
        input_data = json.loads(args.input_json)
    except json.JSONDecodeError:
        print("Error: Invalid JSON for input", file=sys.stderr)
        sys.exit(1)
    
    # Use a temporary agent for sending
    agent = A2AAgent(
        agent_id="cli-sender",
        name="CLI Sender",
        capabilities=[],
        directory_url=args.directory
    )
    
    result = agent.send_task(args.target_agent, args.action, input_data)
    print(json.dumps(result, indent=2))


def cmd_serve(args):
    """Start an A2A agent server."""
    capabilities = args.capabilities.split(',')
    
    print(f"Starting A2A agent server...")
    print(f"  Agent ID: {args.agent_id}")
    print(f"  Name: {args.name}")
    print(f"  Capabilities: {capabilities}")
    print(f"  Port: {args.port}")
    
    server = A2AServer(
        agent_id=args.agent_id,
        name=args.name,
        capabilities=capabilities,
        port=args.port
    )
    
    # Simple handler that echoes
    @server.handle_task
    def echo_handler(action, input_data, sender):
        return {
            "received_action": action,
            "received_input": input_data,
            "from": sender
        }
    
    print("\nServer running. Press Ctrl+C to stop.")
    server.run()


def main():
    parser = argparse.ArgumentParser(
        description="A2A Protocol CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    a2a register my-agent "My Agent" "search,analyze" http://localhost:9001
    a2a discover search
    a2a list
    a2a send other-agent do_something '{"key": "value"}'
    a2a serve my-agent "My Agent" "search" 9001
        """
    )
    
    parser.add_argument(
        "--directory", "-d",
        default="http://localhost:8080",
        help="Directory URL (default: http://localhost:8080)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # register
    p_register = subparsers.add_parser("register", help="Register an agent")
    p_register.add_argument("agent_id", help="Agent ID")
    p_register.add_argument("name", help="Agent name")
    p_register.add_argument("capabilities", help="Comma-separated capabilities")
    p_register.add_argument("endpoint", help="Agent endpoint URL")
    p_register.set_defaults(func=cmd_register)
    
    # discover
    p_discover = subparsers.add_parser("discover", help="Discover agents")
    p_discover.add_argument("capabilities", help="Comma-separated capabilities to search")
    p_discover.set_defaults(func=cmd_discover)
    
    # list
    p_list = subparsers.add_parser("list", help="List all agents")
    p_list.set_defaults(func=cmd_list)
    
    # send
    p_send = subparsers.add_parser("send", help="Send a task")
    p_send.add_argument("target_agent", help="Target agent ID")
    p_send.add_argument("action", help="Action to perform")
    p_send.add_argument("input_json", help="Input as JSON string")
    p_send.set_defaults(func=cmd_send)
    
    # serve
    p_serve = subparsers.add_parser("serve", help="Start an agent server")
    p_serve.add_argument("agent_id", help="Agent ID")
    p_serve.add_argument("name", help="Agent name")
    p_serve.add_argument("capabilities", help="Comma-separated capabilities")
    p_serve.add_argument("port", type=int, help="Port to listen on")
    p_serve.set_defaults(func=cmd_serve)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
