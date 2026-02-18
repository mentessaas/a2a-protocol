# A2A Protocol Specification

**Version:** 0.1.0 (MVP)  
**Status:** Implemented  
**Date:** 2026-02-17

---

## Overview

A2A (Agent-to-Agent) is a JSON-RPC 2.0 protocol for inter-agent communication. It enables agents to:

1. **Discover** other agents by capability
2. **Register** themselves for discovery
3. **Exchange tasks** with structured input/output
4. **Coordinate** without hardcoded connections

---

## Design Principles

1. **Minimal MVP** - Only essential features
2. **JSON-RPC 2.0** - Proven, familiar standard
3. **Capability-based** - No agent IDs hardcoded
4. **HTTP transport** - Simple, universal
5. **Extensible** - Easy to add features later

---

## Message Format

All messages follow JSON-RPC 2.0:

```json
{
  "jsonrpc": "2.0",
  "id": "unique-id",
  "method": "a2a/<method>",
  "params": { ... }
}
```

---

## Methods

### 1. `a2a/register`

Register an agent with the directory.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "reg-1",
  "method": "a2a/register",
  "params": {
    "agentId": "research-agent",
    "name": "Research Agent",
    "capabilities": ["research", "search", "analysis"],
    "endpoint": "http://localhost:9001"
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "reg-1",
  "result": {
    "status": "registered",
    "agentId": "research-agent"
  }
}
```

**Fields:**
| Field | Required | Description |
|-------|----------|-------------|
| `agentId` | Yes | Unique identifier |
| `name` | Yes | Human-readable name |
| `capabilities` | Yes | List of capabilities |
| `endpoint` | Yes | HTTP endpoint for this agent |

---

### 2. `a2a/discover`

Find agents by capability.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "disc-1",
  "method": "a2a/discover",
  "params": {
    "capabilities": ["search"]
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "disc-1",
  "result": {
    "agents": [
      {
        "agentId": "research-agent",
        "name": "Research Agent",
        "capabilities": ["research", "search"],
        "endpoint": "http://localhost:9001",
        "registeredAt": "2026-02-17T18:00:00Z"
      }
    ]
  }
}
```

**Matching:** Returns agents where any capability matches.

---

### 3. `a2a/task`

Send a task to another agent.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "task-123",
  "method": "a2a/task",
  "params": {
    "taskId": "task-123",
    "action": "search",
    "sender": "my-agent",
    "input": {
      "query": "latest AI news",
      "maxResults": 5
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "task-123",
  "result": {
    "taskId": "task-123",
    "status": "completed",
    "output": {
      "results": [...]
    }
  }
}
```

**Error Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "task-123",
  "error": {
    "code": -32001,
    "message": "Task failed",
    "data": {"reason": "timeout"}
  }
}
```

**Status Values:**
- `completed` - Task finished successfully
- `failed` - Task failed with error
- `cancelled` - Task was cancelled
- `timeout` - Task exceeded time limit

---

## Transport

### HTTP

- **Content-Type:** `application/json`
- **Method:** POST
- **URL:** Agent endpoint

### Request
```http
POST /a2a/task HTTP/1.1
Host: agent.example.com
Content-Type: application/json

{"jsonrpc": "2.0", "id": "1", "method": "a2a/task", "params": {...}}
```

### Response
```http
HTTP/1.1 200 OK
Content-Type: application/json

{"jsonrpc": "2.0", "id": "1", "result": {...}}
```

---

## Directory API (Standalone)

The directory service exposes REST endpoints for convenience:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/a2a/agents` | List all agents |
| GET | `/a2a/agents/:id` | Get specific agent |

---

## Security (MVP)

- **No authentication** in MVP
- **No encryption** (use HTTPS in production)
- **No identity verification** (trust the directory)

---

## Error Codes

| Code | Meaning |
|------|---------|
| -32600 | Invalid Request |
| -32601 | Method not found |
| -32602 | Invalid params |
| -32700 | Parse error |
| -32001 | Task failed |
| -32002 | Task timeout |

---

## Extensibility

Future additions may include:

- `a2a/cancel` - Cancel a running task
- `a2a/stream` - Streaming responses
- `a2a/events` - Event subscriptions
- Authentication extensions
- Multi-hop workflows

---

## Reference Implementation

See `a2a_directory.py` and `a2a_sdk.py` in this repository.

---

## Similar Protocols

- **MCP (Model Context Protocol)** - Agent-to-tool communication
- **Agent Protocol** - Anthropic's agent specification
- **AutoGen** - Microsoft's multi-agent framework

A2A complements these by focusing on **peer-to-peer agent communication** rather than agent-to-tool or agent-to-human.

---

*Specification v0.1.0 - Implemented and running.*
