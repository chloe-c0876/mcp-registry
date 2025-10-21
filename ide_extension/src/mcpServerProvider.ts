import * as vscode from 'vscode';
import { McpApiClient, McpServerData } from './mcpApiClient';
import { AuthenticationManager } from './authManager';

export class McpTool extends vscode.TreeItem {
	constructor(
		public readonly id: string,
		public readonly label: string,
		public readonly description: string
	) {
		super(label, vscode.TreeItemCollapsibleState.None);
		this.tooltip = `${this.label} - ${this.description}`;
		this.contextValue = 'mcpTool';
		this.iconPath = new vscode.ThemeIcon('tools');
	}
}

export class McpServer extends vscode.TreeItem {
	public readonly tools: McpTool[] = [];
	public readonly serverData: McpServerData;

	constructor(
		public readonly id: string,
		public readonly label: string,
		public readonly description: string,
		public readonly version: string,
		public readonly owner: string,
		serverData: McpServerData
	) {
		super(label, vscode.TreeItemCollapsibleState.Collapsed);
		this.tooltip = `${this.label} - ${this.description}`;
		this.contextValue = 'mcpServer';
		this.iconPath = new vscode.ThemeIcon('server');
		this.serverData = serverData;
		
		// Create tool items for this server
		if (serverData.tools && Array.isArray(serverData.tools)) {
			this.tools = serverData.tools.map((tool, index) => 
				new McpTool(
					`${this.id}-tool-${index}`,
					tool.name,
					tool.description || ''
				)
			);
		}
	}
}

// Define a type for tree items that can be either a server or a tool
type McpTreeItem = McpServer | McpTool;

export class McpServerProvider implements vscode.TreeDataProvider<McpTreeItem> {
	private _onDidChangeTreeData: vscode.EventEmitter<McpTreeItem | undefined | null | void> = new vscode.EventEmitter<McpTreeItem | undefined | null | void>();
	readonly onDidChangeTreeData: vscode.Event<McpTreeItem | undefined | null | void> = this._onDidChangeTreeData.event;

	private servers: McpServer[] = [];

	constructor(private apiClient: McpApiClient, private authManager: AuthenticationManager) {}

	refresh(): void {
		this.loadServers();
		this._onDidChangeTreeData.fire();
	}

	getTreeItem(element: McpTreeItem): vscode.TreeItem {
		return element;
	}

	getChildren(element?: McpTreeItem): Thenable<McpTreeItem[]> {
		if (!element) {
			// Return root level servers
			return Promise.resolve(this.servers);
		}
		
		// If the element is a server, return its tools
		if (element instanceof McpServer) {
			return Promise.resolve(element.tools);
		}
		
		// Tools don't have children
		return Promise.resolve([]);
	}

	private async loadServers(): Promise<void> {
		try {
			const token = await this.authManager.getToken();
			const authDisabled = await this.authManager.isAuthenticationDisabled();
			
			const serverData = await this.apiClient.getServers(undefined, 50, token);
			this.servers = serverData.servers.map((server: McpServerData) => 
				new McpServer(
					server.id,
					server.name,
					server.description,
					server.version,
					server.owner,
					server // Pass the full server data to the constructor
				)
			);
		} catch (error) {
			console.error('Failed to load MCP servers:', error);
			this.servers = [];
			
			const authDisabled = await this.authManager.isAuthenticationDisabled();
			if (authDisabled) {
				vscode.window.showErrorMessage('Failed to load MCP servers. Check your API connection.');
			} else {
				vscode.window.showErrorMessage('Failed to load MCP servers. Please authenticate first using "KP_MCP: Authenticate with Registry"');
			}
		}
	}
}