/**
 * A2A TypeScript SDK - Simple Test
 */

const DIRECTORY_URL = 'http://localhost:8080';

async function request(path, body) {
  const response = await fetch(`${DIRECTORY_URL}${path}`, {
    method: body ? 'POST' : 'GET',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  return response.json();
}

async function discover(capabilities) {
  return request('/a2a/discover', { capabilities });
}

async function getAgent(agentId) {
  return request(`/a2a/agents/${agentId}`);
}

async function sendTask(targetAgentId, action, input) {
  const target = await getAgent(targetAgentId);
  
  const taskId = crypto.randomUUID();
  const response = await fetch(target.endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: taskId,
      method: 'a2a/task',
      params: { taskId, action, sender: 'ts-client', input }
    })
  });
  
  return response.json();
}

async function demo() {
  console.log('🔷 A2A TypeScript SDK Demo\n');
  
  // List agents
  console.log('📋 Registered agents:');
  const agents = await request('/a2a/agents');
  console.log(`   Found ${agents.agents.length} agents\n`);
  
  // Discover echo
  console.log('🔍 Discovering agents with "echo"...');
  const result = await discover(['echo']);
  console.log('   Raw result:', JSON.stringify(result));
  
  if (result.agents && result.agents[0]) {
    const echo = result.agents[0];
    console.log(`   Found: ${echo.name} (${echo.agentId})`);
    
    console.log('\n📤 Sending task to Echo Agent...');
    const taskResult = await sendTask(echo.agentId, 'echo', { message: 'Hello from TypeScript!' });
    console.log('   Result:', JSON.stringify(taskResult, null, 2));
  }
  
  console.log('\n✅ Done!');
}

demo().catch(console.error);
