from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import os

from database import engine, get_db, Base
from models import AgentExecution
from agent_executor import AgentExecutor
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Agent Platform API...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down Agent Platform API...")
    await engine.dispose()

app = FastAPI(
    title="Agent Platform API",
    description="REST API for executing AI agents using HuggingFace smolagents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class AgentExecutionRequest(BaseModel):
    task: str = Field(..., description="The task for the agent to execute")
    tools: Optional[List[str]] = Field(default=None, description="List of tool names to enable")
    model: Optional[str] = Field(default=None, description="LLM model to use")
    max_steps: Optional[int] = Field(default=10, description="Maximum execution steps")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class AgentExecutionResponse(BaseModel):
    execution_id: str
    status: str
    result: Optional[str] = None
    error: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    redis: str

# Dependency for tenant isolation
async def get_tenant_id() -> str:
    """
    Get tenant ID from Omnistrate system parameters.
    
    Each Omnistrate deployment is for a SPECIFIC customer/tenant.
    The tenant ID is automatically injected via $sys.tenant.userID.
    
    There is NO scenario where a deployment is shared between customers.
    Each customer subscription creates a dedicated instance with its own tenant ID.
    """
    tenant_id = os.getenv("TENANT_ID")
    
    if not tenant_id:
        raise HTTPException(
            status_code=500,
            detail="TENANT_ID not configured. This service must be deployed via Omnistrate."
        )
    
    return tenant_id

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check database
        async with engine.connect() as conn:
            await conn.execute(select(1))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # TODO: Add Redis health check
    redis_status = "healthy"
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        version="1.0.0",
        database=db_status,
        redis=redis_status
    )

# Omnistrate tenant info endpoint
@app.get("/api/v1/tenant/info")
async def get_tenant_info(tenant_id: str = Depends(get_tenant_id)):
    """
    Get tenant information from Omnistrate system parameters.
    
    Returns tenant metadata that was injected by Omnistrate during deployment.
    Each deployment serves a single customer/tenant.
    """
    return {
        "tenant_id": tenant_id,
        "tenant_email": os.getenv("TENANT_EMAIL"),
        "tenant_name": os.getenv("TENANT_NAME"),
        "org_id": os.getenv("TENANT_ORG_ID"),
        "org_name": os.getenv("TENANT_ORG_NAME"),
        "instance_id": os.getenv("OMNISTRATE_INSTANCE_ID"),
        "resource_id": os.getenv("OMNISTRATE_RESOURCE_ID"),
        "service_id": os.getenv("OMNISTRATE_SERVICE_ID"),
        "plan_id": os.getenv("OMNISTRATE_PLAN_ID"),
        "is_omnistrate_deployment": os.getenv("TENANT_ID") is not None
    }

# Agent execution endpoint
@app.post("/api/v1/agent/execute", response_model=AgentExecutionResponse)
async def execute_agent(
    request: AgentExecutionRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute an agent task
    
    Tenant ID is automatically determined from Omnistrate system parameters.
    Each deployment serves a single customer/tenant.
    
    - **task**: The task description for the agent
    - **tools**: Optional list of tools to enable
    - **model**: Optional LLM model override
    - **max_steps**: Maximum execution steps (default: 10)
    - **metadata**: Additional metadata to store
    """
    logger.info(f"Executing agent task for tenant {tenant_id}: {request.task[:100]}")
    
    try:
        # Create execution record
        execution = AgentExecution(
            tenant_id=tenant_id,
            task=request.task,
            status="running",
            model=request.model or os.getenv("DEFAULT_MODEL"),
            exec_metadata=request.metadata or {}
        )
        db.add(execution)
        await db.commit()
        await db.refresh(execution)
        
        # Execute agent
        executor = AgentExecutor(tenant_id=tenant_id)
        result = await executor.execute(
            task=request.task,
            tools=request.tools,
            model=request.model,
            max_steps=request.max_steps
        )
        
        # Update execution record
        execution.status = "completed"
        execution.result = result["output"]
        execution.steps = result.get("steps", [])
        execution.completed_at = datetime.utcnow()
        await db.commit()
        
        return AgentExecutionResponse(
            execution_id=execution.id,
            status=execution.status,
            result=execution.result,
            steps=execution.steps,
            created_at=execution.created_at,
            completed_at=execution.completed_at
        )
        
    except Exception as e:
        logger.error(f"Agent execution failed: {e}", exc_info=True)
        
        # Update execution record with error
        execution.status = "failed"
        execution.error = str(e)
        execution.completed_at = datetime.utcnow()
        await db.commit()
        
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

# Get execution status
@app.get("/api/v1/agent/execution/{execution_id}", response_model=AgentExecutionResponse)
async def get_execution_status(
    execution_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the status and results of an agent execution.
    
    Tenant ID is automatically determined from Omnistrate system parameters.
    Only returns executions for the current tenant.
    """
    result = await db.execute(
        select(AgentExecution).where(
            AgentExecution.id == execution_id,
            AgentExecution.tenant_id == tenant_id
        )
    )
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return AgentExecutionResponse(
        execution_id=execution.id,
        status=execution.status,
        result=execution.result,
        error=execution.error,
        steps=execution.steps,
        created_at=execution.created_at,
        completed_at=execution.completed_at
    )

# List executions for tenant
@app.get("/api/v1/agent/executions", response_model=List[AgentExecutionResponse])
async def list_executions(
    tenant_id: str = Depends(get_tenant_id),
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    List agent executions for the current tenant.
    
    Tenant ID is automatically determined from Omnistrate system parameters.
    """
    result = await db.execute(
        select(AgentExecution)
        .where(AgentExecution.tenant_id == tenant_id)
        .order_by(AgentExecution.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    executions = result.scalars().all()
    
    return [
        AgentExecutionResponse(
            execution_id=execution.id,
            status=execution.status,
            result=execution.result,
            error=execution.error,
            steps=execution.steps,
            created_at=execution.created_at,
            completed_at=execution.completed_at
        )
        for execution in executions
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
