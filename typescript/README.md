# A2A TypeScript SDK

TypeScript/JavaScript SDK for the A2A Protocol.

## Installation

```bash
npm install @org/a2a-sdk
# or
yarn add @org/a2a-sdk
```

## Quick Start

```typescript
import { A2ADirectory, A2AAgentClient, createAgent } from '@org/a2a-sdk';

// Option 1: Use directory directly
const directory = new A2ADirectory('http://localhost:8080');
const agents = await directory.listAgents();

// Option 2: Create an agent client
const agent = createAgent(
  'my-agent',
  'My Agent',
  ['search', 'analyze'],
  'http://localhost:8080'
);

// Register with endpoint
await agent.register('http://localhost:8081');

// Discover other agents
const searchAgent = await agent.discover(['search']);

// Send a task
const result = await agent.sendTask(
  searchAgent.agentId,
  'search',
  { query: 'AI news' }
);
```

## API

### A2ADirectory

```typescript
const dir = new A2ADirectory('http://localhost:8080');

// Register an agent
await dir.register({
  agentId: 'my-agent',
  name: 'My Agent',
  capabilities: ['search'],
  endpoint: 'http://localhost:8081'
});

// Discover agents by capability
const agents = await dir.discover(['search']);

// List all agents
const all = await dir.listAgents();

// Get specific agent
const agent = await dir.getAgent('my-agent');
```

### A2AAgentClient

```typescript
const client = new A2AAgentClient(
  'my-agent',
  'My Agent',
  ['search'],
  'http://localhost:8080'
);

// Register this agent
await client.register('http://localhost:8081');

// Discover others
const other = await client.discover(['analyze']);

// Send task
const result = await client.sendTask(
  'other-agent',
  'analyze',
  { data: '...' }
);
```

## Running the Demo

```bash
cd typescript
npm install
node test.mjs
```

## Requirements

- Node.js 18+ (for native fetch)
- Or any environment with fetch polyfill

## License

MIT
