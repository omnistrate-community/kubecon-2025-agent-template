#!/usr/bin/env python3
"""
Test script for Agent Platform API

Note: This requires TENANT_ID to be set in the environment.
For local testing, set it in compose.yaml or via environment variable.
"""

import requests
import json
import time
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Health check passed\n")

def test_tenant_info():
    """Test tenant info endpoint"""
    print("👤 Testing tenant info...")
    
    response = requests.get(f"{API_BASE_URL}/api/v1/tenant/info")
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Tenant ID: {result['tenant_id']}")
        print(f"Is Omnistrate: {result.get('is_omnistrate_deployment', False)}")
        if result.get('is_omnistrate_deployment'):
            print(f"Org Name: {result.get('org_name')}")
            print(f"Instance ID: {result.get('instance_id')}")
        print("✅ Tenant info passed\n")
    else:
        print(f"❌ Error: {response.text}\n")
        print("Make sure TENANT_ID is set in compose.yaml for local testing")

def test_agent_execution():
    """Test agent execution"""
    print("🤖 Testing agent execution...")
    
    payload = {
        "task": "What is 5 + 7? Calculate and return the result.",
        "max_steps": 5,
        "metadata": {"test": "simple_math"}
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/v1/agent/execute",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Execution ID: {result['execution_id']}")
        print(f"Status: {result['status']}")
        print(f"Result: {result.get('result', 'N/A')[:200]}")
        print(f"Steps: {len(result.get('steps', []))} steps")
        print("✅ Agent execution passed\n")
        return result['execution_id']
    else:
        print(f"❌ Error: {response.text}")
        return None

def test_get_execution(execution_id: str):
    """Test getting execution status"""
    print(f"📊 Testing get execution status for {execution_id}...")
    
    response = requests.get(
        f"{API_BASE_URL}/api/v1/agent/execution/{execution_id}"
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Execution Status: {result['status']}")
        print(f"Created: {result['created_at']}")
        print("✅ Get execution passed\n")
    else:
        print(f"❌ Error: {response.text}\n")

def test_list_executions():
    """Test listing executions"""
    print("📋 Testing list executions...")
    
    response = requests.get(
        f"{API_BASE_URL}/api/v1/agent/executions?limit=10"
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        results = response.json()
        print(f"Found {len(results)} executions")
        print("✅ List executions passed\n")
    else:
        print(f"❌ Error: {response.text}\n")

def main():
    print("=" * 60)
    print("Agent Platform API - Test Suite")
    print("=" * 60 + "\n")
    
    try:
        # Test health check
        test_health_check()
        
        # Test tenant info
        test_tenant_info()
        
        # Test agent execution
        execution_id = test_agent_execution()
        
        if execution_id:
            # Wait a moment for execution to process
            time.sleep(2)
            
            # Test get execution
            test_get_execution(execution_id)
            
            # Test list executions
            test_list_executions()
        
        print("=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Is the server running?")
        print("Start the server with: docker-compose up")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
