import click
import requests
import json
from models import Server
import os
from dotenv import load_dotenv

load_dotenv()
API_BASE = os.getenv('API_BASE', 'http://localhost:5000')  # Default to localhost
TOKEN = os.getenv('KP_MCP_TOKEN')

def get_headers():
    """Get common headers for API requests"""
    if not TOKEN:
        click.echo("❌ Error: KP_MCP_TOKEN environment variable not set")
        click.echo("Please set your JWT token: export KP_MCP_TOKEN='your-token'")
        exit(1)
    return {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }

def handle_api_response(response, success_message):
    """Handle API response and display appropriate message"""
    if response.status_code in [200, 201]:
        click.echo(f"✅ {success_message}")
        if response.json():
            click.echo(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        click.echo(f"❌ Error {response.status_code}: {response.text}")

@click.group()
def cli():
    """KP MCP Registry CLI - Manage Model Context Protocol servers"""
    pass

@cli.command()
@click.option('--file', required=True, help='Path to server.json')
@click.option('--namespace', required=True, help='Namespace prefix, e.g., kp.internal.example')
def publish(file, namespace):
    """Publish a new MCP server to the registry"""
    # Validate file exists and parse JSON
    try:
        with open(file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        click.echo(f"❌ Error: File '{file}' not found")
        return
    except json.JSONDecodeError as e:
        click.echo(f"❌ Error: Invalid JSON in '{file}': {e}")
        return
    except Exception as e:
        click.echo(f"❌ Error reading file: {e}")
        return
    
    # Local validation
    try:
        server_id = f"{namespace}/{data['name'].lower().replace(' ', '-')}"
        server = Server(id=server_id, metadata=data, **data)
        click.echo(f"📝 Validating server: {server_id}")
    except ValueError as e:
        click.echo(f"❌ Validation error: {e}")
        return
    except KeyError as e:
        click.echo(f"❌ Missing required field in server.json: {e}")
        return
    
    # POST to API
    headers = get_headers()
    try:
        response = requests.post(f'{API_BASE}/v0/servers', json=server.model_dump(), headers=headers)
        handle_api_response(response, "Server published successfully!")
    except requests.ConnectionError:
        click.echo(f"❌ Error: Could not connect to API at {API_BASE}")
    except Exception as e:
        click.echo(f"❌ Error: {e}")

@cli.command()
@click.option('--query', '-q', help='Search query')
@click.option('--tools', help='Filter by tool names (comma-separated)')
@click.option('--limit', default=20, help='Number of results (default: 20)')
@click.option('--offset', default=0, help='Offset for pagination (default: 0)')
def list(query, tools, limit, offset):
    """List servers from the registry"""
    params = {
        'limit': limit,
        'offset': offset
    }
    if query:
        params['q'] = query
    if tools:
        params['tools'] = tools
    
    try:
        response = requests.get(f'{API_BASE}/v0/servers', params=params)
        if response.status_code == 200:
            data = response.json()
            click.echo(f"📋 Found {data['total']} servers (showing {len(data['servers'])})")
            click.echo("─" * 80)
            
            for server in data['servers']:
                click.echo(f"🔧 {server['name']} ({server['id']})")
                click.echo(f"   📝 {server['description']}")
                click.echo(f"   🔗 {server['endpoint']}")
                click.echo(f"   👤 {server['owner']} | 🏢 {server['team']}")
                if server.get('tools'):
                    tools_names = [tool['name'] for tool in server['tools']]
                    click.echo(f"   🛠️  Tools: {', '.join(tools_names)}")
                click.echo()
        else:
            click.echo(f"❌ Error {response.status_code}: {response.text}")
    except requests.ConnectionError:
        click.echo(f"❌ Error: Could not connect to API at {API_BASE}")
    except Exception as e:
        click.echo(f"❌ Error: {e}")

@cli.command()
@click.argument('server_id')
def get(server_id):
    """Get detailed information about a specific server"""
    try:
        response = requests.get(f'{API_BASE}/v0/servers/{server_id}')
        if response.status_code == 200:
            server = response.json()
            click.echo(f"🔧 Server Details: {server['name']}")
            click.echo("─" * 80)
            click.echo(json.dumps(server, indent=2, default=str))
        else:
            click.echo(f"❌ Error {response.status_code}: {response.text}")
    except requests.ConnectionError:
        click.echo(f"❌ Error: Could not connect to API at {API_BASE}")
    except Exception as e:
        click.echo(f"❌ Error: {e}")

@cli.command()
@click.argument('server_id')
@click.option('--file', help='Path to updated server.json (optional)')
@click.option('--name', help='Update server name')
@click.option('--description', help='Update server description')
@click.option('--version', help='Update server version')
@click.option('--endpoint', help='Update server endpoint')
def update(server_id, file, name, description, version, endpoint):
    """Update an existing server"""
    update_data = {}
    
    # Load data from file if provided
    if file:
        try:
            with open(file, 'r') as f:
                update_data = json.load(f)
        except FileNotFoundError:
            click.echo(f"❌ Error: File '{file}' not found")
            return
        except json.JSONDecodeError as e:
            click.echo(f"❌ Error: Invalid JSON in '{file}': {e}")
            return
    
    # Override with command line options
    if name:
        update_data['name'] = name
    if description:
        update_data['description'] = description
    if version:
        update_data['version'] = version
    if endpoint:
        update_data['endpoint'] = endpoint
    
    if not update_data:
        click.echo("❌ Error: No update data provided. Use --file or specify fields to update.")
        return
    
    headers = get_headers()
    try:
        response = requests.put(f'{API_BASE}/v0/servers/{server_id}', json=update_data, headers=headers)
        handle_api_response(response, f"Server '{server_id}' updated successfully!")
    except requests.ConnectionError:
        click.echo(f"❌ Error: Could not connect to API at {API_BASE}")
    except Exception as e:
        click.echo(f"❌ Error: {e}")

@cli.command()
@click.argument('server_id')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
def delete(server_id, confirm):
    """Delete a server from the registry"""
    if not confirm:
        if not click.confirm(f"⚠️  Are you sure you want to delete server '{server_id}'?"):
            click.echo("❌ Deletion cancelled")
            return
    
    headers = get_headers()
    try:
        response = requests.delete(f'{API_BASE}/v0/servers/{server_id}', headers=headers)
        handle_api_response(response, f"Server '{server_id}' deleted successfully!")
    except requests.ConnectionError:
        click.echo(f"❌ Error: Could not connect to API at {API_BASE}")
    except Exception as e:
        click.echo(f"❌ Error: {e}")

@cli.command()
def health():
    """Check API health status"""
    try:
        response = requests.get(f'{API_BASE}/v0/health')
        if response.status_code == 200:
            click.echo("✅ API is healthy!")
            click.echo(f"Response: {response.json()}")
        else:
            click.echo(f"❌ API health check failed: {response.status_code}")
    except requests.ConnectionError:
        click.echo(f"❌ Error: Could not connect to API at {API_BASE}")
    except Exception as e:
        click.echo(f"❌ Error: {e}")

@cli.command()
def config():
    """Show current configuration"""
    click.echo("🔧 Current Configuration:")
    click.echo(f"API Base URL: {API_BASE}")
    click.echo(f"Token Set: {'✅ Yes' if TOKEN else '❌ No'}")
    if TOKEN:
        # Show first and last 4 chars of token for verification
        masked_token = f"{TOKEN[:8]}...{TOKEN[-8:]}" if len(TOKEN) > 16 else "***"
        click.echo(f"Token Preview: {masked_token}")

if __name__ == '__main__':
    cli()