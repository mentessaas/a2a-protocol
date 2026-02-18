# A2A Protocol C# SDK

C# SDK for the A2A (Agent-to-Agent) Protocol.

## Installation

### NuGet

```bash
dotnet add package A2A-Protocol
```

Or add to .csproj:

```xml
<PackageReference Include="A2A-Protocol" Version="0.1.0" />
```

## Quick Start

```csharp
using A2A;

var agent = new A2ASDK.A2AAgent(
    "my-agent",
    "My Agent",
    new List<string> { "search", "summarize" }
);

// Register with directory
await agent.RegisterAsync("http://localhost:9001", "http://localhost:8080");

// Discover another agent
var other = await agent.DiscoverAsync(
    new List<string> { "calculator" },
    "http://localhost:8080"
);

// Send a task
var input = new Dictionary<string, object>
{
    { "a", 10 },
    { "b", 20 }
};

var result = await agent.SendTaskAsync(
    other.AgentId,
    "add",
    input,
    "http://localhost:8080"
);

Console.WriteLine($"Result: {result.Output}");
```

## Running an Agent Server

```csharp
using A2A;

var server = new A2ASDK.A2AServer(
    "calculator-agent",
    "Calculator Agent",
    new List<string> { "math", "calculate", "add" },
    9001
);

server.HandleTask((action, input, sender) =>
{
    Console.WriteLine($"Received task: {action} from {sender}");

    if (action == "add")
    {
        var a = Convert.ToDouble(input["a"]);
        var b = Convert.ToDouble(input["b"]);
        
        return new Dictionary<string, object>
        {
            { "result", a + b }
        };
    }

    return new Dictionary<string, object>
    {
        { "error", "Unknown action" }
    };
});

server.Run();
```

## API

### A2AAgent

- `new A2AAgent(agentId, name, capabilities)` - Create a new agent
- `RegisterAsync(endpoint, directoryUrl)` - Register with directory
- `DiscoverAsync(wantedCapabilities, directoryUrl)` - Find agents
- `SendTaskAsync(targetAgentId, action, input, directoryUrl)` - Send task

### A2AServer

- `new A2AServer(agentId, name, capabilities, port)` - Create server
- `HandleTask(handler)` - Register task handler
- `Run()` - Start server

## See Also

- [Python SDK](../a2a_sdk.py)
- [TypeScript SDK](../typescript/)
- [Go SDK](../go/)
- [Rust SDK](../rust/)
- [Java SDK](../java/)
- [Specification](../SPEC.md)
