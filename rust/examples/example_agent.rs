//! A2A Protocol Rust Example Agent
//!
//! Run with: cargo run --example example_agent

use a2a::{A2AAgent, run_server};
use serde_json::json;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create and register an agent
    let mut agent = A2AAgent::new(
        "calculator-agent",
        "Calculator Agent",
        vec!["math".to_string(), "calculate".to_string(), "add".to_string()],
    );

    // Register with directory (optional)
    if let Err(e) = agent.register("http://localhost:9001", "http://localhost:8080").await {
        println!("Registration note: {}", e);
    }

    // Start server with task handler
    run_server(
        "calculator-agent",
        "Calculator Agent",
        vec!["math".to_string(), "calculate".to_string(), "add".to_string()],
        9001,
        |action, input, sender| {
            println!("📥 Received task: action={} from={}", action, sender);
            
            match action.as_str() {
                "add" => {
                    let a = input["a"].as_f64().unwrap_or(0.0);
                    let b = input["b"].as_f64().unwrap_or(0.0);
                    json!({"result": a + b})
                }
                "echo" => {
                    json!({"echo": input["message"]})
                }
                _ => {
                    json!({"error": "Unknown action"})
                }
            }
        },
    ).await?;

    Ok(())
}

// Example of client usage
/*
async fn client_example() -> Result<(), Box<dyn std::error::Error>> {
    let agent = A2AAgent::new(
        "my-agent",
        "My Agent",
        vec!["search".to_string()],
    );

    // Discover agents
    let other = agent.discover(
        vec!["calculator".to_string()],
        "http://localhost:8080"
    ).await?;

    if let Some(other) = other {
        // Send a task
        let result = agent.send_task(
            &other.agent_id,
            "add",
            json!({"a": 10, "b": 20}),
            "http://localhost:8080"
        ).await?;

        println!("Result: {:?}", result);
    }

    Ok(())
}
*/
