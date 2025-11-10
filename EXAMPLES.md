# Agent Platform API - Usage Examples

## Example 1: Simple Math Calculation

```bash
curl -X POST http://your-instance.omnistrate.com/api/v1/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Calculate 15% tip on a $87.50 restaurant bill",
    "max_steps": 5
  }'
```

## Example 2: Web Search and Summarization

```bash
curl -X POST http://your-instance.omnistrate.com/api/v1/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Search for recent news about renewable energy and provide a brief summary of the top 3 findings",
    "tools": ["web_search", "visit_webpage"],
    "max_steps": 15
  }'
```

## Example 3: Research Task

```bash
curl -X POST http://your-instance.omnistrate.com/api/v1/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Find information about HuggingFace smolagents and explain what it is in 2-3 sentences",
    "tools": ["web_search", "visit_webpage"],
    "max_steps": 10,
    "metadata": {
      "category": "research",
      "priority": "medium"
    }
  }'
```

## Example 4: Get Execution Status

```bash
# Replace {execution_id} with actual ID from previous request
curl -X GET http://your-instance.omnistrate.com/api/v1/agent/execution/{execution_id}
```

## Example 5: List All Executions

```bash
curl -X GET "http://your-instance.omnistrate.com/api/v1/agent/executions?limit=20&offset=0"
```

## Example 6: Using Python

```python
import requests

API_BASE = "http://your-instance.omnistrate.com"

def execute_agent(task: str, tools: list = None):
    response = requests.post(
        f"{API_BASE}/api/v1/agent/execute",
        headers={"Content-Type": "application/json"},
        json={
            "task": task,
            "tools": tools or ["web_search"],
            "max_steps": 10
        }
    )
    return response.json()

# Example usage
result = execute_agent(
    task="What is the capital of France and what's the population?",
    tools=["web_search", "visit_webpage"]
)

print(f"Execution ID: {result['execution_id']}")
print(f"Status: {result['status']}")
print(f"Result: {result['result']}")
```

## Example 7: Using JavaScript/Node.js

```javascript
const axios = require('axios');

const API_BASE = 'http://your-instance.omnistrate.com';

async function executeAgent(task, tools = ['web_search']) {
  try {
    const response = await axios.post(
      `${API_BASE}/api/v1/agent/execute`,
      {
        task: task,
        tools: tools,
        max_steps: 10
      },
      {
        headers: {'Content-Type': 'application/json'}
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
    throw error;
  }
}

// Example usage
executeAgent(
  'Search for Python programming tutorials and recommend the top 3',
  ['web_search', 'visit_webpage']
).then(result => {
  console.log('Execution ID:', result.execution_id);
  console.log('Status:', result.status);
  console.log('Result:', result.result);
});
```

## Example 8: With Custom Model

```bash
curl -X POST http://your-instance.omnistrate.com/api/v1/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Explain quantum computing in simple terms",
    "model": "meta-llama/Llama-3.2-3B-Instruct",
    "max_steps": 8
  }'
```

## Example 9: Complex Multi-Step Task

```bash
curl -X POST http://your-instance.omnistrate.com/api/v1/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Research the top 3 cloud providers, compare their pricing for compute instances, and create a summary table",
    "tools": ["web_search", "visit_webpage"],
    "max_steps": 20,
    "metadata": {
      "project": "cloud-migration",
      "requester": "john@acme.com"
    }
  }'
```

## Response Format

All execution endpoints return:

```json
{
  "execution_id": "abc123-def456-ghi789",
  "status": "completed",  // or "running", "failed"
  "result": "The agent's final output...",
  "error": null,  // Error message if failed
  "steps": [
    {
      "step": 1,
      "action": "web_search",
      "observation": "Search results..."
    },
    {
      "step": 2,
      "action": "visit_webpage",
      "observation": "Page content..."
    }
  ],
  "created_at": "2024-01-01T00:00:00",
  "completed_at": "2024-01-01T00:01:30"
}
```

## Error Handling

### Missing Tenant ID Configuration
```json
{
  "detail": "TENANT_ID not configured. This service must be deployed via Omnistrate."
}
```

This error occurs when the service is not properly deployed on Omnistrate or TENANT_ID is not set.

### Execution Failed
```json
{
  "execution_id": "abc123",
  "status": "failed",
  "error": "Agent execution timeout after 300 seconds",
  "result": null
}
```

### Not Found
```json
{
  "detail": "Execution not found"
}
```

## Rate Limiting (Future)

Once implemented, rate limits will return:

```json
{
  "detail": "Rate limit exceeded",
  "retry_after": 60
}
```

## Best Practices

1. **No Tenant ID Management**: Tenant ID is automatic from Omnistrate, no manual management needed
2. **Set appropriate max_steps**: More steps = longer execution time
3. **Use metadata**: Track execution context for debugging
4. **Poll for status**: For long-running tasks, poll the status endpoint
5. **Handle errors gracefully**: Check status field before using result
6. **Limit scope**: More specific tasks = better results

## Monitoring Execution

```bash
# Get execution status
EXECUTION_ID="abc123-def456"

watch -n 2 'curl -s http://your-instance.omnistrate.com/api/v1/agent/execution/$EXECUTION_ID | jq ".status"'
```

## Local Testing

For local development, you must set TENANT_ID in your environment:

```bash
# Set environment variable
export TENANT_ID="test-tenant-local"

# Or uncomment in compose.yaml:
# TENANT_ID: "test-tenant-local"

# Then test
curl -X POST http://localhost:8000/api/v1/agent/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "What is 10 * 15?", "max_steps": 3}'
```
