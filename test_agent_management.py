"""
Test script for Agent Management MySQL implementation.
This script demonstrates the new agent management flow.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword"

def test_agent_management():
    """Test the complete agent management flow."""
    
    # 1. Login to get JWT token
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed. Make sure you have a test user created.")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create an agent
    agent_data = {
        "agent_config": {
            "agent_name": "Test MySQL Agent",
            "agent_type": "simple",
            "tasks": [
                {
                    "tools_config": {
                        "llm_agent": {
                            "agent_type": "simple_llm_agent",
                            "agent_flow_type": "streaming",
                            "llm_config": {
                                "model": "gpt-3.5-turbo",
                                "temperature": 0.7
                            }
                        }
                    },
                    "toolchain": {
                        "execution": "sequential",
                        "pipelines": [["llm_agent"]]
                    },
                    "task_type": "conversation"
                }
            ]
        },
        "agent_prompts": {
            "system_prompt": "You are a helpful assistant."
        }
    }
    
    create_response = requests.post(f"{BASE_URL}/agent", json=agent_data, headers=headers)
    
    if create_response.status_code == 200:
        agent_id = create_response.json()["agent_id"]
        print(f"✅ Agent created successfully: {agent_id}")
        
        # 3. Get the agent
        get_response = requests.get(f"{BASE_URL}/agent/{agent_id}", headers=headers)
        if get_response.status_code == 200:
            print("✅ Agent retrieved successfully")
        else:
            print(f"❌ Failed to get agent: {get_response.text}")
        
        # 4. List all agents
        list_response = requests.get(f"{BASE_URL}/agent", headers=headers)
        if list_response.status_code == 200:
            agents = list_response.json()["agents"]
            print(f"✅ Listed {len(agents)} agents")
        else:
            print(f"❌ Failed to list agents: {list_response.text}")
        
        # 5. Update the agent
        agent_data["agent_config"]["agent_name"] = "Updated MySQL Agent"
        update_response = requests.put(f"{BASE_URL}/agent/{agent_id}", json=agent_data, headers=headers)
        if update_response.status_code == 200:
            print("✅ Agent updated successfully")
        else:
            print(f"❌ Failed to update agent: {update_response.text}")
        
        # 6. Delete the agent
        delete_response = requests.delete(f"{BASE_URL}/agent/{agent_id}", headers=headers)
        if delete_response.status_code == 200:
            print("✅ Agent deleted successfully")
        else:
            print(f"❌ Failed to delete agent: {delete_response.text}")
            
    else:
        print(f"❌ Failed to create agent: {create_response.text}")


if __name__ == "__main__":
    test_agent_management()