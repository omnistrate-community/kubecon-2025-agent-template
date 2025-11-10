"""
Tenant Information Tool for AI Agents

This tool allows agents to access tenant context information during execution.
"""

from smolagents import Tool
import os
import logging

logger = logging.getLogger(__name__)


class TenantInfoTool(Tool):
    """Tool that provides tenant context information to the agent"""
    
    name = "get_tenant_info"
    description = """
    Retrieves information about the current tenant (customer) context.
    
    This tool provides:
    - Tenant ID: Unique identifier for the customer
    - Tenant Email: Customer's email address
    - Tenant Name: Customer's display name
    - Organization ID: Organization identifier
    - Organization Name: Organization display name
    - Instance ID: Current deployment instance
    
    Use this when you need to:
    - Personalize responses with customer information
    - Include tenant context in your output
    - Reference the current customer in your response
    - Access organization details
    
    Args:
        None
    
    Returns:
        A dictionary containing tenant information
    """
    
    inputs = {}
    output_type = "string"
    
    def __init__(self, tenant_id: str):
        """
        Initialize the tenant info tool with tenant context
        
        Args:
            tenant_id: The tenant ID for this execution context
        """
        super().__init__()
        self.tenant_id = tenant_id
    
    def forward(self) -> str:
        """
        Retrieve tenant information from environment variables
        
        Returns:
            JSON string with tenant information
        """
        try:
            tenant_info = {
                "tenant_id": self.tenant_id,
                "tenant_email": os.getenv("TENANT_EMAIL", "unknown"),
                "tenant_name": os.getenv("TENANT_NAME", "unknown"),
                "org_id": os.getenv("TENANT_ORG_ID", "unknown"),
                "org_name": os.getenv("TENANT_ORG_NAME", "unknown"),
                "instance_id": os.getenv("OMNISTRATE_INSTANCE_ID", "unknown"),
                "resource_id": os.getenv("OMNISTRATE_RESOURCE_ID", "unknown"),
                "is_production": os.getenv("TENANT_ID") is not None
            }
            
            logger.info(f"[Tenant: {self.tenant_id}] Tenant info retrieved by agent")
            
            # Format as readable string for the agent
            info_str = f"""Tenant Information:
- Tenant ID: {tenant_info['tenant_id']}
- Email: {tenant_info['tenant_email']}
- Name: {tenant_info['tenant_name']}
- Organization: {tenant_info['org_name']} (ID: {tenant_info['org_id']})
- Instance: {tenant_info['instance_id']}
- Environment: {'Production' if tenant_info['is_production'] else 'Development'}"""
            
            return info_str
            
        except Exception as e:
            logger.error(f"Error retrieving tenant info: {e}", exc_info=True)
            return f"Error retrieving tenant information: {str(e)}"
