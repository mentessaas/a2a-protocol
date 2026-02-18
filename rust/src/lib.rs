//! A2A Protocol SDK for Rust
//!
//! # Usage
//!
//! ```rust
//! use a2a::{A2AAgent, A2AServer};
//!
//! // Create an agent
//! let agent = A2AAgent::new(
//!     "my-agent",
//!     "My Agent",
//!     vec!["search".to_string(), "summarize".to_string()],
//! );
//!
//! // Register with directory
//! agent.register("http://localhost:9001", "http://localhost:8080").await?;
//!
//! // Discover agents
//! let other = agent.discover(vec!["calculator".to_string()], "http://localhost:8080").await?;
//!
//! // Send a task
//! let result = agent.send_task(
//!     &other.agent_id,
//!     "add",
//!     serde_json::json!({"a": 10, "b": 20}),
//!     "http://localhost:8080"
//! ).await?;
//! ```

use reqwest::Client;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::HashMap;

// ============ Types ============

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct AgentInfo {
    pub agent_id: String,
    pub name: String,
    pub capabilities: Vec<String>,
    pub endpoint: String,
    #[serde(rename = "registeredAt")]
    pub registered_at: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct JSONRPCRequest {
    jsonrpc: String,
    id: String,
    method: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    params: Option<Value>,
}

#[derive(Debug, Serialize, Deserialize)]
struct JSONRPCResponse {
    jsonrpc: String,
    id: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    result: Option<Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    error: Option<JSONRPCError>,
}

#[derive(Debug, Serialize, Deserialize)]
struct JSONRPCError {
    code: i32,
    message: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct RegisterParams {
    #[serde(rename = "agentId")]
    agent_id: String,
    name: String,
    capabilities: Vec<String>,
    endpoint: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct DiscoverParams {
    capabilities: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct TaskParams {
    #[serde(rename = "taskId")]
    task_id: String,
    action: String,
    sender: String,
    input: Value,
}

#[derive(Debug, Serialize, Deserialize)]
struct TaskResult {
    #[serde(rename = "taskId")]
    task_id: String,
    status: String,
    output: Option<Value>,
}

// ============ A2AAgent ============

pub struct A2AAgent {
    pub agent_id: String,
    pub name: String,
    pub capabilities: Vec<String>,
    pub endpoint: Option<String>,
    client: Client,
}

impl A2AAgent {
    pub fn new(agent_id: &str, name: &str, capabilities: Vec<String>) -> Self {
        Self {
            agent_id: agent_id.to_string(),
            name: name.to_string(),
            capabilities,
            endpoint: None,
            client: Client::new(),
        }
    }

    pub async fn register(&mut self, endpoint: &str, directory_url: &str) -> Result<(), String> {
        self.endpoint = Some(endpoint.to_string());

        let params = RegisterParams {
            agent_id: self.agent_id.clone(),
            name: self.name.clone(),
            capabilities: self.capabilities.clone(),
            endpoint: endpoint.to_string(),
        };

        let result = self
            .request(&format!("{}/a2a/register", directory_url.trim_end_matches('/')), "a2a/register", Some(params))
            .await?;

        println!("✅ Registered: {}", self.agent_id);
        Ok(result)
    }

    pub async fn discover(
        &self,
        wanted_capabilities: Vec<String>,
        directory_url: &str,
    ) -> Result<Option<AgentInfo>, String> {
        let params = DiscoverParams {
            capabilities: wanted_capabilities,
        };

        let result = self
            .request(&format!("{}/a2a/discover", directory_url.trim_end_matches('/')), "a2a/discover", Some(params))
            .await?;

        let agents: Vec<AgentInfo> = serde_json::from_value(
            result.get("agents").cloned().unwrap_or(json!([]))
        ).map_err(|e| e.to_string())?;

        Ok(agents.into_iter().next())
    }

    pub async fn send_task(
        &self,
        target_agent_id: &str,
        action: &str,
        input: Value,
        directory_url: &str,
    ) -> Result<TaskResult, String> {
        // Get target agent info
        let agent_url = format!("{}/a2a/agents/{}", directory_url.trim_end_matches('/'), target_agent_id);
        let response = self.client.get(&agent_url).send().await.map_err(|e| e.to_string())?;
        
        if !response.status().is_success() {
            return Err(format!("Agent not found: {}", target_agent_id));
        }

        let agent_info: AgentInfo = response.json().await.map_err(|e| e.to_string())?;

        // Send task
        let params = TaskParams {
            task_id: uuid::Uuid::new_v4().to_string(),
            action: action.to_string(),
            sender: self.agent_id.clone(),
            input,
        };

        let result = self
            .request(&agent_info.endpoint, "a2a/task", Some(params))
            .await?;

        let task_result: TaskResult = serde_json::from_value(result).map_err(|e| e.to_string())?;
        Ok(task_result)
    }

    async fn request(&self, url: &str, method: &str, params: Option<Value>) -> Result<Value, String> {
        let request = JSONRPCRequest {
            jsonrpc: "2.0".to_string(),
            id: uuid::Uuid::new_v4().to_string(),
            method: method.to_string(),
            params,
        };

        let response = self.client
            .post(url)
            .json(&request)
            .send()
            .await
            .map_err(|e| e.to_string())?;

        if !response.status().is_success() {
            return Err(format!("HTTP error: {}", response.status()));
        }

        let rpc_response: JSONRPCResponse = response.json().await.map_err(|e| e.to_string())?;

        if let Some(error) = rpc_response.error {
            return Err(format!("RPC error {}: {}", error.code, error.message));
        }

        rpc_response.result.ok_or_else(|| "No result".to_string())
    }
}

// ============ A2AServer ============

pub type TaskHandler = Box<dyn Fn(String, Value, String) -> Value + Send + Sync>;

pub struct A2AServer {
    agent_id: String,
    name: String,
    capabilities: Vec<String>,
    port: u16,
    task_handler: Option<TaskHandler>,
}

impl A2AServer {
    pub fn new(agent_id: &str, name: &str, capabilities: Vec<String>, port: u16) -> Self {
        Self {
            agent_id: agent_id.to_string(),
            name: name.to_string(),
            capabilities,
            port,
            task_handler: None,
        }
    }

    pub fn handle_task<F>(&mut self, handler: F)
    where
        F: Fn(String, Value, String) -> Value + Send + Sync + 'static,
    {
        self.task_handler = Some(Box::new(handler));
    }

    pub async fn run(&self) -> Result<(), String> {
        let addr = format!("0.0.0.0:{}", self.port);
        println!("🤖 Agent '{}' running on port {}", self.agent_id, self.port);
        
        // Simple HTTP server using axum would be better for production
        // This is a placeholder - use with actix-web or axum for real implementation
        Ok(())
    }
}

// ============ Convenience ============

pub async fn run_server<F>(agent_id: &str, name: &str, capabilities: Vec<String>, port: u16, handler: F) -> Result<(), String>
where
    F: Fn(String, Value, String) -> Value + Send + Sync + 'static,
{
    let mut server = A2AServer::new(agent_id, name, capabilities, port);
    server.handle_task(handler);
    server.run().await
}
