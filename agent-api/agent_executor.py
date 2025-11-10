from smolagents import CodeAgent, LiteLLMModel, DuckDuckGoSearchTool, VisitWebpageTool
from typing import Optional, List, Dict, Any
import logging
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from tenant_tool import TenantInfoTool

logger = logging.getLogger(__name__)

class AgentExecutor:
    """Wrapper for executing smolagents with multi-tenant isolation"""
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def execute(
        self,
        task: str,
        tools: Optional[List[str]] = None,
        model: Optional[str] = None,
        max_steps: int = 10
    ) -> Dict[str, Any]:
        """
        Execute an agent task using smolagents
        
        Args:
            task: The task description
            tools: List of tool names to enable
            model: LLM model to use
            max_steps: Maximum execution steps
            
        Returns:
            Dict with output and execution steps
        """
        logger.info(f"[Tenant: {self.tenant_id}] Executing task: {task[:100]}")
        
        try:
            # Run agent execution in thread pool to avoid blocking
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._execute_sync,
                task,
                tools,
                model,
                max_steps
            )
            return result
        except Exception as e:
            logger.error(f"[Tenant: {self.tenant_id}] Execution failed: {e}", exc_info=True)
            raise
    
    def _execute_sync(
        self,
        task: str,
        tools: Optional[List[str]],
        model: Optional[str],
        max_steps: int
    ) -> Dict[str, Any]:
        """Synchronous agent execution"""
        
        # Initialize model
        model_id = model or os.getenv("DEFAULT_MODEL", "claude-3-5-sonnet-20241022")
        
        # Determine which model provider to use
        if "claude" in model_id.lower() or "anthropic" in model_id.lower():
            # Use Anthropic Claude via LiteLLM
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if not anthropic_key:
                raise ValueError("ANTHROPIC_API_KEY not set for Claude models")
            
            # LiteLLM expects the model name with provider prefix
            if not model_id.startswith("anthropic/"):
                model_id = f"anthropic/{model_id}"
            
            llm_model = LiteLLMModel(model_id=model_id, api_key=anthropic_key)
            logger.info(f"Using Claude model: {model_id}")
            
        elif "gpt" in model_id.lower() or "openai" in model_id.lower():
            # Use OpenAI via LiteLLM
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                raise ValueError("OPENAI_API_KEY not set for OpenAI models")
            
            llm_model = LiteLLMModel(model_id=model_id, api_key=openai_key)
            logger.info(f"Using OpenAI model: {model_id}")
            
        else:
            # Default to Claude if no model specified
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if not anthropic_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
            
            model_id = "claude-3-5-sonnet-20241022"
            llm_model = LiteLLMModel(model_id=model_id, api_key=anthropic_key)
            logger.info(f"Using default Claude model: {model_id}")
        
        # Initialize tools
        available_tools = self._get_tools(tools)
        
        # Create agent
        agent = CodeAgent(
            tools=available_tools,
            model=llm_model,
            max_steps=max_steps,
            verbosity_level=1
        )
        
        # Execute task
        try:
            output = agent.run(task)
            
            # Extract execution steps
            steps = []
            if hasattr(agent, 'logs') and agent.logs:
                for i, log in enumerate(agent.logs):
                    steps.append({
                        "step": i + 1,
                        "action": log.get("action", "unknown"),
                        "observation": log.get("observation", ""),
                    })
            
            return {
                "output": str(output),
                "steps": steps,
                "model": model_id
            }
            
        except Exception as e:
            logger.error(f"Agent run failed: {e}", exc_info=True)
            raise
    
    def _get_tools(self, tool_names: Optional[List[str]]) -> List[Any]:
        """Get tool instances based on tool names"""
        
        # If empty list explicitly passed, return no tools
        if tool_names is not None and len(tool_names) == 0:
            return []
        
        # Map of available tools (tenant_info is always available)
        tool_map = {
            "web_search": DuckDuckGoSearchTool(),
            "visit_webpage": VisitWebpageTool(),
            "tenant_info": TenantInfoTool(tenant_id=self.tenant_id),
        }
        
        # If no tools specified (None), return default set including tenant_info
        if tool_names is None:
            return [
                tool_map["tenant_info"],
                tool_map["web_search"],
                tool_map["visit_webpage"]
            ]
        
        # Return requested tools
        tools = []
        for name in tool_names:
            if name in tool_map:
                tools.append(tool_map[name])
            else:
                logger.warning(f"Unknown tool: {name}")
        
        return tools
