/**
 * A2A Protocol - TypeScript SDK
 * Zero-dependency A2A client for Node.js
 */

// Simple UUID generation (works everywhere)
function generateId(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Fallback simple UUID
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

export interface AgentInfo {
  agentId: string;
  name: string;
  capabilities: string[];
  endpoint: string;
  registeredAt?: string;
}

export interface TaskParams {
  taskId: string;
  action: string;
  sender: string;
  input: Record<string, unknown>;
}

export interface TaskResult {
  taskId: string;
  status: 'completed' | 'failed' | 'cancelled' | 'timeout';
  output: Record<string, unknown>;
}

export interface JsonRpcRequest<T = unknown> {
  jsonrpc: '2.0';
  id: string;
  method: string;
  params: T;
}

export interface JsonRpcResponse<T = unknown> {
  jsonrpc: '2.0';
  id: string;
  result?: T;
  error?: {
    code: number;
    message: string;
    data?: unknown;
  };
}

/**
 * A2A Directory Client
 * For registering and discovering agents
 */
export class A2ADirectory {
  private baseUrl: string;

  constructor(directoryUrl: string = 'http://localhost:8080') {
    this.baseUrl = directoryUrl.replace(/\/$/, '');
  }

  private async request<T>(path: string, body?: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method: body ? 'POST' : 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      throw new Error(`A2A Directory error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Register an agent with the directory
   */
  async register(agent: Omit<AgentInfo, 'registeredAt'>): Promise<{ status: string; agentId: string }> {
    return this.request('/a2a/register', agent);
  }

  /**
   * Discover agents by capabilities
   */
  async discover(capabilities: string[]): Promise<{ agents: AgentInfo[] }> {
    return this.request('/a2a/discover', { capabilities });
  }

  /**
   * List all registered agents
   */
  async listAgents(): Promise<{ agents: AgentInfo[] }> {
    return this.request('/a2a/agents');
  }

  /**
   * Get specific agent info
   */
  async getAgent(agentId: string): Promise<AgentInfo> {
    return this.request(`/a2a/agents/${agentId}`);
  }
}

/**
 * A2A Agent Client
 * For sending tasks to other agents
 */
export class A2AAgentClient {
  private agentId: string;
  private name: string;
  private capabilities: string[];
  private directory: A2ADirectory;

  constructor(
    agentId: string,
    name: string,
    capabilities: string[],
    directoryUrl: string = 'http://localhost:8080'
  ) {
    this.agentId = agentId;
    this.name = name;
    this.capabilities = capabilities;
    this.directory = new A2ADirectory(directoryUrl);
  }

  /**
   * Register this agent with the directory
   */
  async register(endpoint: string): Promise<void> {
    await this.directory.register({
      agentId: this.agentId,
      name: this.name,
      capabilities: this.capabilities,
      endpoint,
    });
  }

  /**
   * Discover agents by capability
   */
  async discover(wantedCapabilities: string[]): Promise<AgentInfo | null> {
    const result = await this.directory.discover(wantedCapabilities);
    if (!result.agents || result.agents.length === 0) {
      return null;
    }
    return result.agents[0];
  }

  /**
   * Send a task to another agent
   */
  async sendTask(
    targetAgentId: string,
    action: string,
    input: Record<string, unknown>
  ): Promise<TaskResult> {
    // Get target agent's endpoint
    const target = await this.directory.getAgent(targetAgentId);

    const taskId = generateId();
    const request: JsonRpcRequest<TaskParams> = {
      jsonrpc: '2.0',
      id: taskId,
      method: 'a2a/task',
      params: {
        taskId,
        action,
        sender: this.agentId,
        input,
      },
    };

    const response = await fetch(target.endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Task failed: ${response.status}`);
    }

    const result: JsonRpcResponse<{ result: TaskResult }> = await response.json();

    if (result.error) {
      throw new Error(`A2A error: ${result.error.message}`);
    }

    return result.result!.result;
  }
}

// Helper function for quick setup
export function createAgent(
  agentId: string,
  name: string,
  capabilities: string[],
  directoryUrl?: string
): A2AAgentClient {
  return new A2AAgentClient(agentId, name, capabilities, directoryUrl);
}
