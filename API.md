# A2A Protocol API Reference

## Overview

A2A Protocol uses JSON-RPC 2.0 over HTTP. All requests are POST with `application/json` content type.

## Endpoints

### Directory Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/a2a/register` | Register an agent |
| POST | `/a2a/discover` | Find agents by capability |
| GET | `/a2a/agents` | List all agents |
| GET | `/a2a/agents/:id` | Get specific agent |

### Agent Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Process JSON-RPC request |

---

## Methods

### `a2a/register`

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
    "capabilities": ["research", "search"],
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

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| agentId | string | Yes | Unique identifier |
| name | string | Yes | Human-readable name |
| capabilities | array | Yes | List of capabilities |
| endpoint | string | Yes | Agent's HTTP endpoint |

---

### `a2a/discover`

Find agents by capability.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "disc-1",
  "method": "a2a/discover",
  "params": {
    "capabilities": ["research"]
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

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| capabilities | array | Yes | Capabilities to search for |

**Matching:** Returns agents where ANY capability matches.

---

### `a2a/task`

Send a task to another agent.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "task-1",
  "method": "a2a/task",
  "params": {
    "taskId": "task-123",
    "action": "search",
    "sender": "coordinator-agent",
    "input": {
      "query": "AI news",
      "maxResults": 5
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "task-1",
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
  "id": "task-1",
  "error": {
    "code": -32001,
    "message": "Task failed",
    "data": {"reason": "timeout"}
  }
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| taskId | string | Yes | Unique task identifier |
| action | string | Yes | Action to perform |
| sender | string | Yes | Sender's agent ID |
| input | object | Yes | Task input data |

**Status Values:**
- `completed` - Task finished successfully
- `failed` - Task failed
- `cancelled` - Task was cancelled
- `timeout` - Task exceeded time limit

---

## Error Codes

| Code | Meaning | Description |
|------|---------|-------------|
| -32700 | Parse Error | Invalid JSON |
| -32600 | Invalid Request | Missing required fields |
| -32601 | Method Not Found | Unknown method |
| -32602 | Invalid Params | Bad parameters |
| -32001 | Task Failed | Agent processing error |
| -32002 | Task Timeout | Task took too long |

---

## HTTP Headers

**Request:**
```
Content-Type: application/json
```

**Response:**
```
Content-Type: application/json
```

---

## Examples

### cURL

```bash
# Register agent
curl -X POST http://localhost:8080/a2a/register \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "a2a/register",
    "params": {
      "agentId": "my-agent",
      "name": "My Agent",
      "capabilities": ["search"],
      "endpoint": "http://localhost:9001"
    }
  }'

# Discover agents
curl -X POST http://localhost:8080/a2a/discover \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "2",
    "method": "a2a/discover",
    "params": {
      "capabilities": ["search"]
    }
  }'

# Send task
curl -X POST http://localhost:9001/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "3",
    "method": "a2a/task",
    "params": {
      "taskId": "task-1",
      "action": "search",
      "sender": "other-agent",
      "input": {"query": "test"}
    }
  }'
```

### Python

```python
import requests

# Register
requests.post("http://localhost:8080/a2a/register", json={
    "jsonrpc": "2.0",
    "id": "1",
    "method": "a2a/register",
    "params": {
        "agentId": "my-agent",
        "name": "My Agent",
        "capabilities": ["search"],
        "endpoint": "http://localhost:9001"
    }
})

# Discover
requests.post("http://localhost:8080/a2a/discover", json={
    "jsonrpc": "2.0",
    "id": "2",
    "method": "a2a/discover",
    "params": {"capabilities": ["search"]}
})

# Send task
requests.post("http://localhost:9001/", json={
    "jsonrpc": "2.0",
    "id": "3",
    "method": "a2a/task",
    "params": {
        "taskId": "task-1",
        "action": "search",
        "sender": "other-agent",
        "input": {"query": "test"}
    }
})
```

---

## See Also

- [Specification](./SPEC.md)
- [Tutorial](./TUTORIAL.md)
- [SDKs](./#sdks)
