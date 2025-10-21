from flask import Flask, request, jsonify, abort
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
import pymongo
from dotenv import load_dotenv
from models import Server, Tool
from msal import ConfidentialClientApplication
import os
from datetime import timedelta, datetime, timezone
from typing import Optional


load_dotenv(os.path.join(os.getcwd(), "kpmcpg", ".env"))

# Development mode configuration
DEV_MODE = os.getenv('DEV_MODE', 'false').lower() == 'true'
MOCK_USER_EMAIL = os.getenv('MOCK_USER_EMAIL', 'dev@kp.com')

app = Flask(__name__)
if DEV_MODE:
    app.config['JWT_SECRET_KEY'] = os.getenv('MOCK_JWT_SECRET', 'dev-secret')
    print("🔧 Running in DEVELOPMENT MODE with mock authentication")
else:
    app.config['JWT_SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
    print("🔐 Running in PRODUCTION MODE with Azure AD")

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

# MongoDB
client = pymongo.MongoClient(os.getenv('MONGO_URI'))
db = client['Agentic']  # Match the database name used in seed.py
servers_collection = db['servers']
audits_collection = db['audits']

# Global flag to track text search support
TEXT_SEARCH_SUPPORTED = None

# Azure AD Config (only in production mode)
if not DEV_MODE:
    AUTHORITY = os.getenv('AZURE_AUTHORITY')
    CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
    CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')
    try:
        app_instance = ConfidentialClientApplication(
            CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
        )
        print("✅ Azure AD client initialized")
    except Exception as e:
        print(f"⚠️  Warning: Azure AD initialization failed: {e}")
        app_instance = None
else:
    app_instance = None
    print("🔧 Skipping Azure AD initialization in development mode")

# Helper: Validate Azure AD token and get user
def validate_token(token: str) -> str:
    if DEV_MODE:
        # Mock validation - always return mock user
        return MOCK_USER_EMAIL
    
    if not app_instance:
        abort(401, "Authentication not configured")
        
    try:
        result = app_instance.acquire_token_silent(scopes=['User.Read'], account=None)
        if not result:
            abort(401, "Invalid token")
        # In prod, decode token to get email/group
        user_email = "user@example.com"  # Placeholder; use jwt.decode(token) for real
        return user_email
    except Exception as e:
        abort(401, f"Token validation failed: {str(e)}")

# Helper: Audit log
def log_audit(action: str, user_id: str, server_id: Optional[str] = None, details: dict = None):
    audits_collection.insert_one({
        "action": action, "user_id": user_id, "server_id": server_id,
        "timestamp": datetime.now(timezone.utc), "details": details or {}
    })

@app.route('/v0/servers', methods=['GET'])
def list_servers():
    global TEXT_SEARCH_SUPPORTED
    
    query = request.args.get('q', '')
    tools_filter = request.args.get('tools', '')
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    
    mongo_query = {}
    
    # Check if text search is supported (cache the result)
    if TEXT_SEARCH_SUPPORTED is None:
        try:
            # Test if text search is supported
            servers_collection.count_documents({'$text': {'$search': 'test'}})
            TEXT_SEARCH_SUPPORTED = True
            print("ℹ️  Text search is supported")
        except Exception as e:
            TEXT_SEARCH_SUPPORTED = False
            print(f"ℹ️  Text search not supported, using regex fallback: {e}")
    
    # Handle text search based on support
    if query:
        if TEXT_SEARCH_SUPPORTED:
            # Use MongoDB text search (case-insensitive by default)
            mongo_query['$text'] = {'$search': query}
        else:
            # Use case-insensitive regex fallback for "contains" search
            import re
            escaped_query = re.escape(query)  # Escape special regex characters
            mongo_query['$or'] = [
                {'name': {'$regex': escaped_query, '$options': 'i'}},
                {'description': {'$regex': escaped_query, '$options': 'i'}},
                {'tags': {'$regex': escaped_query, '$options': 'i'}}
            ]
            print(f"🔍 Using regex search for: '{query}' -> '{escaped_query}'")
    
    # Tool filtering
    if tools_filter:
        mongo_query['tools.name'] = {'$in': tools_filter.split(',')}
    
    print(f"🔍 Final query: {mongo_query}")  # Debug: show final query
    
    # Execute query (should work with either text search or regex)
    total = servers_collection.count_documents(mongo_query)
    servers = list(servers_collection.find(mongo_query).skip(offset).limit(limit))
    
    # Remove MongoDB ObjectId from results
    for server in servers:
        server.pop('_id', None)
    
    return jsonify({
        "servers": servers,
        "total": total,
        "offset": offset,
        "limit": limit
    })

@app.route('/v0/servers/<server_id>', methods=['GET'])
def get_server(server_id):
    server = servers_collection.find_one({'id': server_id})
    if not server:
        abort(404)
    # Remove MongoDB ObjectId from result
    server.pop('_id', None)
    return jsonify(server)

@app.route('/v0/servers/<server_id>/tools', methods=['GET'])
def get_server_tools(server_id):
    """Get only the tools for a specific server"""
    server = servers_collection.find_one({'id': server_id}, {'tools': 1, 'name': 1, '_id': 0})
    if not server:
        abort(404)
    return jsonify({
        'server_id': server_id,
        'server_name': server.get('name', ''),
        'tools': server.get('tools', [])
    })

@app.route('/v0/servers', methods=['POST'])
@jwt_required()
def publish_server():
    user_email = get_jwt_identity()  # From token
    data = request.get_json()
    try:
        # Create a copy of data to avoid modifying the original
        server_data = data.copy()
        # Set owner in the data dictionary
        server_data['owner'] = user_email
        # Create Server object without duplicate id parameter
        server = Server(**server_data)  # Validates schema
    except ValueError as e:
        abort(400, str(e))
    
    # Ownership check: e.g., namespace matches team domain (simplified)
    if DEV_MODE:
        # Relaxed validation for development
        if not server.id.startswith(('kp.internal.', 'kp.public.', 'kp.experimental.')):
            abort(403, "Invalid namespace. Must start with kp.internal., kp.public., or kp.experimental.")
    else:
        # Strict validation for production
        if not server.id.startswith('kp.internal.') or server.owner != user_email:
            abort(403, "Ownership mismatch")
    
    server_dict = server.model_dump()
    servers_collection.replace_one({'id': server.id}, server_dict, upsert=True)
    log_audit('publish', user_email, server.id)
    return jsonify({'id': server.id, 'message': 'Published'}), 201

@app.route('/v0/servers/<server_id>', methods=['PUT'])
@jwt_required()
def update_server(server_id):
    user_email = get_jwt_identity()
    data = request.get_json()
    existing = servers_collection.find_one({'id': server_id})
    if not existing or existing['owner'] != user_email:
        abort(403)
    
    # Partial update
    update_data = {k: v for k, v in data.items() if k != 'owner' and k != 'id'}
    update_data['updated_at'] = datetime.now(timezone.utc)
    servers_collection.update_one({'id': server_id}, {'$set': update_data})
    log_audit('update', user_email, server_id)
    return jsonify({'message': 'Updated'})

@app.route('/v0/servers/<server_id>', methods=['DELETE'])
@jwt_required()
def delete_server(server_id):
    user_email = get_jwt_identity()
    existing = servers_collection.find_one({'id': server_id})
    if not existing or existing['owner'] != user_email:
        abort(403)
    servers_collection.delete_one({'id': server_id})
    log_audit('delete', user_email, server_id)
    return jsonify({'message': 'Deleted'})

@app.route('/auth/token', methods=['POST'])
def get_token():
    """Get JWT token for authentication"""
    if DEV_MODE:
        # Mock token generation for development
        token = create_access_token(identity=MOCK_USER_EMAIL)
        return jsonify({
            'access_token': token,
            'user_email': MOCK_USER_EMAIL,
            'dev_mode': True,
            'message': 'Mock token generated for development'
        })
    else:
        # Production OAuth flow
        data = request.get_json() or {}
        code = data.get('code')
        if not code:
            abort(400, "Authorization code required")
        
        # ... MSAL acquire_token_by_code ...
        # For now, return placeholder
        token = create_access_token(identity='user@example.com')
        return jsonify({
            'access_token': token,
            'dev_mode': False,
            'message': 'Production token (placeholder implementation)'
        })

@app.route('/v0/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'dev_mode': DEV_MODE,
        'mock_user': MOCK_USER_EMAIL if DEV_MODE else None
    })

@app.route('/dev/token', methods=['GET'])
def dev_get_token():
    """Development helper: Get a mock token without authentication"""
    if not DEV_MODE:
        abort(404, "Development endpoints not available in production mode")
    
    token = create_access_token(identity=MOCK_USER_EMAIL)
    return jsonify({
        'access_token': token,
        'user_email': MOCK_USER_EMAIL,
        'expires_in': 3600,
        'usage': 'Set as KP_MCP_TOKEN environment variable',
        'example': f'export KP_MCP_TOKEN="{token[:20]}..."'
    })

if __name__ == '__main__':
    # Create text index (optional - may not work with Cosmos DB)
    # Only attempt if we haven't tried before in this session
    if not hasattr(app, '_indexes_checked'):
        # Initialize text search support check
        if TEXT_SEARCH_SUPPORTED is None:
            try:
                # Test if text search is supported before creating indexes
                servers_collection.count_documents({'$text': {'$search': 'test'}})
                TEXT_SEARCH_SUPPORTED = True
            except Exception as e:
                TEXT_SEARCH_SUPPORTED = False
                if "'text' is not supported" in str(e) or "CommandNotSupported" in str(e):
                    print("ℹ️  Text search not supported by database, using regex fallback")
                else:
                    print(f"⚠️  Warning: Could not test text search: {e}")
                print("🔧 Search will use case-insensitive regex matching instead")
        
        # Create indexes only if text search is supported
        if TEXT_SEARCH_SUPPORTED:
            try:
                existing_indexes = list(servers_collection.list_indexes())
                text_index_exists = any('text' in str(idx) for idx in existing_indexes)
                
                if not text_index_exists:
                    servers_collection.create_index([
                        ("name", "text"), 
                        ("description", "text"), 
                        ("tools.name", "text"),
                        ("tags", "text")
                    ])
                    print("✅ Created text search indexes")
                else:
                    print("ℹ️  Text search indexes already exist")
            except Exception as e:
                print(f"⚠️  Warning: Could not create text indexes: {e}")
        
        app._indexes_checked = True
    
    # Check if running under debugger to avoid reloader conflicts
    import sys
    in_debugger = hasattr(sys, 'gettrace') and sys.gettrace() is not None
    
    if in_debugger:
        # Running under debugger - disable reloader to avoid "No module named app" error
        app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
    else:
        # Normal execution - enable reloader for development convenience
        app.run(debug=True, host="0.0.0.0", port=5000)