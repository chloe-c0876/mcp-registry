import requests
import pymongo
from models import Server, Tool
from dotenv import load_dotenv
import os
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

def seed_database():
    """Seed the database with sample MCP servers"""
    
    # MongoDB connection
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        print("❌ Error: MONGO_URI environment variable not set")
        return
    
    try:
        client = pymongo.MongoClient(mongo_uri)
        db = client['Agentic']
        servers_collection = db['servers']
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        return
    
    # Create sample servers for testing
    sample_servers = [
        {
            "id": "kp.internal.example/github-integration",
            "name": "GitHub Integration",
            "description": "Access GitHub repositories, issues, and pull requests",
            "version": "1.0.0",
            "endpoint": "https://github-mcp.kp.com",
            "tools": [
                {"name": "list_repos", "description": "List user repositories"},
                {"name": "get_issues", "description": "Get repository issues"},
                {"name": "create_pr", "description": "Create a pull request"}
            ],
            "auth_methods": ["bearer"],
            "owner": "platform@kp.com",
            "team": "Platform Team",
            "tags": ["git", "development", "api"],
            "metadata": {
                "name": "GitHub Integration",
                "endpoint": "https://github-mcp.kp.com",
                "tools": [{"name": "list_repos"}, {"name": "get_issues"}],
                "auth_methods": ["bearer"]
            },
            "is_public": False
        },
        {
            "id": "kp.internal.example/slack-bot",
            "name": "Slack Bot",
            "description": "Send messages and interact with Slack channels",
            "version": "1.2.0",
            "endpoint": "https://slack-mcp.kp.com",
            "tools": [
                {"name": "send_message", "description": "Send a message to a channel"},
                {"name": "list_channels", "description": "List available channels"},
                {"name": "get_users", "description": "Get workspace users"}
            ],
            "auth_methods": ["oauth2"],
            "owner": "communication@kp.com",
            "team": "Communication Team",
            "tags": ["messaging", "collaboration"],
            "metadata": {
                "name": "Slack Bot",
                "endpoint": "https://slack-mcp.kp.com",
                "tools": [{"name": "send_message"}, {"name": "list_channels"}],
                "auth_methods": ["oauth2"]
            },
            "is_public": True
        },
        {
            "id": "kp.internal.example/database-query",
            "name": "Database Query Tool",
            "description": "Execute safe database queries and retrieve data",
            "version": "2.1.0",
            "endpoint": "https://db-mcp.kp.com",
            "tools": [
                {"name": "execute_query", "description": "Execute a SELECT query"},
                {"name": "get_schema", "description": "Get table schema information"},
                {"name": "list_tables", "description": "List available tables"}
            ],
            "auth_methods": ["bearer"],
            "owner": "data@kp.com",
            "team": "Data Team",
            "tags": ["database", "analytics", "query"],
            "metadata": {
                "name": "Database Query Tool",
                "endpoint": "https://db-mcp.kp.com",
                "tools": [{"name": "execute_query"}, {"name": "get_schema"}],
                "auth_methods": ["bearer"]
            },
            "is_public": False
        }
    ]
    
    # Insert sample servers
    inserted_count = 0
    for server_data in sample_servers:
        try:
            # Validate using Pydantic model
            server = Server(**server_data)
            
            # Check if server already exists
            existing = servers_collection.find_one({'id': server.id})
            if existing:
                print(f"⚠️  Server {server.id} already exists, skipping")
                continue
            
            # Insert into database
            servers_collection.insert_one(server.model_dump())
            print(f"✅ Inserted server: {server.id}")
            inserted_count += 1
            
        except Exception as e:
            print(f"❌ Error inserting server {server_data.get('id', 'unknown')}: {e}")
    
    # Create text indexes for search functionality
    try:
        servers_collection.create_index([
            ("name", "text"), 
            ("description", "text"), 
            ("tools.name", "text"),
            ("tags", "text")
        ])
        print("✅ Created text search indexes")
    except Exception as e:
        print(f"⚠️  Warning: Could not create indexes: {e}")
    
    print(f"\n🎉 Seeding completed! Inserted {inserted_count} new servers")
    print(f"Total servers in database: {servers_collection.count_documents({})}")

if __name__ == "__main__":
    seed_database()