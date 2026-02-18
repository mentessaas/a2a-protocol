# A2A Protocol 🔗

> The open standard for agent-to-agent communication

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://typescriptlang.org)

## What is A2A?

**A2A (Agent-to-Agent)** is an open protocol for AI agents to discover and communicate with each other. Think of it as **yellow pages + message bus** for AI agents.

Think about how MCP (Model Context Protocol) standardized tool-calling for AI agents. A2A does the same thing for **agent-to-agent** communication.

### Why A2A?

Currently, AI agents can call tools (via MCP), but they can't easily call **other agents**. A2A solves that:

- **Discovery** — Agents find each other by capability, not hardcoded addresses
- **Interoperability** — Agents built with different frameworks can talk
- **Composition** — Build complex multi-agent systems from simpler agents

## Quick Start

### 1. Run the Directory

```bash
# Python (no dependencies)
python3 a2a_directory.py
```

### 2. Run a Demo Agent

```bash
# Terminal 2: Start echo agent
python3 examples/echo_agent.py
```

### 3. Send a Task

```python
from a2a_sdk import A2AAgent

agent = A2AAgent(
    agent_id="my-agent",
    name="My Agent", 
    capabilities=["echo"]
)
agent.register("http://localhost:9001")

# Discover and call another agent
other = agent.discover(["echo"])
result = agent.send_task(other["agentId"], "echo", {"message": "Hello!"})
print(result)
```

### 4. Or use TypeScript

```typescript
import { A2AAgentClient } from './a2a';

const agent = new A2AAgentClient('my-agent', 'My Agent', ['echo']);
await agent.register('http://localhost:3000');

const result = await agent.sendTask('echo-agent', 'echo', { message: 'Hello!' });
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Agent A   │────▶│  Directory   │◀────│   Agent B   │
│ (requester) │     │  (registry) │     │ (responder) │
└─────────────┘     └──────────────┘     └─────────────┘
       │                   │                    │
       │  1. Register      │                    │
       │──────────────────>│                    │
       │                   │                    │
       │  2. Discover      │                    │
       │<──────────────────│                    │
       │                   │                    │
       │  3. Task Request  │                    │
       │────────────────────────>│              │
       │                   │                    │
       │  4. Task Response│                    │
       │<────────────────────────│              │
```

## Features

- **Agent Registry** — Agents register with capabilities
- **Capability Discovery** — Find agents by what they do
- **Task Exchange** — Structured request/response
- **JSON-RPC 2.0** — Industry-standard format
- **Zero Dependencies** — Pure stdlib implementations
- **Multi-language** — Python and TypeScript SDKs

## SDKs

| Language | Status | Install |
|----------|--------|---------|
| Python | ✅ Ready | `pip install a2a-sdk` (coming soon) |
| TypeScript | ✅ Ready | `@org/a2a-sdk` (coming soon) |

## Protocol

A2A uses JSON-RPC 2.0 over HTTP:

```json
// Discover agents
POST /a2a/discover
{ "capabilities": ["search"] }

// Send task
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "a2a/task", 
  "params": {
    "taskId": "123",
    "action": "search",
    "input": { "query": "..." }
  }
}
```

See [SPEC.md](SPEC.md) for full protocol specification.

## Use Cases

- **Multi-agent workflows** — Compose agents that delegate to each other
- **Agent marketplaces** — Discover and hire specialist agents
- **Enterprise orchestration** — Coordinate agents across systems
- **Research + Code + Write** — Specialized agents collaborating

## Why Open Source?

We believe **agent interoperability** will unlock the next wave of AI innovation. Just as HTTP enabled the web, and MCP enabled tool calling, A2A enables agent calling.

The standard should be open. Let's build it together.

## Contributing

1. Fork the repo
2. Make a change
3. Submit a PR

Ideas, feedback, and contributions welcome!

## Roadmap

- [ ] Authentication / mTLS
- [ ] Streaming responses
- [ ] Multi-hop workflows
- [ ] Federation / peer discovery
- [ ] More SDKs (Go, Rust)

## Contact

- GitHub Issues for bugs/features
- Discord (coming soon)

---

**Built by AI agents, for AI agents.** 🦾
