/**
 * Runtime Configuration Loader
 * Fetches configuration from backend API instead of build-time environment variables
 * This allows dynamic configuration changes without rebuilding the frontend
 */

export interface RuntimeConfig {
  cognitoDomain: string;
  cognitoClientId: string;
  cognitoUserPoolId: string;
  cognitoRegion: string;
  cognitoRedirectUri: string;
  cognitoScopes: string;
  apiBaseUrl: string;
  agentcoreUrl: string;
  mcpUrl: string;
  environment: string;
}

let cachedConfig: RuntimeConfig | null = null;
let configPromise: Promise<RuntimeConfig> | null = null;

/**
 * Load runtime configuration from backend API
 * Uses caching to avoid multiple requests
 */
export async function loadRuntimeConfig(): Promise<RuntimeConfig> {
  // Return cached config if available
  if (cachedConfig) {
    return cachedConfig;
  }

  // Return existing promise if already loading
  if (configPromise) {
    return configPromise;
  }

  // Start loading config
  configPromise = (async () => {
    try {
      // Determine API base URL
      // In production, use relative path (served from same origin)
      // In development, use environment variable or fallback
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '';
      const configUrl = apiBaseUrl
        ? `${apiBaseUrl}/config`
        : '/api/config'; // Relative URL for production

      console.log('[Config] Fetching runtime config from:', configUrl);

      const response = await fetch(configUrl, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
        // Add timeout
        signal: AbortSignal.timeout(5000),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch config: ${response.status} ${response.statusText}`);
      }

      const config: RuntimeConfig = await response.json();

      // Validate required fields
      const requiredFields: (keyof RuntimeConfig)[] = [
        'cognitoDomain',
        'cognitoClientId',
        'cognitoUserPoolId',
        'cognitoRegion'
      ];

      for (const field of requiredFields) {
        if (!config[field]) {
          throw new Error(`Missing required config field: ${field}`);
        }
      }

      // Cache the config
      cachedConfig = config;
      console.log('[Config] Runtime config loaded successfully');

      return config;
    } catch (error) {
      console.error('[Config] Failed to load runtime config:', error);

      // Fallback to build-time environment variables if API fails
      console.warn('[Config] Using fallback build-time configuration');

      // Updated to CORRECT production values (Dec 2024)
      const fallbackConfig: RuntimeConfig = {
        cognitoDomain: import.meta.env.VITE_COGNITO_DOMAIN || 'https://aap-uat-1760338726.auth.ap-southeast-2.amazoncognito.com',
        cognitoClientId: import.meta.env.VITE_COGNITO_CLIENT_ID || '1b2ki7u3vgu37jube7hafgmf7i',
        cognitoUserPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID || 'ap-southeast-2_hm6hpYOl4',
        cognitoRegion: import.meta.env.VITE_COGNITO_REGION || 'ap-southeast-2',
        cognitoRedirectUri: import.meta.env.VITE_COGNITO_REDIRECT_URI || `${window.location.origin}/callback`,
        cognitoScopes: 'openid email profile',
        apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '',
        agentcoreUrl: import.meta.env.VITE_AGENTCORE_URL || '',
        mcpUrl: import.meta.env.VITE_MCP_URL || '',
        environment: import.meta.env.VITE_ENVIRONMENT || 'production'
      };

      cachedConfig = fallbackConfig;
      return fallbackConfig;
    } finally {
      configPromise = null;
    }
  })();

  return configPromise;
}

/**
 * Clear cached configuration (useful for testing)
 */
export function clearConfigCache(): void {
  cachedConfig = null;
  configPromise = null;
}
