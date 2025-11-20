# Agent Platform - Agentic AI SaaS on Omnistrate

**🚀 A production-ready, multi-tenant AI Agent Platform template for the KubeCon 2025 NA Omnistrate Challenge**

Transform your agentic AI service into a globally distributed SaaS offering in minutes! This template provides a complete foundation for building and deploying AI agent platforms on Omnistrate with:

- ✅ Multi-tenant architecture with automatic isolation
- ✅ HTTPS endpoints with TLS termination
- ✅ Production-ready FastAPI backend
- ✅ HuggingFace smolagents integration

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│              HTTPS with TLS Termination                   │
│         (Automatic cert provisioning by Omnistrate)       │
└─────────────────────┬────────────────────────────────────┘
                      │
         ┌────────────▼────────────┐
         │  Agent Runtime API      │
         │  (FastAPI + smolagents) │
         │                         │
         │  Available Tools:       │
         │  • tenant_info          │
         │  • web_search           │
         │  • visit_webpage        │
         └────┬─────────┬──────────┘
              │         │
      ┌───────▼──┐  ┌──▼───┐
      │PostgreSQL│  │Redis │
      │ Metadata │  │Cache │
      └──────────┘  └──────┘
```

## 🚀 Quick Start for New Omnistrate Users

### Prerequisites

1. **Sign up for Omnistrate**
   - Visit: https://omnistrate.cloud/signup
   - Complete account creation

2. **Install Omnistrate CLI**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/omnistrate-oss/omnistrate-ctl/main/install-ctl.sh | sh
   
   # Or download from: https://github.com/omnistrate/ctl/releases
   ```

3. **Login to Omnistrate**
   ```bash
   omctl login
   # Follow the prompts to authenticate
   ```

4. **Get Anthropic API Key** (for Claude)
   - Visit: https://console.anthropic.com/
   - Create an API key
   - Save it securely

5. **Integrate w/ your favor AI Copilot platform**
    - Leverage the Omnistrate FDE skill to iterate on your service with your Copilot tool (e.g., GitHub Copilot, Claude Code, etc.)
    - See: https://docs.omnistrate.com/getting-started/overview/#setup-your-ai-agent for detailed instructions.

### Step 1: Clone This Template

```bash
git clone https://github.com/omnistrate-community/kubecon-2025-agent-template
cd kubecon-2025-agent-template
```

### Step 2: Create Omnistrate Secret

Store your Claude API key securely:

```bash
omctl secret set DEV CLAUDE_KEY "your-anthropic-api-key-here"
```

### Step 3: Build Your PaaS on Omnistrate

```bash
omctl build --file compose-omnistrate.yaml --product-name "Agent Platform" --release-as-preferred
```

This command:
- Transforms your Docker Compose into Omnistrate service
- Configures multi-tenant deployment
- Sets up HTTPS with automatic TLS
- Sets up a self-serve customer portal

### Step 4: Access your self-serve customer portal

Wait for customer portal deployment to finish 
```bash
omctl service describe "Agent Platform" --output json | jq -r '. as $root | .serviceEnvironments[0] | .saasPortalStatus'
```
Once its in the RUNNING state, get the customer portal endpoint:
```bash
omctl service describe "Agent Platform" --output json | jq -r '. as $root | .serviceEnvironments[0] | "https://\(.saasPortalUrl)/service-plans?serviceId=\($root.id)&environmentId=\(.id)"'
```

Use your Omnistrate email and password to test your PaaS service as a customer. We automatically enable internal users as customers for pre-prod environments.

### Step 5: Deploy an instance of your application in the Dev Environment

You can use UI or use the CLI commands below to create instances:

```bash
# AWS (restricted to us-east-2 when testing with Omnistrate's AWS account)
omctl instance create \
  --service="Agent Platform" \
  --environment=Dev \
  --plan=Basic \
  --version=latest \
  --resource=agent-platform-root \
  --cloud-provider=aws \
  --region=us-east-2 \
  --param '{}' \
  --wait

# GCP (restricted to us-central1 when testing with Omnistrate's GCP project)
omctl instance create \
  --service="Agent Platform" \
  --environment=Dev \
  --plan=Basic \
  --version=latest \
  --resource=agent-platform-root \
  --cloud-provider=gcp \
  --region=us-central1 \
  --param '{}' \
  --wait

# Azure (restricted to eastus2 when testing with Omnistrate's Azure subscription)
omctl instance create \
  --service="Agent Platform" \
  --environment=Dev \
  --plan=Basic \
  --version=latest \
  --resource=agent-platform-root \
  --cloud-provider=azure \
  --region=eastus2 \
  --param '{}' \
  --wait
```

### Step 6: Get your application's HTTPS Endpoint

```bash
omctl instance list-endpoints <your-instance-id>
```

You'll get an HTTPS endpoint like:
```
https://agent-api.instance-xyz.hc-abc.us-east-2.aws.f2e0a955bb84.cloud
```

### Step 7: Test Your Agent Platform

```bash
# Health check
curl https://your-endpoint/health

# Get tenant info
curl https://your-endpoint/api/v1/tenant/info

# Execute an agent task
curl -X POST https://your-endpoint/api/v1/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": "What is 2 + 2? Just give me the number."
  }'
```

### Step 8: Make changes to the agent and publish new images

```bash
cd agent-api && docker build --platform linux/amd64 -t <custom-image-repo>/agent-runtime:v1.x --load .
docker push <custom-image-repo>/agent-runtime:v1.x

## Change the image in the compose file and build the service again
omctl build --file compose-omnistrate.yaml --product-name "Agent Platform" --release-as-preferred

## Update your existing deployment instance to migrate to the new version
omctl upgrade create [instanceID] --version=latest
```

🎉 **That's it!** Your AI agent platform is now running on Omnistrate with automatic multi-tenancy and HTTPS!

## 📖 Complete Getting Started Guide

For more detailed instructions, see the [Official Omnistrate Getting Started Guide](https://docs.omnistrate.com/getting-started/overview/).

## 🔌 API Endpoints

### Execute Agent Task
```bash
POST /api/v1/agent/execute

curl -X POST https://your-endpoint/api/v1/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": "What is the capital of France?",
    "max_steps": 10
  }'
```

### Get Execution Status
```bash
GET /api/v1/agent/execution/{execution_id}

curl https://your-endpoint/api/v1/agent/execution/{execution_id}
```

### List Executions
```bash
GET /api/v1/agent/executions?limit=50&offset=0

curl https://your-endpoint/api/v1/agent/executions?limit=50
```

### Health Check
```bash
GET /health

curl https://your-endpoint/health
```

## 🧰 Available Agent Tools

The Agent Platform includes the following **smolagents** tools that agents can use during execution:

### 1. **Tenant Info Tool** (`tenant_info`)
Access current tenant context information injected by Omnistrate. This tool allows agents to:
- Retrieve tenant ID, email, and name
- Get organization details
- Access instance metadata
- Personalize responses with customer information

**How it works:**
- Omnistrate injects system parameters as environment variables for each tenant
- The tool reads these environment variables to provide tenant context
- Enables agents to provide personalized, context-aware responses

**Example Usage:**
```bash
curl -X POST https://your-endpoint/api/v1/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": "What do you know about me?",
    "max_steps": 5
  }'
```

**Response:**
```json
{
  "execution_id": "7cd03665-e644-43ff-8d16-00be220f417c",
  "status": "completed",
  "result": "Based on the tenant information I have access to, here's what I know about you:\n\n**Personal Information:**\n- Name: Omnistrate Demo\n- Email: demo@omnistrate.com\n- Tenant ID: user-18ZZD6JBrS\n\n**Organization Details:**\n- Organization Name: Omnistrate Demo\n- Organization ID: org-TCl8TNH3b9\n\n**System Context:**\n- Instance ID: instance-9yrrrhfy5\n- Environment: Production\n\nThis is the context information associated with your current session.",
  "steps": []
}
```

### 2. **Web Search** (`web_search`)
Search the web using DuckDuckGo. Great for:
- Finding current information
- Research tasks
- Looking up facts
- Real-time data retrieval

**Implementation:** Uses `DuckDuckGoSearchTool` from smolagents

### 3. **Visit Webpage** (`visit_webpage`)
Visit and extract content from web pages. Useful for:
- Reading articles
- Extracting specific information
- Following up on search results
- Accessing documentation

**Implementation:** Uses `VisitWebpageTool` from smolagents

### Tool Configuration

**Default Tools:**
When no tools are specified, the agent has access to all three tools:
```python
# Default tools (when tools parameter is None or omitted)
["tenant_info", "web_search", "visit_webpage"]
```

**Custom Tool Selection:**
Specify which tools to enable:
```bash
curl -X POST https://your-endpoint/api/v1/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Search for the latest AI news",
    "tools": ["web_search", "visit_webpage"]
  }'
```

**Disable All Tools:**
Pass an empty array to use only the agent's reasoning capabilities:
```bash
curl -X POST https://your-endpoint/api/v1/agent/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": "What is 2+2?",
    "tools": []
  }'
```


## Detailed Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR CONTROL PLANE                           │
│                                                                 │
│  Customer Subscription → System Parameters Generation           │
│                                                                 │
│  $sys.tenant.userID = "user-abc123"                             │
│  $sys.tenant.email = "john@acme.com"                            │
│  $sys.tenant.name = "John Doe"                                  │
│  $sys.tenant.orgId = "org-xyz789"                               │
│  $sys.id = "instance-def456"                                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Inject as Environment Variables
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              CUSTOMER INSTANCE (Shared VM)                      │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  agent-api Container                                     │   │
│  │                                                          │   │
│  │  ENV: TENANT_ID=user-abc123                              │   │
│  │  ENV: TENANT_EMAIL=john@acme.com                         │   │
│  │  ENV: OMNISTRATE_INSTANCE_ID=instance-def456             │   │
│  │                                                          │   │
│  │  Agent Executor (smolagents):                            │   │
│  │  ┌──────────────────────────────────────────┐            │   │
│  │  │ Available Tools:                         │            │   │
│  │  │ • tenant_info (TenantInfoTool)           │            │   │
│  │  │   - Reads Omnistrate system variables    │            │   │
│  │  │   - Returns tenant context               │            │   │
│  │  │ • web_search (DuckDuckGoSearchTool)      │            │   │
│  │  │   - DuckDuckGo integration               │            │   │
│  │  │ • visit_webpage (VisitWebpageTool)       │            │   │
│  │  │   - Web scraping capability              │            │   │
│  │  └──────────────────────────────────────────┘            │   │
│  │                                                          │   │
│  │  API Logic:                                              │   │
│  │  ┌──────────────────────────────────────────┐            │   │
│  │  │ get_tenant_id():                         │            │   │
│  │  │     return TENANT_ID                     │            │   │
│  │  └──────────────────────────────────────────┘            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                         │                                       │
│                         │ Tenant ID: user-abc123                │
│                         ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  postgres Container                                      │   │
│  │                                                          │   │
│  │  agent_executions table:                                 │   │
│  │  ┌────────────┬────────────┬─────────┬─────────────┐     │   │
│  │  │ id         │ tenant_id  │ task    │ result      │     │   │
│  │  ├────────────┼────────────┼─────────┼─────────────┤     │   │
│  │  │ exec-1     │ user-abc123│ Task 1  │ Result 1    │     │   │
│  │  │ exec-2     │ user-abc123│ Task 2  │ Result 2    │     │   │
│  │  └────────────┴────────────┴─────────┴─────────────┘     │   │
│  │                                                          │   │
│  │  All queries filtered by tenant_id = user-abc123         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  redis Container                                         │   │
│  │  Session state isolated by tenant_id prefix              │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Multi-Customer Deployment

```
CUSTOMER A                          CUSTOMER B                          CUSTOMER C
┌──────────────┐                   ┌──────────────┐                   ┌──────────────┐
│ Subscription │                   │ Subscription │                   │ Subscription │
└──────┬───────┘                   └──────┬───────┘                   └──────┬───────┘
       │                                  │                                  │
       │ Omnistrate deploys               │ Omnistrate deploys               │ Omnistrate deploys
       ▼                                  ▼                                  ▼
┌────────────────┐              ┌────────────────┐              ┌────────────────┐
│ Instance A     │              │ Instance B     │              │ Instance C     │
│                │              │                │              │                │
│ Tenant ID:     │              │ Tenant ID:     │              │ Tenant ID:     │
│ user-aaa       │              │ user-bbb       │              │ user-ccc       │
│                │              │                │              │                │
│ agent-api      │              │ agent-api      │              │ agent-api      │
│ postgres       │              │ postgres       │              │ postgres       │
│ redis          │              │ redis          │              │ redis          │
│                │              │                │              │                │
│ Data isolated  │              │ Data isolated  │              │ Data isolated  │
│ by user-aaa    │              │ by user-bbb    │              │ by user-ccc    │
└────────────────┘              └────────────────┘              └────────────────┘

         ▲                               ▲                               ▲
         │                               │                               │
         │                               │                               │
         └───────────────────────────────┴───────────────────────────────┘
                        All share VMs in Provider Account
                        (Multi-tenant PaaS Model)
```

### API Request Flow

```
User Request
     │
     │ POST /api/v1/agent/execute
     │ {task: "What is 2+2?", tools: ["tenant_info"]}
     │ 
     ▼
┌─────────────────────────────────────┐
│  FastAPI Endpoint                   │
│  @app.post("/api/v1/agent/execute") │
└────────────┬────────────────────────┘
             │
             │ Depends(get_tenant_id)
             ▼
┌─────────────────────────────────────┐
│  get_tenant_id()                    │
│                                     │
│  return TENANT_ID                   │
│  (from environment variable)        │
│                                     │
│  tenant_id = "user-abc123"          │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Create AgentExecution              │
│  execution.tenant_id = "user-abc123"│
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  AgentExecutor._get_tools()         │
│                                     │
│  Initialize smolagents tools:       │
│  • TenantInfoTool(tenant_id)        │
│  • DuckDuckGoSearchTool()           │
│  • VisitWebpageTool()               │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Execute Agent (smolagents)         │
│  CodeAgent.run(task, tools)         │
│                                     │
│  Agent can invoke:                  │
│  - tenant_info tool                 │
│  - web_search tool                  │
│  - visit_webpage tool               │
│                                     │
│  Store results with tenant_id       │
└────────────┬────────────────────────┘
             │
             ▼
       Return Result
       {
         execution_id: "...",
         status: "completed",
         result: "...",
         steps: [...]
       }
```
