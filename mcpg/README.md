# KP MCP Registry

A comprehensive registry and management system for Model Context Protocol (MCP) servers, providing both REST API and CLI interfaces for publishing, discovering, and managing MCP servers within the KP ecosystem.

## 🏗️ Architecture

- **REST API** (`app.py`): Flask-based API with JWT authentication and MongoDB storage
- **CLI Tool** (`cli.py`): Command-line interface for easy server management
- **Data Models** (`models.py`): Pydantic models with schema validation
- **Database**: MongoDB (Azure Cosmos DB) for persistence
- **Authentication**: Azure AD integration with JWT tokens

## 🚀 Features

- ✅ **Server Registry**: Publish and discover MCP servers
- ✅ **Search & Filter**: Find servers by tools, descriptions, or queries
- ✅ **Authentication**: Azure AD integration with role-based access
- ✅ **Validation**: JSON schema validation for MCP compliance
- ✅ **Audit Logging**: Track all registry operations
- ✅ **CLI Management**: Professional command-line interface
- ✅ **Namespace Control**: Organized server hierarchies

## 📦 Installation

### Prerequisites

- Python 3.9+
- uv (Python package manager)
- Access to MongoDB/Azure Cosmos DB
- Azure AD application (for authentication)

### Setup

1. **Clone and install dependencies:**
   ```bash
   git clone <repository-url>
   cd kpmcpg
   uv sync
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

3. **Environment Variables:**
   ```env
   MONGO_URI=mongodb://your-cosmos-db-connection-string
   AZURE_CLIENT_ID=your-app-client-id
   AZURE_CLIENT_SECRET=your-app-secret
   AZURE_TENANT_ID=your-tenant-id
   AZURE_AUTHORITY=https://login.microsoftonline.com/your-tenant-id
   FLASK_SECRET_KEY=your-secret-key
   API_BASE=http://localhost:5000  # For CLI
   KP_MCP_TOKEN=your-jwt-token     # For CLI authentication
   ```

## 🖥️ API Usage

### Start the Server

```bash
uv run python app.py
```

The API will be available at `http://localhost:5000`

### API Endpoints

#### 🔍 **List Servers**
```bash
GET /v0/servers?q=search&tools=git,api&limit=20&offset=0
```

#### 📋 **Get Server Details**
```bash
GET /v0/servers/{server_id}
```

#### 📤 **Publish Server** (Requires JWT)
```bash
POST /v0/servers
Content-Type: application/json
Authorization: Bearer <jwt-token>

{
  "id": "kp.internal.example/github",
  "name": "GitHub Integration",
  "description": "Access GitHub repositories and issues",
  "version": "1.0.0",
  "endpoint": "https://api.example.com/github",
  "tools": [
    {"name": "list_repos", "description": "List user repositories"},
    {"name": "get_issues", "description": "Get repository issues"}
  ],
  "auth_methods": ["bearer"],
  "team": "Platform Team",
  "metadata": {
    "name": "GitHub Integration",
    "endpoint": "https://api.example.com/github"
  }
}
```

#### ✏️ **Update Server** (Requires JWT)
```bash
PUT /v0/servers/{server_id}
Authorization: Bearer <jwt-token>

{
  "version": "1.1.0",
  "description": "Updated description"
}
```

#### 🗑️ **Delete Server** (Requires JWT)
```bash
DELETE /v0/servers/{server_id}
Authorization: Bearer <jwt-token>
```

#### 🏥 **Health Check**
```bash
GET /v0/health
```

## 🖱️ CLI Usage

The CLI provides a user-friendly interface for all registry operations.

### Setup

```bash
# Set your JWT token
export KP_MCP_TOKEN="your-jwt-token"

# Optional: Set custom API endpoint
export API_BASE="https://your-api.com"
```

### Commands

#### 📋 **List Servers**
```bash
# List all servers
uv run python cli.py list

# Search servers
uv run python cli.py list --query "github"

# Filter by tools
uv run python cli.py list --tools "git,api"

# Pagination
uv run python cli.py list --limit 10 --offset 20

# Combined search
uv run python cli.py list --query "integration" --tools "api" --limit 5
```

#### 🔍 **Get Server Details**
```bash
uv run python cli.py get kp.internal.example/github
```

#### 📤 **Publish Server**
```bash
# Create server.json file first
uv run python cli.py publish --file server.json --namespace kp.internal.example
```

#### ✏️ **Update Server**
```bash
# Update from file
uv run python cli.py update kp.internal.example/github --file updated-server.json

# Update specific fields
uv run python cli.py update kp.internal.example/github \
  --name "New Name" \
  --version "2.0.0" \
  --description "Updated description"
```

#### 🗑️ **Delete Server**
```bash
# With confirmation prompt
uv run python cli.py delete kp.internal.example/github

# Skip confirmation
uv run python cli.py delete kp.internal.example/github --confirm
```

#### 🏥 **Health Check**
```bash
uv run python cli.py health
```

#### ⚙️ **Show Configuration**
```bash
uv run python cli.py config
```

#### 📚 **Help**
```bash
# General help
uv run python cli.py --help

# Command-specific help
uv run python cli.py list --help
uv run python cli.py publish --help
```

## 📄 Server JSON Format

Your `server.json` file should follow this structure:

```json
{
  "name": "GitHub Integration",
  "description": "Access GitHub repositories and issues",
  "version": "1.0.0",
  "endpoint": "https://api.example.com/github",
  "tools": [
    {
      "name": "list_repos",
      "description": "List user repositories"
    },
    {
      "name": "get_issues", 
      "description": "Get repository issues"
    }
  ],
  "auth_methods": ["bearer"],
  "team": "Platform Team"
}
```

## 🔧 Development

### Project Structure

```
kpmcpg/
├── app.py          # Flask REST API
├── cli.py          # Command-line interface
├── models.py       # Pydantic data models
├── .env            # Environment variables
├── pyproject.toml  # Project configuration
├── uv.lock         # Dependency lock file
└── README.md       # This file
```

### Running Tests

```bash
# Run the application
uv run python app.py

# Test CLI functionality
uv run python cli.py config
uv run python cli.py health
```

### Adding Dependencies

```bash
uv add package-name
```

## � Search & Discovery

The registry provides powerful search capabilities to help you find the right MCP servers:

### Search Features
- **Text Search**: Search across server names, descriptions, and tool names
- **Tool Filtering**: Find servers that provide specific tools
- **Tag Filtering**: Search by categorization tags
- **Pagination**: Handle large result sets efficiently

### CLI Search Examples

```bash
# Search by text in name/description
uv run python cli.py list --query "github"
uv run python cli.py list --query "integration"

# Filter by specific tools
uv run python cli.py list --tools "send_message,list_channels"
uv run python cli.py list --tools "execute_query"

# Pagination for large results
uv run python cli.py list --limit 5 --offset 10

# Complex search combining multiple criteria
uv run python cli.py list --query "database" --tools "execute_query" --limit 3
```

### API Search Examples

```bash
# Text search
GET /v0/servers?q=github&limit=10

# Tool filtering
GET /v0/servers?tools=send_message,list_channels

# Combined search
GET /v0/servers?q=integration&tools=api&limit=20&offset=0
```

### Search Limitations

**Note**: When using Azure Cosmos DB, full-text search indexes are not supported. Search functionality works through basic string matching rather than advanced text indexing. For production deployments requiring advanced search, consider:

- Using MongoDB Atlas (supports full-text indexes)
- Implementing external search (Elasticsearch, Azure Search)
- Using client-side filtering for small datasets

## �🛡️ Security

- **Authentication**: JWT tokens via Azure AD
- **Authorization**: Namespace-based ownership control
- **Validation**: Input validation with Pydantic models
- **Audit Logging**: All operations are logged
- **Environment Variables**: Sensitive data in `.env` file

## 🌐 Namespaces

Servers are organized using namespaces:

- `kp.internal.*` - Internal KP services
- `kp.public.*` - Public KP services  
- `kp.experimental.*` - Experimental/development servers

Example: `kp.internal.platform/github-integration`

## 📝 Examples

### Complete Workflow Example

1. **Create server definition:**
   ```json
   {
     "name": "Slack Bot",
     "description": "Send messages to Slack channels",
     "version": "1.0.0",
     "endpoint": "https://slack-bot.kp.com",
     "tools": [
       {"name": "send_message", "description": "Send a message to a channel"},
       {"name": "list_channels", "description": "List available channels"}
     ],
     "auth_methods": ["bearer"],
     "team": "Communication Team"
   }
   ```

2. **Publish to registry:**
   ```bash
   uv run python cli.py publish --file slack-bot.json --namespace kp.internal.communication
   ```

3. **Verify publication:**
   ```bash
   uv run python cli.py get kp.internal.communication/slack-bot
   ```

4. **Update version:**
   ```bash
   uv run python cli.py update kp.internal.communication/slack-bot --version "1.1.0"
   ```

5. **Search for it:**
   ```bash
   uv run python cli.py list --query "slack" --tools "send_message"
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

[Add your license here]

## 🆘 Support

For issues and questions:
- Create an issue in the repository
- Contact the Platform Team
- Check the API health: `uv run python cli.py health`