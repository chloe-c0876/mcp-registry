import * as vscode from 'vscode';

export interface McpServerData {
	id: string;
	name: string;
	description: string;
	version: string;
	endpoint: string;
	owner: string;
	team: string;
	tools: Array<{ name: string; description: string }>;
	auth_methods: string[];
	tags: string[];
	metadata: any;
}

export interface ServerListResponse {
	servers: McpServerData[];
	total: number;
	offset: number;
	limit: number;
}

export class McpApiClient {
	private baseUrl: string;

	constructor() {
		const config = vscode.workspace.getConfiguration('mcpRegistry');
		this.baseUrl = config.get('apiBaseUrl', 'http://localhost:5000');
	}

	async getServers(query?: string, limit: number = 50, token?: string): Promise<ServerListResponse> {
		const url = new URL(`${this.baseUrl}/v0/servers`);
		if (query) {
			url.searchParams.append('q', query);
		}
		url.searchParams.append('limit', limit.toString());

		const headers: Record<string, string> = {};
		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}

		const response = await fetch(url.toString(), {
			headers
		});
		if (!response.ok) {
			throw new Error(`Failed to fetch servers: ${response.statusText}`);
		}

		return await response.json() as ServerListResponse;
	}

	async getServerDetails(serverId: string, token?: string): Promise<McpServerData> {
		const headers: Record<string, string> = {};
		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}

		const response = await fetch(`${this.baseUrl}/v0/servers/${encodeURIComponent(serverId)}`, {
			headers
		});
		if (!response.ok) {
			throw new Error(`Failed to fetch server details: ${response.statusText}`);
		}

		return await response.json() as McpServerData;
	}

	async publishServer(serverConfig: any, namespace: string, token: string): Promise<void> {
		const serverId = `${namespace}/${serverConfig.name.toLowerCase().replace(/\s+/g, '-')}`;
		const payload = {
			...serverConfig,
			id: serverId
		};

		const response = await fetch(`${this.baseUrl}/v0/servers`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${token}`
			},
			body: JSON.stringify(payload)
		});

		if (!response.ok) {
			const errorText = await response.text();
			throw new Error(`Failed to publish server: ${response.statusText} - ${errorText}`);
		}
	}

	async updateServer(serverId: string, updates: any, token: string): Promise<void> {
		const response = await fetch(`${this.baseUrl}/v0/servers/${encodeURIComponent(serverId)}`, {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${token}`
			},
			body: JSON.stringify(updates)
		});

		if (!response.ok) {
			const errorText = await response.text();
			throw new Error(`Failed to update server: ${response.statusText} - ${errorText}`);
		}
	}

	async deleteServer(serverId: string, token: string): Promise<void> {
		const response = await fetch(`${this.baseUrl}/v0/servers/${encodeURIComponent(serverId)}`, {
			method: 'DELETE',
			headers: {
				'Authorization': `Bearer ${token}`
			}
		});

		if (!response.ok) {
			const errorText = await response.text();
			throw new Error(`Failed to delete server: ${response.statusText} - ${errorText}`);
		}
	}

	async getAuthToken(): Promise<string> {
		const response = await fetch(`${this.baseUrl}/dev/token`);
		if (!response.ok) {
			throw new Error(`Failed to get auth token: ${response.statusText}`);
		}

		const data = await response.json() as { access_token: string };
		return data.access_token;
	}

	async checkApiHealth(): Promise<boolean> {
		try {
			const response = await fetch(`${this.baseUrl}/v0/health`);
			return response.ok;
		} catch {
			return false;
		}
	}
}