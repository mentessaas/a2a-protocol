// A2A Go SDK - Example Agent
//
// This example demonstrates how to create an A2A-enabled agent in Go.
//
// Run:
//
//	go run example_agent.go
package main

import (
	"fmt"
	"log"

	"github.com/mentessaas/a2a-protocol/go/a2a"
)

// SimpleTaskHandler handles tasks for the agent
func SimpleTaskHandler(action string, input map[string]interface{}, sender string) map[string]interface{} {
	fmt.Printf("📥 Received task: action=%s from=%s\n", action, sender)

	switch action {
	case "echo":
		return map[string]interface{}{
			"echo": input["message"],
		}
	case "add":
		a := input["a"].(float64)
		b := input["b"].(float64)
		return map[string]interface{}{
			"result": a + b,
		}
	default:
		return map[string]interface{}{
			"error": "Unknown action",
		}
	}
}

func main() {
	// Create an agent
	agent := a2a.NewAgent(
		"calculator-agent",
		"Calculator Agent",
		[]string{"math", "calculate", "add", "subtract"},
	)

	// Register with directory (optional)
	err := agent.Register("http://localhost:9001", "http://localhost:8080")
	if err != nil {
		log.Printf("Registration: %v", err)
	}

	// Start the server
	fmt.Println("🚀 Starting A2A agent server...")
	err = a2a.RunServer(
		"calculator-agent",
		"Calculator Agent",
		[]string{"math", "calculate", "add", "subtract"},
		9001,
		SimpleTaskHandler,
	)
	if err != nil {
		log.Fatal(err)
	}
}

// Example of using the agent client (uncomment to use)
/*
func clientExample() {
	agent := a2a.NewAgent("my-agent", "My Agent", []string{"search"})

	// Discover agents
	other, _ := agent.Discover([]string{"calculator"}, "http://localhost:8080")
	if other != nil {
		// Send a task
		result, err := agent.SendTask(other.AgentID, "add", map[string]interface{}{
			"a": 10,
			"b": 20,
		}, "http://localhost:8080")
		if err != nil {
			log.Fatal(err)
		}

		output, _ := json.Marshal(result.Output)
		fmt.Printf("Result: %s\n", output)
	}
}
*/
