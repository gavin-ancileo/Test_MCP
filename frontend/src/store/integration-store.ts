import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface IntegrationConnection {
  provider: 'github' | 'jira' | 'drive';
  connected: boolean;
  username?: string;
  accountId?: string;
  connectedAt?: string;
  scopes?: string[];
}

interface IntegrationState {
  connections: IntegrationConnection[];
  isConnecting: boolean;
  connectingProvider?: string;
  
  // Actions
  setConnection: (provider: 'github' | 'jira' | 'drive', data: Partial<IntegrationConnection>) => void;
  removeConnection: (provider: 'github' | 'jira' | 'drive') => void;
  setConnecting: (provider?: string) => void;
  getConnection: (provider: 'github' | 'jira' | 'drive') => IntegrationConnection | undefined;
  isConnected: (provider: 'github' | 'jira' | 'drive') => boolean;
  
  // Integration actions
  connectProvider: (provider: 'github' | 'jira' | 'drive') => Promise<void>;
  disconnectProvider: (provider: 'github' | 'jira' | 'drive') => Promise<void>;
  refreshConnection: (provider: 'github' | 'jira' | 'drive') => Promise<void>;
  fetchAllIntegrations: () => Promise<void>;

  // Telemetry
  logEvent: (event: string, data?: any) => void;
}

export const useIntegrationStore = create<IntegrationState>()(
  persist(
    (set, get) => ({
      connections: [],
      isConnecting: false,
      connectingProvider: undefined,

      setConnection: (provider, data) => {
        set((state) => {
          const existingIndex = state.connections.findIndex(c => c.provider === provider);
          const connection: IntegrationConnection = {
            provider,
            connected: false,
            ...data,
          };
          
          if (existingIndex >= 0) {
            const newConnections = [...state.connections];
            newConnections[existingIndex] = { ...newConnections[existingIndex], ...connection };
            return { connections: newConnections };
          } else {
            return { connections: [...state.connections, connection] };
          }
        });
      },

      removeConnection: (provider) => {
        set((state) => ({
          connections: state.connections.filter(c => c.provider !== provider)
        }));
      },

      setConnecting: (provider) => {
        set({ isConnecting: !!provider, connectingProvider: provider });
      },

      getConnection: (provider) => {
        return get().connections.find(c => c.provider === provider);
      },

      isConnected: (provider) => {
        const connection = get().getConnection(provider);
        return connection?.connected || false;
      },

      connectProvider: async (provider) => {
        const { setConnecting, logEvent } = get();

        try {
          setConnecting(provider);
          logEvent('integration_connect_attempt', { provider });

          // ✅ REDIRECT FLOW: Redirect to OAuth provider
          const authUrl = await getProviderAuthUrl(provider);

          // Save connecting state to localStorage so we can restore after redirect
          localStorage.setItem('oauth_connecting_provider', provider);

          // Redirect to OAuth provider (will come back to /chat?integration=X&status=success)
          window.location.href = authUrl;

        } catch (error) {
          console.error(`Failed to connect ${provider}:`, error);
          logEvent('integration_connect_error', { provider, error: (error as Error).message });
          setConnecting(undefined);
          throw error;
        }
      },

      disconnectProvider: async (provider) => {
        const { removeConnection, logEvent, getConnection } = get();
        
        try {
          const connection = getConnection(provider);
          await revokeProviderAccess(provider);
          removeConnection(provider);
          logEvent('integration_disconnect', { 
            provider, 
            username: connection?.username 
          });
        } catch (error) {
          console.error(`Failed to disconnect ${provider}:`, error);
          throw error;
        }
      },

      refreshConnection: async (provider) => {
        const { setConnection, getConnection, logEvent } = get();
        
        try {
          const connection = getConnection(provider);
          if (!connection?.connected) return;

          const status = await checkProviderConnection(provider);
          if (status.connected) {
            setConnection(provider, {
              connected: true,
              username: status.username,
              accountId: status.accountId,
            });
          } else {
            get().removeConnection(provider);
            logEvent('integration_connection_lost', { provider });
          }
        } catch (error) {
          console.error(`Failed to refresh ${provider} connection:`, error);
        }
      },

      fetchAllIntegrations: async () => {
        try {
          const token = localStorage.getItem('id_token');
          if (!token) return;

          const response = await fetch('/integrations/status', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (!response.ok) {
            console.error('Failed to fetch integrations status:', response.status);
            return;
          }

          const data = await response.json();
          const { setConnection, removeConnection } = get();

          // Update connections from backend response
          const providers: Array<'github' | 'jira' | 'drive'> = ['github', 'jira', 'drive'];

          providers.forEach(provider => {
            const integration = data.integrations?.[provider];
            if (integration?.connected) {
              setConnection(provider, {
                connected: true,
                username: integration.username || integration.provider_user_email,
                accountId: integration.provider_user_id,
                connectedAt: integration.created_at,
                scopes: integration.scope?.split(' '),
              });
            } else {
              removeConnection(provider);
            }
          });

          console.log('✅ Integrations fetched successfully', data);
        } catch (error) {
          console.error('Failed to fetch all integrations:', error);
        }
      },

      logEvent: (event, data = {}) => {
        console.log(`[Integration Event] ${event}:`, data);
        
        const events = JSON.parse(localStorage.getItem('integration_telemetry') || '[]');
        events.push({
          event,
          data,
          timestamp: new Date().toISOString(),
        });
        
        // Keep only last 100 events
        if (events.length > 100) {
          events.splice(0, events.length - 100);
        }
        
        localStorage.setItem('integration_telemetry', JSON.stringify(events));
      },
    }),
    {
      name: 'aap-integrations',
      partialize: (state) => ({
        connections: state.connections,
      }),
    }
  )
);

// ============================================
// ✅ UPDATED: Backend-connected OAuth helpers
// ============================================

async function getProviderAuthUrl(provider: 'github' | 'jira' | 'drive'): Promise<string> {
  const token = localStorage.getItem('id_token');

  const response = await fetch(`/integrations/connect/${provider}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error(`Failed to initiate OAuth for ${provider}`);
  }
  
  const data = await response.json();
  
  // Store state for CSRF verification
  sessionStorage.setItem(`${provider}_oauth_state`, data.state);
  
  return data.authorization_url;
}

async function openOAuthPopup(url: string, provider: string): Promise<any> {
  return new Promise((resolve, reject) => {
    // Open OAuth in popup window
    const width = 600;
    const height = 700;
    const left = (window.screen.width - width) / 2;
    const top = (window.screen.height - height) / 2;

    const popup = window.open(
      url,
      `${provider}_oauth`,
      `width=${width},height=${height},left=${left},top=${top},toolbar=no,location=no,status=no,menubar=no,scrollbars=yes`
    );

    if (!popup) {
      reject(new Error('Popup blocked. Please allow popups for this site.'));
      return;
    }

    // Listen for postMessage from popup
    const handleMessage = async (event: MessageEvent) => {
      // Security: verify origin
      if (event.origin !== window.location.origin) {
        return;
      }

      // Check if this is our OAuth success message
      if (event.data?.type === 'oauth-success' && event.data?.provider === provider) {
        console.log('✅ OAuth success message received from popup', event.data);

        // Cleanup
        window.removeEventListener('message', handleMessage);
        clearTimeout(timeoutId);

        try {
          // Wait a bit for backend to save integration
          await new Promise(resolve => setTimeout(resolve, 500));

          // Fetch connection details from backend
          const details = await fetchConnectionDetails(provider);
          resolve({
            success: true,
            username: details.username,
            accountId: details.accountId,
            scopes: details.scopes,
          });
        } catch (error) {
          reject(error);
        }
      }
    };

    window.addEventListener('message', handleMessage);

    // REMOVED popup.closed check - COOP policy blocks it
    // Instead, rely entirely on postMessage and timeout

    // Timeout after 5 minutes
    const timeoutId = setTimeout(() => {
      window.removeEventListener('message', handleMessage);
      try {
        popup.close();
      } catch (e) {
        console.warn('Could not close popup:', e);
      }
      reject(new Error('OAuth timeout - please try again'));
    }, 300000);
  });
}

async function fetchConnectionDetails(provider: string): Promise<any> {
  const token = localStorage.getItem('id_token');

  const response = await fetch('/integrations/status', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    throw new Error('Failed to fetch connection details');
  }

  const data = await response.json();
  // Backend returns integrations as object keyed by provider, not array
  const connection = data.integrations?.[provider];

  if (!connection) {
    throw new Error('Connection not found');
  }

  return {
    username: connection.connected_as,
    accountId: connection.provider_user_id || provider + '-' + Date.now(),
    scopes: connection.scopes || [],
  };
}

async function revokeProviderAccess(provider: string): Promise<void> {
  const token = localStorage.getItem('id_token');

  const response = await fetch(`/integrations/${provider}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (!response.ok) {
    throw new Error(`Failed to disconnect ${provider}`);
  }
}

async function checkProviderConnection(provider: string): Promise<any> {
  const token = localStorage.getItem('id_token');

  try {
    const response = await fetch('/integrations/status', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      return { connected: false };
    }
    
    const data = await response.json();
    const connection = data.integrations?.find((i: any) => i.provider === provider);
    
    if (connection) {
      return {
        connected: true,
        username: connection.connected_as,
        accountId: connection.provider_user_id
      };
    }
    
    return { connected: false };
  } catch (error) {
    console.error('Failed to check connection:', error);
    return { connected: false };
  }
}