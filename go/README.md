# A2A Protocol Go SDK

Go SDK for the A2A (Agent-to-Agent) Protocol.

## Installation

```bash
go get github.com/mentessaas/a2a-protocol/go/a2a
```

## Quick Start

```go
package main

import (
	"fmt"
	"log"

	"github.com/mentessaas/a2a-protocol/go/a2a"
)

func main() {
	// Create an agent
	agent := a2a.NewAgent(
		"my-agent",
		"My Agent",
		[]string{"search", "summarize"},
	)

	// Register with directory
	err := agent.Register("http://localhost:9001", "http://localhost:8080")
	if err != nil {
		log.Fatal(err)
	}

	// Discover another agent
	other, err := agent.Discover([]string{"calculator"}, "http://localhost:8080")
	if err != nil {
		log.Fatal(err)
	}

	// Send a task
	result, err := agent.SendTask(other.AgentID, "add", map[string]interface{}{
		"a": 10,
		"b": 20,
	}, "http://localhost:8080")
	if err != nil {
		log.Fatal(err)
	}

	fmt.Printf("Result: %+v\n", result)
}
```

## Running an Agent Server

```go
package main

import (
	"fmt"
	"log"

	"github.com/mentessaas/a2a-protocol/go/a2a"
)

func myHandler(action string, input map[string]interface{}, sender string) map[string]interface{} {
	fmt.Printf("Received task: %s from %s\n", action, sender)
	
	switch action {
	case "add":
		a := input["a"].(float64)
		b := input["b"].(float64)
		return map[string]interface{}{"result": a + b}
	default:
		return map[string]interface{}{"error": "unknown action"}
	}
}

func main() {
	err := a2a.RunServer(
		"calculator-agent",
		"Calculator Agent", 
		[]string{"math", "calculate"},
		9001,
		myHandler,
	)
	if err != nil {
		log.Fatal(err)
	}
}
```

## API

### A2AAgent

- `NewAgent(agentID, name string, capabilities []string)` - Create a new agent
- `Register(endpoint, directoryURL string) error` - Register with directory
- `Discover(wantedCapabilities []string, directoryURL string) (*AgentInfo, error)` - Find agents
- `SendTask(targetAgentID, action string, input map[string]interface{}, directoryURL string) (*TaskResult, error)` - Send task

### A2AServer

- `NewServer(agentID, name string, capabilities []string, port int)` - Create server
- `HandleTask(handler TaskHandler)` - Register task handler
- `Serve() error` - Start server
- `RunServer(...)` - Convenience function

## See Also

- [Python SDK](../a2a_sdk.py)
- [TypeScript SDK](../typescript/)
- [Specification](../SPEC.md)
