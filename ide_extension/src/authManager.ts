import * as vscode from 'vscode';
import { McpApiClient } from './mcpApiClient';

export class AuthenticationManager {
	private static readonly TOKEN_KEY = 'mcpRegistry.authToken';
	private static readonly AUTH_DISABLED_KEY = 'mcpRegistry.authDisabled';
	private apiClient: McpApiClient;

	constructor(private context: vscode.ExtensionContext) {
		this.apiClient = new McpApiClient();
	}

	async authenticate(): Promise<void> {
		try {
			// Check if API is reachable
			const isHealthy = await this.apiClient.checkApiHealth();
			if (!isHealthy) {
				vscode.window.showErrorMessage('Cannot connect to MCP Registry API. Please ensure it is running at the configured URL.');
				return;
			}

			// For development mode, get a token from the dev endpoint
			vscode.window.showInformationMessage('Authenticating with MCP Registry...');
			
			const token = await this.apiClient.getAuthToken();
			await this.storeToken(token);
			
			vscode.window.showInformationMessage('Successfully authenticated with MCP Registry!');
		} catch (error) {
			vscode.window.showErrorMessage(`Authentication failed: ${error}`);
		}
	}

	async disableAuthentication(): Promise<void> {
		await this.context.globalState.update(AuthenticationManager.AUTH_DISABLED_KEY, true);
		vscode.window.showInformationMessage('Authentication disabled for development. API calls will be made without tokens.');
	}

	async enableAuthentication(): Promise<void> {
		await this.context.globalState.update(AuthenticationManager.AUTH_DISABLED_KEY, false);
		vscode.window.showInformationMessage('Authentication enabled. Please authenticate to access the API.');
	}

	async isAuthenticationDisabled(): Promise<boolean> {
		return this.context.globalState.get(AuthenticationManager.AUTH_DISABLED_KEY, false);
	}

	async getToken(): Promise<string | undefined> {
		// If authentication is disabled, return undefined (no token needed)
		const authDisabled = await this.isAuthenticationDisabled();
		if (authDisabled) {
			return undefined;
		}
		return await this.context.secrets.get(AuthenticationManager.TOKEN_KEY);
	}

	async storeToken(token: string): Promise<void> {
		await this.context.secrets.store(AuthenticationManager.TOKEN_KEY, token);
	}

	async clearToken(): Promise<void> {
		await this.context.secrets.delete(AuthenticationManager.TOKEN_KEY);
	}

	async isAuthenticated(): Promise<boolean> {
		const token = await this.getToken();
		return !!token;
	}

	async logout(): Promise<void> {
		await this.clearToken();
		vscode.window.showInformationMessage('Logged out from MCP Registry');
	}
}