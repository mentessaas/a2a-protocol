# A2A Protocol Rust SDK

Rust SDK for the A2A (Agent-to-Agent) Protocol.

## Installation

Add to your `Cargo.toml`:

```toml
[dependencies]
a2a-protocol = { git = "https://github.com/mentessaas/a2a-protocol", branch = "main" }
```

Or path dependency:
```toml
a2a-protocol = { path = "./rust" }
```

## Quick Start

```rust
use a2a::{A2AAgent, run_server};
use serde_json::json;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create an agent
    let mut agent = A2AAgent::new(
        "my-agent",
        "My Agent",
        vec!["search".to_string(), "summarize".to_string()],
    );

    // Register with directory
    agent.register("http://localhost:9001", "http://localhost:8080").await?;

    // Discover another agent
    let other = agent.discover(
        vec!["calculator".to_string()],
        "http://localhost:8080"
    ).await?;

    // Send a task
    let result = agent.send_task(
        &other.agent_id,
        "add",
        json!({"a": 10, "b": 20}),
        "http://localhost:8080"
    ).await?;

    println!("Result: {:?}", result);
    
    // Or run a server
    run_server(
        "calculator-agent",
        "Calculator Agent",
        vec!["math".to_string()],
        9001,
        |action, input, sender| {
            // Handle tasks
            json!({"result": "ok"})
        },
    ).await?;

    Ok(())
}
```

## API

### A2AAgent

- `new(agent_id, name, capabilities)` - Create a new agent
- `register(endpoint, directory_url).await` - Register with directory
- `discover(wanted_capabilities, directory_url).await` - Find agents
- `send_task(target_agent_id, action, input, directory_url).await` - Send task

### Server

- `A2AServer::new(...)` - Create server
- `handle_task(handler)` - Register task handler
- `run().await` - Start server
- `run_server(...)` - Convenience function

## See Also

- [Python SDK](../a2a_sdk.py)
- [TypeScript SDK](../typescript/)
- [Go SDK](../go/)
- [Specification](../SPEC.md)
