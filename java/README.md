# A2A Protocol Java SDK

Java SDK for the A2A (Agent-to-Agent) Protocol.

## Installation

### Maven

```xml
<dependency>
    <groupId>com.mentessaas</groupId>
    <artifactId>a2a-protocol</artifactId>
    <version>0.1.0</version>
</dependency>
```

### Gradle

```groovy
implementation 'com.mentessaas:a2a-protocol:0.1.0'
```

### Manual

```bash
# Build
cd java
mvn package

# Add to classpath
java -cp target/a2a-protocol-0.1.0.jar:$(ls ~/.m2/repository/com/fasterxml/jackson/core/jackson-databind/*/jackson-databind-*.jar | head -1) YourApp.java
```

## Quick Start

```java
import com.a2a.A2ASDK.A2AAgent;
import com.a2a.A2ASDK.AgentInfo;
import com.a2a.A2ASDK.TaskResult;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

public class Main {
    public static void main(String[] args) throws Exception {
        // Create an agent
        A2AAgent agent = new A2AAgent(
            "my-agent",
            "My Agent",
            Arrays.asList("search", "summarize")
        );

        // Register with directory
        agent.register("http://localhost:9001", "http://localhost:8080");

        // Discover another agent
        AgentInfo other = agent.discover(
            Arrays.asList("calculator"),
            "http://localhost:8080"
        );

        // Send a task
        Map<String, Object> input = new HashMap<>();
        input.put("a", 10);
        input.put("b", 20);

        TaskResult result = agent.sendTask(
            other.getAgentId(),
            "add",
            input,
            "http://localhost:8080"
        );

        System.out.println("Result: " + result.getOutput());
    }
}
```

## Running an Agent Server

```java
import com.a2a.A2ASDK.A2AServer;
import java.util.*;

public class ServerExample {
    public static void main(String[] args) {
        A2AServer server = new A2AServer(
            "calculator-agent",
            "Calculator Agent",
            Arrays.asList("math", "calculate", "add"),
            9001
        );

        server.handleTask((action, input, sender) -> {
            System.out.println("Received task: " + action + " from " + sender);
            
            if ("add".equals(action)) {
                double a = ((Number) input.get("a")).doubleValue();
                double b = ((Number) input.get("b")).doubleValue();
                
                Map<String, Object> result = new HashMap<>();
                result.put("result", a + b);
                return result;
            }
            
            return Map.of("error", "Unknown action");
        });

        server.run();
    }
}
```

## API

### A2AAgent

- `new A2AAgent(agentId, name, capabilities)` - Create a new agent
- `register(endpoint, directoryUrl)` - Register with directory
- `discover(wantedCapabilities, directoryUrl)` - Find agents
- `sendTask(targetAgentId, action, input, directoryUrl)` - Send task

### A2AServer

- `new A2AServer(agentId, name, capabilities, port)` - Create server
- `handleTask(handler)` - Register task handler
- `run()` - Start server

## See Also

- [Python SDK](../a2a_sdk.py)
- [TypeScript SDK](../typescript/)
- [Go SDK](../go/)
- [Rust SDK](../rust/)
- [Specification](../SPEC.md)
