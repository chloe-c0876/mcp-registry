import * as vscode from 'vscode';
import { McpServerProvider, McpServer } from './mcpServerProvider';
import { McpApiClient } from './mcpApiClient';
import { AuthenticationManager } from './authManager';

let mcpServerProvider: McpServerProvider;
let apiClient: McpApiClient;
let authManager: AuthenticationManager;

export function activate(context: vscode.ExtensionContext) {
	console.log('MCP Registry extension is now active!');

	// Initialize services
	apiClient = new McpApiClient();
	authManager = new AuthenticationManager(context);
	mcpServerProvider = new McpServerProvider(apiClient, authManager);

	// Set context for view visibility
	vscode.commands.executeCommand('setContext', 'mcpRegistryEnabled', true);

	// Register tree data provider
	vscode.window.registerTreeDataProvider('mcpServerExplorer', mcpServerProvider);

	// Register commands
	const commands = [
		vscode.commands.registerCommand('mcpRegistry.refreshServers', () => {
			mcpServerProvider.refresh();
			vscode.window.showInformationMessage('MCP Server list refreshed');
		}),

		vscode.commands.registerCommand('mcpRegistry.authenticate', async () => {
			await authManager.authenticate();
		}),

		vscode.commands.registerCommand('mcpRegistry.disableAuth', async () => {
			await authManager.disableAuthentication();
			mcpServerProvider.refresh(); // Refresh to load servers without auth
		}),

		vscode.commands.registerCommand('mcpRegistry.enableAuth', async () => {
			await authManager.enableAuthentication();
		}),

		vscode.commands.registerCommand('mcpRegistry.publishServer', async () => {
			await publishServer();
		}),

		vscode.commands.registerCommand('mcpRegistry.createServerConfig', async () => {
			await createServerConfiguration();
		}),

		vscode.commands.registerCommand('mcpRegistry.viewServerDetails', async (server: McpServer) => {
			await showServerDetails(server);
		}),

		vscode.commands.registerCommand('mcpRegistry.updateServer', async (server: McpServer) => {
			await updateServer(server);
		}),

		vscode.commands.registerCommand('mcpRegistry.deleteServer', async (server: McpServer) => {
			await deleteServer(server);
		})
	];

	// Add all commands to context subscriptions
	commands.forEach(cmd => context.subscriptions.push(cmd));

	// Auto-refresh if enabled
	const config = vscode.workspace.getConfiguration('mcpRegistry');
	if (config.get('autoRefresh', true)) {
		mcpServerProvider.refresh();
	}
}

async function publishServer() {
	try {
		// Check authentication
		const token = await authManager.getToken();
		if (!token) {
			vscode.window.showErrorMessage('Please authenticate first');
			return;
		}

		// Get server.json file from workspace
		const serverConfigFiles = await vscode.workspace.findFiles('**/server.json', '**/node_modules/**');
		
		if (serverConfigFiles.length === 0) {
			const create = await vscode.window.showInformationMessage(
				'No server.json found. Create one?', 
				'Create Config', 
				'Cancel'
			);
			if (create === 'Create Config') {
				await createServerConfiguration();
			}
			return;
		}

		// If multiple configs, let user choose
		let configFile = serverConfigFiles[0];
		if (serverConfigFiles.length > 1) {
			const pick = await vscode.window.showQuickPick(
				serverConfigFiles.map(file => ({
					label: vscode.workspace.asRelativePath(file),
					file: file
				})),
				{ placeHolder: 'Select server configuration to publish' }
			);
			if (!pick) {
				return;
			}
			configFile = pick.file;
		}

		// Read and parse the config
		const configContent = await vscode.workspace.fs.readFile(configFile);
		const config = JSON.parse(configContent.toString());

		// Get namespace from user
		const namespace = await vscode.window.showInputBox({
			prompt: 'Enter namespace (e.g., kp.internal.example)',
			value: 'kp.internal.example',
			validateInput: (value) => {
				if (!value || !value.match(/^kp\.(internal|public|experimental)\./)) {
					return 'Namespace must start with kp.internal., kp.public., or kp.experimental.';
				}
				return null;
			}
		});

		if (!namespace) {
			return;
		}

		// Publish to registry
		await apiClient.publishServer(config, namespace, token);
		vscode.window.showInformationMessage('Server published successfully!');
		mcpServerProvider.refresh();

	} catch (error) {
		vscode.window.showErrorMessage(`Failed to publish server: ${error}`);
	}
}

async function createServerConfiguration() {
	const name = await vscode.window.showInputBox({
		prompt: 'Server Name',
		placeHolder: 'My MCP Server'
	});
	if (!name) {
		return;
	}

	const description = await vscode.window.showInputBox({
		prompt: 'Server Description',
		placeHolder: 'What does your server do?'
	});
	if (!description) {
		return;
	}

	const endpoint = await vscode.window.showInputBox({
		prompt: 'Server Endpoint URL',
		placeHolder: 'https://api.example.com/mcp'
	});
	if (!endpoint) {
		return;
	}

	const serverConfig = {
		name: name,
		description: description,
		version: "1.0.0",
		endpoint: endpoint,
		tools: [
			{
				name: "example_tool",
				description: "An example tool"
			}
		],
		auth_methods: ["bearer"],
		team: "Development Team",
		tags: ["example"],
		metadata: {
			name: name,
			endpoint: endpoint,
			tools: [{ name: "example_tool" }],
			auth_methods: ["bearer"]
		}
	};

	// Create server.json file
	const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
	if (!workspaceFolder) {
		vscode.window.showErrorMessage('No workspace folder open');
		return;
	}

	const serverJsonPath = vscode.Uri.joinPath(workspaceFolder.uri, 'server.json');
	await vscode.workspace.fs.writeFile(
		serverJsonPath, 
		Buffer.from(JSON.stringify(serverConfig, null, 2))
	);

	// Open the file
	const document = await vscode.workspace.openTextDocument(serverJsonPath);
	await vscode.window.showTextDocument(document);

	vscode.window.showInformationMessage('Server configuration created!');
}

async function showServerDetails(server: McpServer) {
	try {
		const token = await authManager.getToken();
		const details = await apiClient.getServerDetails(server.id, token);
		const panel = vscode.window.createWebviewPanel(
			'mcpServerDetails',
			`MCP Server: ${server.label}`,
			vscode.ViewColumn.One,
			{ enableScripts: false }
		);

		panel.webview.html = generateServerDetailsHtml(details);
	} catch (error) {
		const authDisabled = await authManager.isAuthenticationDisabled();
		if (authDisabled) {
			vscode.window.showErrorMessage(`Failed to load server details: ${error}`);
		} else {
			vscode.window.showErrorMessage(`Failed to load server details: ${error}. Try authenticating first.`);
		}
	}
}

async function updateServer(server: McpServer) {
	// Similar to publish but for updates
	vscode.window.showInformationMessage(`Update server ${server.label} - Feature coming soon!`);
}

async function deleteServer(server: McpServer) {
	const token = await authManager.getToken();
	if (!token) {
		vscode.window.showErrorMessage('Please authenticate first');
		return;
	}

	const confirm = await vscode.window.showWarningMessage(
		`Delete server "${server.label}"?`,
		{ modal: true },
		'Delete'
	);

	if (confirm === 'Delete') {
		try {
			await apiClient.deleteServer(server.id, token);
			vscode.window.showInformationMessage('Server deleted successfully');
			mcpServerProvider.refresh();
		} catch (error) {
			vscode.window.showErrorMessage(`Failed to delete server: ${error}`);
		}
	}
}

function generateServerDetailsHtml(server: any): string {
	return `
	<!DOCTYPE html>
	<html>
	<head>
		<title>MCP Server Details</title>
		<style>
			body { font-family: var(--vscode-font-family); padding: 20px; }
			.section { margin-bottom: 20px; }
			.tools { display: flex; flex-wrap: wrap; gap: 10px; }
			.tool { background: var(--vscode-button-background); padding: 8px; border-radius: 4px; }
			pre { background: var(--vscode-textBlockQuote-background); padding: 10px; border-radius: 4px; }
		</style>
	</head>
	<body>
		<h1>${server.name}</h1>
		<div class="section">
			<h3>Description</h3>
			<p>${server.description}</p>
		</div>
		<div class="section">
			<h3>Details</h3>
			<p><strong>ID:</strong> ${server.id}</p>
			<p><strong>Version:</strong> ${server.version}</p>
			<p><strong>Endpoint:</strong> ${server.endpoint}</p>
			<p><strong>Owner:</strong> ${server.owner}</p>
			<p><strong>Team:</strong> ${server.team}</p>
		</div>
		<div class="section">
			<h3>Tools</h3>
			<div class="tools">
				${server.tools.map((tool: any) => `<div class="tool">${tool.name}</div>`).join('')}
			</div>
		</div>
		<div class="section">
			<h3>Authentication Methods</h3>
			<p>${server.auth_methods.join(', ')}</p>
		</div>
		<div class="section">
			<h3>Tags</h3>
			<p>${server.tags.join(', ')}</p>
		</div>
	</body>
	</html>`;
}

export function deactivate() {
	console.log('MCP Registry extension deactivated');
}
