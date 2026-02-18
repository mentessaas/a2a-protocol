package a2a

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

// TaskHandler is a function that handles incoming tasks
type TaskHandler func(action string, input map[string]interface{}, sender string) map[string]interface{}

// A2AServer is an HTTP server for A2A agents
type A2AServer struct {
	AgentID      string
	Name         string
	Capabilities []string
	Port         int
	Endpoint     string
	taskHandler  TaskHandler
}

// NewServer creates a new A2A server
func NewServer(agentID, name string, capabilities []string, port int) *A2AServer {
	return &A2AServer{
		AgentID:      agentID,
		Name:         name,
		Capabilities: capabilities,
		Port:         port,
		Endpoint:     fmt.Sprintf("http://localhost:%d", port),
	}
}

// HandleTask registers a task handler function
func (s *A2AServer) HandleTask(handler TaskHandler) {
	s.taskHandler = handler
}

// Serve starts the A2A server
func (s *A2AServer) Serve() error {
	http.HandleFunc("/", s.handleRequest)
	fmt.Printf("🤖 Agent '%s' running on port %d\n", s.AgentID, s.Port)
	return http.ListenAndServe(fmt.Sprintf(":%d", s.Port), nil)
}

func (s *A2AServer) handleRequest(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	body, err := io.ReadAll(r.Body)
	if err != nil {
		s.sendError(w, -32700, "Parse error")
		return
	}

	var req JSONRPCRequest
	if err := json.Unmarshal(body, &req); err != nil {
		s.sendError(w, -32700, "Parse error")
		return
	}

	var resp JSONRPCResponse
	resp.JSONRPC = "2.0"
	resp.ID = req.ID

	switch req.Method {
	case "a2a/task":
		resp.Result = s.handleTask(req.Params)
	case "a2a/discover":
		// For agent-to-agent discovery, return own info
		agent := AgentInfo{
			AgentID:      s.AgentID,
			Name:         s.Name,
			Capabilities: s.Capabilities,
			Endpoint:     s.Endpoint,
		}
		result := map[string]interface{}{
			"agents": []AgentInfo{agent},
		}
		resp.Result, _ = json.Marshal(result)
	default:
		resp.Error = &JSONRPCError{
			Code:    -32601,
			Message: "Method not found",
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func (s *A2AServer) handleTask(params interface{}) json.RawMessage {
	// Convert params to JSON first
	paramsJSON, err := json.Marshal(params)
	if err != nil {
		return s.errorResult(-32602, "Invalid params")
	}

	var taskParams TaskParams
	if err := json.Unmarshal(paramsJSON, &taskParams); err != nil {
		return s.errorResult(-32602, "Invalid params")
	}

	if s.taskHandler == nil {
		return s.errorResult(-32001, "No handler registered")
	}

	output := s.taskHandler(taskParams.Action, taskParams.Input, taskParams.Sender)

	result := TaskResult{
		TaskID: taskParams.TaskID,
		Status: "completed",
		Output: output,
	}

	response, err := json.Marshal(result)
	if err != nil {
		return s.errorResult(-32001, "Task failed")
	}

	return response
}

func (s *A2AServer) errorResult(code int, message string) json.RawMessage {
	err := &JSONRPCError{Code: code, Message: message}
	resp := map[string]interface{}{
		"error": err,
	}
	result, _ := json.Marshal(resp)
	return result
}

func (s *A2AServer) sendError(w http.ResponseWriter, code int, message string) {
	w.Header().Set("Content-Type", "application/json")
	err := &JSONRPCError{Code: code, Message: message}
	json.NewEncoder(w).Encode(err)
}

// RunServer is a convenience function to run a simple agent server
func RunServer(agentID, name string, capabilities []string, port int, handler TaskHandler) error {
	server := NewServer(agentID, name, capabilities, port)
	server.HandleTask(handler)
	return server.Serve()
}
