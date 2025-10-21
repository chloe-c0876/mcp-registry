#!/usr/bin/env python3
"""
Test script for mock authentication
This demonstrates how to get and use tokens in development mode
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_mock_auth():
    """Test the mock authentication system"""
    API_BASE = "http://localhost:5000"
    
    print("🧪 Testing Mock Authentication System")
    print("=" * 50)
    
    # 1. Check health endpoint
    print("\n1. 📋 Checking API health...")
    try:
        response = requests.get(f"{API_BASE}/v0/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ API is healthy")
            print(f"   🔧 Dev mode: {health_data.get('dev_mode')}")
            print(f"   👤 Mock user: {health_data.get('mock_user')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
    except requests.ConnectionError:
        print(f"   ❌ Cannot connect to {API_BASE}")
        print("   💡 Make sure to run: uv run python app.py")
        return
    
    # 2. Get mock token
    print("\n2. 🎫 Getting mock token...")
    try:
        response = requests.get(f"{API_BASE}/dev/token")
        if response.status_code == 200:
            token_data = response.json()
            token = token_data['access_token']
            print(f"   ✅ Mock token generated")
            print(f"   👤 User: {token_data['user_email']}")
            print(f"   ⏰ Expires in: {token_data['expires_in']} seconds")
            print(f"   💡 Usage: {token_data['usage']}")
        else:
            print(f"   ❌ Token generation failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error getting token: {e}")
        return
    
    # 3. Test authenticated endpoint
    print("\n3. 🔐 Testing authenticated endpoint...")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Try to create a test server
    test_server = {
        "id": "kp.internal.test/mock-server",
        "name": "Mock Test Server",
        "description": "A test server for mock authentication",
        "version": "1.0.0",
        "endpoint": "https://mock-test.kp.com",
        "tools": [
            {"name": "test_tool", "description": "A test tool"}
        ],
        "auth_methods": ["bearer"],
        "team": "Test Team",
        "metadata": {
            "name": "Mock Test Server",
            "endpoint": "https://mock-test.kp.com",
            "tools": [{"name": "test_tool"}],
            "auth_methods": ["bearer"]
        }
    }
    
    try:
        response = requests.post(f"{API_BASE}/v0/servers", json=test_server, headers=headers)
        if response.status_code == 201:
            result = response.json()
            print(f"   ✅ Server published successfully!")
            print(f"   🆔 Server ID: {result['id']}")
        else:
            print(f"   ❌ Server publication failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error publishing server: {e}")
    
    # 4. List servers to verify
    print("\n4. 📋 Listing servers...")
    try:
        response = requests.get(f"{API_BASE}/v0/servers")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {data['total']} servers")
            for server in data['servers'][:3]:  # Show first 3
                print(f"   🔧 {server['name']} ({server['id']})")
        else:
            print(f"   ❌ Failed to list servers: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error listing servers: {e}")
    
    print("\n🎉 Mock authentication test completed!")
    print(f"\n💡 To use with CLI, run:")
    print(f"   export KP_MCP_TOKEN=\"{token}\"")
    print(f"   uv run python cli.py list")

if __name__ == "__main__":
    test_mock_auth()