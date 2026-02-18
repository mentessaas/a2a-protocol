using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace A2A
{
    /// <summary>
    /// A2A Protocol C# SDK
    /// </summary>
    public class A2ASDK
    {
        private static readonly HttpClient httpClient = new HttpClient();

        // ============ Models ============

        public class AgentInfo
        {
            public string AgentId { get; set; }
            public string Name { get; set; }
            public List<string> Capabilities { get; set; }
            public string Endpoint { get; set; }
            public string RegisteredAt { get; set; }
        }

        public class TaskResult
        {
            public string TaskId { get; set; }
            public string Status { get; set; }
            public Dictionary<string, object> Output { get; set; }
        }

        // ============ A2AAgent ============

        public class A2AAgent
        {
            public string AgentId { get; private set; }
            public string Name { get; private set; }
            public List<string> Capabilities { get; private set; }
            public string Endpoint { get; private set; }

            public A2AAgent(string agentId, string name, List<string> capabilities)
            {
                AgentId = agentId;
                Name = name;
                Capabilities = capabilities;
            }

            public async Task RegisterAsync(string endpoint, string directoryUrl)
            {
                Endpoint = endpoint;

                var parameters = new Dictionary<string, object>
                {
                    { "agentId", AgentId },
                    { "name", Name },
                    { "capabilities", Capabilities },
                    { "endpoint", endpoint }
                };

                await RequestAsync($"{directoryUrl.TrimEnd('/')}/a2a/register", "a2a/register", parameters);
                Console.WriteLine($"✅ Registered: {AgentId}");
            }

            public async Task<AgentInfo> DiscoverAsync(List<string> wantedCapabilities, string directoryUrl)
            {
                var parameters = new Dictionary<string, object>
                {
                    { "capabilities", wantedCapabilities }
                };

                var result = await RequestAsync($"{directoryUrl.TrimEnd('/')}/a2a/discover", "a2a/discover", parameters);

                if (result.TryGetValue("agents", out var agentsObj) && agentsObj is JsonElement agentsArray)
                {
                    var agents = JsonSerializer.Deserialize<List<AgentInfo>>(agentsArray.GetRawText());
                    if (agents != null && agents.Count > 0)
                    {
                        return agents[0];
                    }
                }

                return null;
            }

            public async Task<TaskResult> SendTaskAsync(string targetAgentId, string action, 
                Dictionary<string, object> input, string directoryUrl)
            {
                // Get target agent info
                var agentResponse = await httpClient.GetAsync($"{directoryUrl.TrimEnd('/')}/a2a/agents/{targetAgentId}");
                if (!agentResponse.IsSuccessStatusCode)
                {
                    throw new Exception($"Agent not found: {targetAgentId}");
                }

                var agentJson = await agentResponse.Content.ReadAsStringAsync();
                var target = JsonSerializer.Deserialize<AgentInfo>(agentJson);

                // Send task
                var parameters = new Dictionary<string, object>
                {
                    { "taskId", Guid.NewGuid().ToString() },
                    { "action", action },
                    { "sender", AgentId },
                    { "input", input }
                };

                var result = await RequestAsync(target.Endpoint, "a2a/task", parameters);
                return JsonSerializer.Deserialize<TaskResult>(JsonSerializer.Serialize(result));
            }

            private async Task<Dictionary<string, object>> RequestAsync(string url, string method, Dictionary<string, object> parameters)
            {
                var requestBody = new Dictionary<string, object>
                {
                    { "jsonrpc", "2.0" },
                    { "id", Guid.NewGuid().ToString() },
                    { "method", method },
                    { "params", parameters }
                };

                var json = JsonSerializer.Serialize(requestBody);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await httpClient.PostAsync(url, content);

                if (!response.IsSuccessStatusCode)
                {
                    throw new Exception($"HTTP {response.StatusCode}");
                }

                var responseJson = await response.Content.ReadAsStringAsync();
                var resp = JsonSerializer.Deserialize<Dictionary<string, object>>(responseJson);

                if (resp.ContainsKey("error"))
                {
                    var error = (JsonElement)resp["error"];
                    throw new Exception($"RPC Error: {error.GetProperty("message").GetString()}");
                }

                if (resp.TryGetValue("result", out var result))
                {
                    return ((JsonElement)result).Deserialize<Dictionary<string, object>>();
                }

                throw new Exception("No result in response");
            }
        }

        // ============ A2AServer ============

        public delegate Dictionary<string, object> TaskHandler(string action, Dictionary<string, object> input, string sender);

        public class A2AServer
        {
            public string AgentId { get; }
            public string Name { get; }
            public List<string> Capabilities { get; }
            public int Port { get; }
            public string Endpoint => $"http://localhost:{Port}";

            private TaskHandler _taskHandler;

            public A2AServer(string agentId, string name, List<string> capabilities, int port)
            {
                AgentId = agentId;
                Name = name;
                Capabilities = capabilities;
                Port = port;
            }

            public void HandleTask(TaskHandler handler)
            {
                _taskHandler = handler;
            }

            public void Run()
            {
                Console.WriteLine($"🤖 Agent '{AgentId}' running on port {Port}");
                // In production, use ASP.NET Core
                // This is a placeholder
                Thread.Sleep(Timeout.Infinite);
            }
        }
    }
}
