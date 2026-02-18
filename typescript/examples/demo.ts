/**
 * A2A TypeScript Demo
 * Run: npx ts-node examples/demo.ts
 * Or: npx tsx examples/demo.ts
 */

import { A2ADirectory, A2AAgentClient } from '../a2a';

async function demo() {
  console.log('🔷 A2A TypeScript SDK Demo\n');

  const directory = new A2ADirectory('http://localhost:8080');

  // List current agents
  console.log('📋 Registered agents:');
  const agents = await directory.listAgents();
  console.log(`   Found ${agents.agents.length} agents\n`);

  // Discover echo agent
  console.log('🔍 Discovering agents with "echo" capability...');
  const echo = await directory.discover(['echo']);
  
  if (echo) {
    console.log(`   Found: ${echo.name} (${echo.agentId})`);

    // Create a client to send tasks
    const client = new A2AAgentClient(
      'ts-demo-client',
      'TypeScript Demo Client',
      ['demo'],
      'http://localhost:8080'
    );

    // Send a task
    console.log('\n📤 Sending task to Echo Agent...');
    const result = await client.sendTask(
      echo.agentId,
      'echo',
      { message: 'Hello from TypeScript!' }
    );

    console.log(`   Status: ${result.status}`);
    console.log(`   Output: ${JSON.stringify(result.output)}`);
  } else {
    console.log('   No echo agent found!');
  }

  // Discover researcher
  console.log('\n🔍 Discovering agents with "research" capability...');
  const researcher = await directory.discover(['research']);
  
  if (researcher) {
    console.log(`   Found: ${researcher.name} (${researcher.agentId})`);
    
    const client = new A2AAgentClient(
      'ts-demo-client',
      'TypeScript Demo Client',
      ['demo'],
      'http://localhost:8080'
    );

    console.log('\n📤 Sending research task...');
    const result = await client.sendTask(
      researcher.agentId,
      'research',
      { query: 'What is A2A?' }
    );

    console.log(`   Status: ${result.status}`);
    // Truncate output for display
    const outputStr = JSON.stringify(result.output);
    console.log(`   Output: ${outputStr.substring(0, 200)}...`);
  } else {
    console.log('   No researcher found!');
  }

  console.log('\n✅ Demo complete!');
}

demo().catch(console.error);
