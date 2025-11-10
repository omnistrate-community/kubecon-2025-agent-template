from sqlalchemy import Column, String, DateTime, JSON, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from database import Base

class AgentExecution(Base):
    """Model for storing agent execution history and results"""
    __tablename__ = "agent_executions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    
    # Execution details
    task = Column(Text, nullable=False)
    status = Column(String, nullable=False)  # running, completed, failed
    result = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    
    # Agent configuration
    model = Column(String, nullable=True)
    steps = Column(JSON, nullable=True)
    exec_metadata = Column(JSON, nullable=True)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<AgentExecution(id={self.id}, tenant_id={self.tenant_id}, status={self.status})>"
