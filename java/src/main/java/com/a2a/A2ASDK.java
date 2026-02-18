package com.a2a;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.*;

/**
 * A2A Protocol Java SDK
 * 
 * Usage:
 * <pre>
 * A2AAgent agent = new A2AAgent("my-agent", "My Agent", Arrays.asList("search", "analyze"));
 * agent.register("http://localhost:9001", "http://localhost:8080");
 * 
 * // Discover another agent
 * AgentInfo other = agent.discover(Arrays.asList("code"), "http://localhost:8080");
 * 
 * // Send task
 * TaskResult result = agent.sendTask(other.getAgentId(), "doSomething", 
 *     Map.of("key", "value"), "http://localhost:8080");
 * </pre>
 */
public class A2ASDK {
    
    private static final ObjectMapper mapper = new ObjectMapper();
    private static final HttpClient httpClient = HttpClient.newBuilder()
        .connectTimeout(Duration.ofSeconds(10))
        .build();
    
    // ============ Models ============
    
    public static class AgentInfo {
        private String agentId;
        private String name;
        private List<String> capabilities;
        private String endpoint;
        private String registeredAt;
        
        public AgentInfo() {}
        
        public String getAgentId() { return agentId; }
        public void setAgentId(String agentId) { this.agentId = agentId; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public List<String> getCapabilities() { return capabilities; }
        public void setCapabilities(List<String> capabilities) { this.capabilities = capabilities; }
        public String getEndpoint() { return endpoint; }
        public void setEndpoint(String endpoint) { this.endpoint = endpoint; }
        public String getRegisteredAt() { return registeredAt; }
        public void setRegisteredAt(String registeredAt) { this.registeredAt = registeredAt; }
    }
    
    public static class TaskResult {
        private String taskId;
        private String status;
        private Map<String, Object> output;
        
        public TaskResult() {}
        
        public String getTaskId() { return taskId; }
        public void setTaskId(String taskId) { this.taskId = taskId; }
        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }
        public Map<String, Object> getOutput() { return output; }
        public void setOutput(Map<String, Object> output) { this.output = output; }
    }
    
    // ============ A2AAgent ============
    
    public static class A2AAgent {
        private String agentId;
        private String name;
        private List<String> capabilities;
        private String endpoint;
        
        public A2AAgent(String agentId, String name, List<String> capabilities) {
            this.agentId = agentId;
            this.name = name;
            this.capabilities = capabilities;
        }
        
        public String getAgentId() { return agentId; }
        public String getName() { return name; }
        public List<String> getCapabilities() { return capabilities; }
        public String getEndpoint() { return endpoint; }
        
        public void register(String endpoint, String directoryUrl) throws Exception {
            this.endpoint = endpoint;
            
            Map<String, Object> params = new HashMap<>();
            params.put("agentId", agentId);
            params.put("name", name);
            params.put("capabilities", capabilities);
            params.put("endpoint", endpoint);
            
            request(directoryUrl + "/a2a/register", "a2a/register", params);
            System.out.println("✅ Registered: " + agentId);
        }
        
        public AgentInfo discover(List<String> wantedCapabilities, String directoryUrl) throws Exception {
            Map<String, Object> params = new HashMap<>();
            params.put("capabilities", wantedCapabilities);
            
            Map<String, Object> result = request(directoryUrl + "/a2a/discover", "a2a/discover", params);
            
            List<Map<String, Object>> agents = (List<Map<String, Object>>) result.get("agents");
            if (agents == null || agents.isEmpty()) {
                return null;
            }
            
            return mapper.convertValue(agents.get(0), AgentInfo.class);
        }
        
        public TaskResult sendTask(String targetAgentId, String action, 
                                   Map<String, Object> input, String directoryUrl) throws Exception {
            // Get target agent info
            HttpResponse<String> agentResp = httpClient.send(
                HttpRequest.newBuilder(URI.create(directoryUrl + "/a2a/agents/" + targetAgentId)).GET().build(),
                HttpResponse.BodyHandlers.ofString()
            );
            
            if (agentResp.statusCode() != 200) {
                throw new RuntimeException("Agent not found: " + targetAgentId);
            }
            
            AgentInfo target = mapper.readValue(agentResp.body(), AgentInfo.class);
            
            // Send task
            Map<String, Object> params = new HashMap<>();
            params.put("taskId", UUID.randomUUID().toString());
            params.put("action", action);
            params.put("sender", agentId);
            params.put("input", input);
            
            Map<String, Object> result = request(target.getEndpoint(), "a2a/task", params);
            
            return mapper.convertValue(result, TaskResult.class);
        }
        
        @SuppressWarnings("unchecked")
        private Map<String, Object> request(String url, String method, Map<String, Object> params) throws Exception {
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("jsonrpc", "2.0");
            requestBody.put("id", UUID.randomUUID().toString());
            requestBody.put("method", method);
            requestBody.put("params", params);
            
            String json = mapper.writeValueAsString(requestBody);
            
            HttpResponse<String> response = httpClient.send(
                HttpRequest.newBuilder(URI.create(url))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(json))
                    .build(),
                HttpResponse.BodyHandlers.ofString()
            );
            
            if (response.statusCode() != 200) {
                throw new RuntimeException("HTTP " + response.statusCode());
            }
            
            Map<String, Object> resp = mapper.readValue(response.body(), Map.class);
            
            if (resp.containsKey("error")) {
                Map<String, Object> error = (Map<String, Object>) resp.get("error");
                throw new RuntimeException("RPC Error: " + error.get("message"));
            }
            
            @SuppressWarnings("unchecked")
            Map<String, Object> result = (Map<String, Object>) resp.get("result");
            return result;
        }
    }
    
    // ============ A2AServer ============
    
    public interface TaskHandler {
        Map<String, Object> handle(String action, Map<String, Object> input, String sender);
    }
    
    public static class A2AServer {
        private String agentId;
        private String name;
        private List<String> capabilities;
        private int port;
        private String endpoint;
        private TaskHandler taskHandler;
        
        public A2AServer(String agentId, String name, List<String> capabilities, int port) {
            this.agentId = agentId;
            this.name = name;
            this.capabilities = capabilities;
            this.port = port;
            this.endpoint = "http://localhost:" + port;
        }
        
        public void handleTask(TaskHandler handler) {
            this.taskHandler = handler;
        }
        
        public void run() {
            System.out.println("🤖 Agent '" + agentId + "' running on port " + port);
            // In production, use a web server (Jetty, Spring Boot, etc.)
            // This is a placeholder
            try {
                Thread.sleep(Long.MAX_VALUE);
            } catch (InterruptedException e) {
                // Shutdown
            }
        }
    }
}
