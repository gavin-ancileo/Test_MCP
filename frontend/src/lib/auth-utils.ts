import { loadRuntimeConfig } from '../config/runtime-config';

// Environment configuration (now loads from runtime API)
export const getAuthConfig = async () => {
  const config = await loadRuntimeConfig();
  return {
    cognitoDomain: config.cognitoDomain,
    clientId: config.cognitoClientId,
    userPoolId: config.cognitoUserPoolId,
    region: config.cognitoRegion,
    redirectUri: config.cognitoRedirectUri,
    scopes: config.cognitoScopes,
  };
};

// Generate PKCE challenge
export const generateCodeChallenge = async (codeVerifier: string): Promise<string> => {
  const encoder = new TextEncoder();
  const data = encoder.encode(codeVerifier);
  const digest = await crypto.subtle.digest('SHA-256', data);
  return btoa(String.fromCharCode(...new Uint8Array(digest)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
};

// Generate random string for code verifier
export const generateCodeVerifier = (): string => {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return btoa(String.fromCharCode(...array))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
};

// Generate state parameter
export const generateState = (): string => {
  const array = new Uint8Array(16);
  crypto.getRandomValues(array);
  return btoa(String.fromCharCode(...array))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
};

// Build Cognito authorization URL
export const buildAuthUrl = async (): Promise<string> => {
  const config = await getAuthConfig();
  const codeVerifier = generateCodeVerifier();
  const codeChallenge = await generateCodeChallenge(codeVerifier);
  const state = generateState();

  // Store PKCE parameters in sessionStorage
  sessionStorage.setItem('code_verifier', codeVerifier);
  sessionStorage.setItem('auth_state', state);

  const params = new URLSearchParams({
    response_type: 'code',
    client_id: config.clientId,
    redirect_uri: config.redirectUri,
    scope: config.scopes,
    code_challenge: codeChallenge,
    code_challenge_method: 'S256',
    state,
  });

  // Handle domain with or without https:// prefix
  const domainUrl = config.cognitoDomain.startsWith('https://') 
    ? config.cognitoDomain 
    : `https://${config.cognitoDomain}`;
  
  return `${domainUrl}/oauth2/authorize?${params.toString()}`;
};

// Exchange authorization code for tokens
export const exchangeCodeForToken = async (code: string, state: string): Promise<{ idToken: string; accessToken: string }> => {
  const config = await getAuthConfig();
  const codeVerifier = sessionStorage.getItem('code_verifier');
  const storedState = sessionStorage.getItem('auth_state');

  if (!codeVerifier || storedState !== state) {
    throw new Error('Invalid state or missing code verifier');
  }

  // Handle domain with or without https:// prefix
  const domainUrl = config.cognitoDomain.startsWith('https://') 
    ? config.cognitoDomain 
    : `https://${config.cognitoDomain}`;

  const response = await fetch(`${domainUrl}/oauth2/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      client_id: config.clientId,
      code,
      redirect_uri: config.redirectUri,
      code_verifier: codeVerifier,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(errorData.error_description || errorData.error || 'Token exchange failed');
  }

  const tokens = await response.json();
  
  // Clean up stored parameters
  sessionStorage.removeItem('code_verifier');
  sessionStorage.removeItem('auth_state');

  return {
    idToken: tokens.id_token,
    accessToken: tokens.access_token,
  };
};

// Decode JWT token (basic implementation)
export const decodeJWT = (token: string): any => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Failed to decode JWT:', error);
    return null;
  }
};

// Build Cognito logout URL
export const buildLogoutUrl = async (): Promise<string> => {
  const config = await getAuthConfig();
  const params = new URLSearchParams({
    client_id: config.clientId,
    logout_uri: window.location.origin, // Use logout_uri for Cognito logout endpoint
  });

  // Handle domain with or without https:// prefix
  const domainUrl = config.cognitoDomain.startsWith('https://')
    ? config.cognitoDomain
    : `https://${config.cognitoDomain}`;

  return `${domainUrl}/logout?${params.toString()}`;
};

// Backend API integration with health check
export const callBackendAPI = async (endpoint: string, options: RequestInit = {}, idToken?: string): Promise<any> => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL;

  if (!baseUrl) {
    throw new Error('Backend API URL not configured');
  }

  try {
    // If idToken not provided, try to get from localStorage
    const token = idToken || localStorage.getItem('id_token');

    const response = await fetch(`${baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers
      }
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Backend API error:', error);
    throw error;
  }
};

// Authenticated fetch wrapper - automatically adds Authorization and X-User-Email headers
// Version 2.0.1 - Deployment build identifier
const AUTH_UTILS_VERSION = '2.0.1';
export const authenticatedFetch = async (url: string, options: RequestInit = {}): Promise<Response> => {
  // Get ID token from localStorage
  const idToken = localStorage.getItem('id_token');

  // Extract email from JWT token for X-User-Email header
  let userEmail = '';
  if (idToken) {
    try {
      const payload = JSON.parse(atob(idToken.split('.')[1]));
      userEmail = payload.email || payload['cognito:username'] || '';
    } catch (e) {
      console.error('Failed to decode JWT for X-User-Email:', e);
    }
  }

  // Add Authorization and X-User-Email headers if token exists
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
    ...(idToken && { 'Authorization': `Bearer ${idToken}` }),
    ...(userEmail && { 'X-User-Email': userEmail }),
  };

  return fetch(url, {
    ...options,
    headers,
  });
};

// Health check function
export const checkBackendHealth = async (): Promise<{ healthy: boolean; error?: string }> => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_AGENTCORE_URL;
  
  if (!baseUrl) {
    return { 
      healthy: false, 
      error: 'No backend URL configured - running in demo mode' 
    };
  }

  try {
    const response = await fetch(`/agentcore/healthz`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      },
      // Add timeout to prevent hanging
      signal: AbortSignal.timeout(10000) // 10 second timeout
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      return {
        healthy: false,
        error: `Backend returned ${response.status}: ${errorText}`
      };
    }

    const data = await response.json().catch(() => ({ status: 'ok' }));
    console.log('✅ Backend health check successful:', data);
    return { healthy: true };
    
  } catch (error) {
    let errorMessage = 'Connection failed';
    
    if (error instanceof Error) {
      if (error.name === 'AbortError' || error.name === 'TimeoutError') {
        errorMessage = 'Backend connection timeout (10s)';
      } else if (error.message.includes('fetch')) {
        errorMessage = 'Network error - backend not reachable';
      } else {
        errorMessage = error.message;
      }
    }
    
    console.warn('⚠️ Backend health check failed:', errorMessage);
    return { 
      healthy: false, 
      error: errorMessage 
    };
  }
};

// Authentication callback handler for Cognito code exchange
export const handleAuthCallback = async (code: string, state: string): Promise<any> => {
  try {
    const response = await callBackendAPI('/auth/callback', {
      method: 'POST',
      body: JSON.stringify({ code, state })
    });
    return response;
  } catch (error) {
    console.error('Auth callback error:', error);
    throw error;
  }
};