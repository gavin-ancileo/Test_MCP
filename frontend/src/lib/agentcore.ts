export const getAgentCoreConfig = () => {
  return {
    url: '/agentcore',
    isDemoMode: false,
  };
};

export interface AgentCoreRequest {
  message: string;
  conversationId?: string;
}

export interface AgentCoreResponse {
  message: string;
  conversationId: string;
  timestamp: string;
}

export const callAgentCore = async (
  request: AgentCoreRequest,
  idToken: string
): Promise<AgentCoreResponse> => {
  const config = getAgentCoreConfig();
  
  // Demo mode - return mock response
  if (config.isDemoMode) {
    await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API delay
    return {
      message: "Hello from AgentCore mock! This is a simulated response since AGENTCORE_URL is not configured. The UI is fully functional and ready for backend integration.",
      conversationId: request.conversationId || `demo-${Date.now()}`,
      timestamp: new Date().toISOString(),
    };
  }

  // Production mode - call actual AgentCore API
  const response = await fetch(`${config.url}/run`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${idToken}`,
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(errorData.message || errorData.error || `HTTP ${response.status}: ${response.statusText}`);
  }

  return await response.json();
};