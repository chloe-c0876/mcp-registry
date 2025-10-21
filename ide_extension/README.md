# MCP Registry VS Code Extension

A Visual Studio Code extension for managing Model Context Protocol (MCP) servers through the KP MCP Registry API. This extension provides a seamless way to register, discover, and manage MCP servers directly from your VS Code environment.

## Features

### 🌐 Server Management
- **Browse MCP Servers**: View all registered MCP servers in a tree view
- **Server Details**: Inspect server capabilities, tools, and metadata
- **Search & Filter**: Find servers by name, description, or tools

### 📤 Publishing & Registration  
- **Publish Servers**: Register your MCP servers to the registry
- **Create Configurations**: Generate server.json files with guided setup
- **Update Servers**: Modify existing server registrations
- **Delete Servers**: Remove servers from the registry

### 🔐 Authentication
- **Secure Access**: JWT-based authentication with the registry API
- **Development Mode**: Easy authentication for local development
- **Token Management**: Automatic token storage and refresh

### ⚙️ Configuration
- **API Endpoint**: Configure the registry API base URL
- **Auto-refresh**: Automatically update server lists
- **Workspace Integration**: Seamless integration with VS Code workspace

## Installation

### Prerequisites
- Visual Studio Code 1.105.0 or later
- KP MCP Registry API running (default: http://localhost:5000)

### From Source
1. Clone this repository
2. Open in VS Code
3. Run `npm install` to install dependencies
4. Press `F5` to launch the extension in a new Extension Development Host window

### Package Installation (Coming Soon)
The extension will be available in the VS Code Marketplace.

## Usage

### Getting Started

1. **Start the MCP Registry API**
   ```bash
   # In your KP MCP Registry project
   cd kpmcpg
   uv run python app.py
   ```

2. **Open VS Code** with the extension installed

3. **Authenticate** with the registry:
   - Open Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
   - Run `MCP: Authenticate with Registry`
   - The extension will automatically get a development token

4. **View MCP Servers**:
   - Open the Explorer panel
   - Find the "MCP Servers" section
   - Browse available servers

### Publishing a Server

#### Option 1: Create from Scratch
1. Run `MCP: Create Server Configuration` from Command Palette
2. Fill in the server details (name, description, endpoint, etc.)
3. Edit the generated `server.json` file as needed
4. Run `MCP: Publish Server to Registry` to publish

#### Option 2: Use Existing server.json
1. Ensure you have a `server.json` file in your workspace
2. Run `MCP: Publish Server to Registry`
3. Select the configuration file (if multiple exist)
4. Choose a namespace (e.g., `kp.internal.example`)
5. Confirm publication

### Server Configuration Format

Your `server.json` should follow this structure:

```json
{
  "name": "My MCP Server",
  "description": "Description of what the server does",
  "version": "1.0.0",
  "endpoint": "https://api.example.com/mcp",
  "tools": [
    {
      "name": "example_tool",
      "description": "What this tool does"
    }
  ],
  "auth_methods": ["bearer"],
  "team": "Your Team Name",
  "tags": ["category", "type"],
  "metadata": {
    "name": "My MCP Server",
    "endpoint": "https://api.example.com/mcp",
    "tools": [{"name": "example_tool"}],
    "auth_methods": ["bearer"]
  }
}
```

### Managing Servers

#### View Server Details
- Right-click on a server in the tree view
- Select "View Details" to see comprehensive information
- Details include tools, authentication methods, and metadata

#### Update a Server
- Right-click on your server in the tree view
- Select "Update Server"
- Modify your local `server.json` and republish

#### Delete a Server
- Right-click on your server in the tree view  
- Select "Delete Server"
- Confirm the deletion

### Tree View Actions

The MCP Servers tree view provides these actions:

- **🔄 Refresh**: Update the server list
- **☁️ Publish**: Publish a new server
- **🔑 Authenticate**: Get/refresh authentication token
- **ℹ️ View Details**: Inspect server details
- **✏️ Update**: Modify an existing server
- **🗑️ Delete**: Remove a server

## Configuration

The extension can be configured through VS Code settings:

```json
{
  "mcpRegistry.apiBaseUrl": "http://localhost:5000",
  "mcpRegistry.autoRefresh": true
}
```

### Settings

- **`mcpRegistry.apiBaseUrl`**: Base URL for the MCP Registry API (default: `http://localhost:5000`)
- **`mcpRegistry.autoRefresh`**: Automatically refresh server list when extension activates (default: `true`)

## Development

### Project Structure

```
src/
├── extension.ts          # Main extension entry point
├── mcpServerProvider.ts  # Tree view data provider
├── mcpApiClient.ts       # API client for registry communication
└── authManager.ts        # Authentication and token management
```

### Build & Test

```bash
# Install dependencies
npm install

# Compile the extension
npm run compile

# Watch for changes during development
npm run watch

# Run tests
npm test

# Package the extension
npm run package
```

### Launch Configuration

The extension includes VS Code launch configurations:

- **Run Extension**: Launch extension in development mode
- **Watch & Debug**: Automatically rebuild and debug
- **Test Extension**: Run extension tests

Press `F5` to start debugging the extension.

## API Integration

The extension integrates with the KP MCP Registry API:

### Endpoints Used
- `GET /v0/servers` - List servers
- `GET /v0/servers/{id}` - Get server details  
- `POST /v0/servers` - Publish server
- `PUT /v0/servers/{id}` - Update server
- `DELETE /v0/servers/{id}` - Delete server
- `GET /v0/health` - API health check
- `GET /dev/token` - Get development token

### Authentication
- Uses JWT tokens for authentication
- Tokens stored securely in VS Code secrets storage
- Development mode supports automatic token retrieval

## Troubleshooting

### Common Issues

**Cannot connect to API**
- Ensure the MCP Registry API is running
- Check the configured API base URL in settings
- Verify the API is accessible at the configured endpoint

**Authentication failed**
- Try running `MCP: Authenticate with Registry` again
- Check if the API is in development mode
- Verify the `/dev/token` endpoint is available

**Server not found**
- Refresh the server list with the refresh button
- Check if the server was published successfully
- Verify you have the correct permissions

**Publishing failed**
- Ensure you're authenticated
- Check your `server.json` format matches the required schema
- Verify the namespace follows the naming convention (kp.internal.*, kp.public.*, kp.experimental.*)

### Debug Mode

Enable debug logging by:
1. Open VS Code Developer Tools (`Help > Toggle Developer Tools`)
2. Check the Console tab for extension logs
3. Look for messages prefixed with "MCP Registry"

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions:
- Create an issue in the repository
- Check the troubleshooting section above
- Review the API documentation
