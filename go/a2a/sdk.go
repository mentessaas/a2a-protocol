// Package a2a provides an A2A (Agent-to-Agent) Protocol SDK for Go.
//
// # Usage
//
//	package main
//
//	import (
//	    "encoding/json"
//	    "fmt"
//	    "log"
//
//	    "github.com/mentessaas/a2a-protocol/go/a2a"
//	)
//
//	func main() {
//	    // Create and register an agent
//	    agent := a2a.NewAgent(
//	        "my-agent",
//	        "My Agent",
//	        []string{"search", "summarize"},
//	    )
//	    err := agent.Register("http://localhost:8081", "http://localhost:8080")
//	    if err != nil {
//	        log.Fatal(err)
//	    }
//
//	    // Discover another agent
//	    other, err := agent.Discover([]string{"code"}, "http://localhost:8080")
//	    if err != nil {
//	        log.Fatal(err)
//	    }
//
//	    // Send a task
//	    result, err := agent.SendTask(other.AgentID, "summarize", map[string]interface{}{
//	        "text": "Hello world",
//	    }, "http://localhost:8080")
//	    if err != nil {
//	        log.Fatal(err)
//	    }
//
//	    fmt.Printf("Result: %+v\n", result)
//	}
package a2a

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// JSONRPCRequest represents a JSON-RPC 2.0 request
type JSONRPCRequest struct {
	JSONRPC string      `json:"jsonrpc"`
	ID      string      `json:"id"`
	Method  string      `json:"method"`
	Params  interface{} `json:"params,omitempty"`
}

// JSONRPCResponse represents a JSON-RPC 2.0 response
type JSONRPCResponse struct {
	JSONRPC string          `json:"jsonrpc"`
	ID      string          `json:"id"`
	Result  json.RawMessage `json:"result,omitempty"`
	Error   *JSONRPCError   `json:"error,omitempty"`
}

// JSONRPCError represents a JSON-RPC 2.0 error
type JSONRPCError struct {
	Code    int             `json:"code"`
	Message string          `json:"message"`
	Data    json.RawMessage `json:"data,omitempty"`
}

// AgentInfo represents registered agent information
type AgentInfo struct {
	AgentID       string    `json:"agentId"`
	Name          string    `json:"name"`
	Capabilities  []string  `json:"capabilities"`
	Endpoint      string    `json:"endpoint"`
	RegisteredAt time.Time `json:"registeredAt,omitempty"`
}

// RegisterParams represents registration parameters
type RegisterParams struct {
	AgentID      string   `json:"agentId"`
	Name         string   `json:"name"`
	Capabilities []string `json:"capabilities"`
	Endpoint     string   `json:"endpoint"`
}

// RegisterResult represents registration result
type RegisterResult struct {
	Status   string `json:"status"`
	AgentID  string `json:"agentId"`
}

// DiscoverParams represents discovery parameters
type DiscoverParams struct {
	Capabilities []string `json:"capabilities"`
}

// DiscoverResult represents discovery result
type DiscoverResult struct {
	Agents []AgentInfo `json:"agents"`
}

// TaskParams represents task parameters
type TaskParams struct {
	TaskID  string                 `json:"taskId"`
	Action  string                 `json:"action"`
	Sender  string                 `json:"sender"`
	Input   map[string]interface{} `json:"input"`
}

// TaskResult represents task result
type TaskResult struct {
	TaskID  string                 `json:"taskId"`
	Status  string                 `json:"status"` // completed, failed, cancelled, timeout
	Output  map[string]interface{} `json:"output,omitempty"`
}

// A2AAgent represents an A2A-enabled agent
type A2AAgent struct {
	AgentID      string
	Name         string
	Capabilities []string
	Endpoint     string
}

// NewAgent creates a new A2A agent
func NewAgent(agentID, name string, capabilities []string) *A2AAgent {
	return &A2AAgent{
		AgentID:      agentID,
		Name:         name,
		Capabilities: capabilities,
	}
}

// Register registers the agent with a directory
func (a *A2AAgent) Register(endpoint, directoryURL string) error {
	a.Endpoint = endpoint

	params := RegisterParams{
		AgentID:      a.AgentID,
		Name:         a.Name,
		Capabilities: a.Capabilities,
		Endpoint:     endpoint,
	}

	result, err := a.doRequest(directoryURL+"/a2a/register", params)
	if err != nil {
		return fmt.Errorf("registration failed: %w", err)
	}

	fmt.Printf("✅ Registered: %s\n", a.AgentID)
	_ = result // Result parsed successfully
	return nil
}

// Discover finds agents with specified capabilities
func (a *A2AAgent) Discover(wantedCapabilities []string, directoryURL string) (*AgentInfo, error) {
	params := DiscoverParams{
		Capabilities: wantedCapabilities,
	}

	result, err := a.doRequest(directoryURL+"/a2a/discover", params)
	if err != nil {
		return nil, fmt.Errorf("discovery failed: %w", err)
	}

	var discoverResult DiscoverResult
	if err := json.Unmarshal(result, &discoverResult); err != nil {
		return nil, err
	}

	if len(discoverResult.Agents) == 0 {
		return nil, nil
	}

	return &discoverResult.Agents[0], nil
}

// SendTask sends a task to another agent
func (a *A2AAgent) SendTask(targetAgentID, action string, input map[string]interface{}, directoryURL string) (*TaskResult, error) {
	// Get target agent info from directory
	resp, err := http.Get(fmt.Sprintf("%s/a2a/agents/%s", directoryURL, targetAgentID))
	if err != nil {
		return nil, fmt.Errorf("failed to get agent: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("agent not found: %s", targetAgentID)
	}

	var agentInfo AgentInfo
	if err := json.NewDecoder(resp.Body).Decode(&agentInfo); err != nil {
		return nil, err
	}

	// Send task to target
	params := TaskParams{
		TaskID:  generateID(),
		Action:  action,
		Sender:  a.AgentID,
		Input:   input,
	}

	result, err := a.doRequest(agentInfo.Endpoint, params)
	if err != nil {
		return nil, fmt.Errorf("task failed: %w", err)
	}

	var taskResult TaskResult
	if err := json.Unmarshal(result, &taskResult); err != nil {
		return nil, err
	}

	return &taskResult, nil
}

func (a *A2AAgent) doRequest(url string, params interface{}) (json.RawMessage, error) {
	req := JSONRPCRequest{
		JSONRPC: "2.0",
		ID:      generateID(),
		Method:  "a2a/register",
		Params:  params,
	}

	body, err := json.Marshal(req)
	if err != nil {
		return nil, err
	}

	resp, err := http.Post(url, "application/json", bytes.NewReader(body))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("HTTP %d", resp.StatusCode)
	}

	var rpcResp JSONRPCResponse
	if err := json.NewDecoder(resp.Body).Decode(&rpcResp); err != nil {
		return nil, err
	}

	if rpcResp.Error != nil {
		return nil, fmt.Errorf("RPC error: %s", rpcResp.Error.Message)
	}

	return rpcResp.Result, nil
}

func generateID() string {
	return fmt.Sprintf("id-%d", time.Now().UnixNano())
}
