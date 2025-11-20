/**
 * Enhanced Conversation Store with DynamoDB Backend
 *
 * Features:
 * - Persistent storage in DynamoDB
 * - Session management API integration
 * - Backward compatible with local storage
 * - Auto-sync with backend
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authenticatedFetch } from '@/lib/auth-utils';

// Always use relative URLs in browser (nginx will proxy)
// This avoids localhost fallback issues in production
const API_URL = '';

export interface Message {
  id: string;
  message_id?: string;  // DynamoDB format
  content: string;
  role: 'user' | 'assistant';
  timestamp: string | number;
  created_at?: string;
  metadata?: Record<string, any>;
}

export interface Conversation {
  id: string;
  session_id?: string;  // DynamoDB format
  title: string;
  messages: Message[];
  createdAt: string | number;
  updatedAt: string | number;
  created_at?: number;  // DynamoDB format
  updated_at?: number;  // DynamoDB format
  message_count?: number;
  user_id?: string;
  status?: string;
}

interface ConversationState {
  conversations: Conversation[];
  activeConversationId: string | null;
  isLoading: boolean;
  isSyncing: boolean;
  lastSyncTime: string | null;

  // Actions
  createConversation: (firstMessage?: string) => Promise<string>;
  addMessage: (conversationId: string, message: Omit<Message, 'id' | 'timestamp'>) => Promise<void>;
  setActiveConversation: (id: string | null) => void;
  updateConversationTitle: (id: string, title: string) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  setLoading: (loading: boolean) => void;

  // Sync actions
  syncConversations: () => Promise<void>;
  loadConversationMessages: (id: string) => Promise<void>;

  // Getters
  getActiveConversation: () => Conversation | null;
  getConversation: (id: string) => Conversation | null;
}

/**
 * API Helper Functions
 */
const api = {
  // Create new session
  async createSession(title: string = 'New Chat'): Promise<{ session_id: string; title: string; created_at: number; updated_at: number }> {
    // Get auth token from localStorage
    const idToken = localStorage.getItem('id_token');
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (idToken) {
      headers['Authorization'] = `Bearer ${idToken}`;
    }

    const url = `/agentcore/sessions`;
    console.log(`[createSession] Calling: ${url}`);
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify({ title }),
    });

    if (!response.ok) {
      throw new Error('Failed to create session');
    }

    return response.json();
  },

  // List all sessions
  async listSessions(): Promise<{ sessions: any[]; count: number }> {
    // Get auth token from localStorage
    const idToken = localStorage.getItem('id_token');
    const headers: HeadersInit = {};
    if (idToken) {
      headers['Authorization'] = `Bearer ${idToken}`;
    }

    const url = `/agentcore/sessions`;
    console.log(`[listSessions] Calling: ${url}`);
    const response = await fetch(url, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      throw new Error('Failed to list sessions');
    }

    return response.json();
  },

  // Get messages for a session
  async getSessionMessages(sessionId: string): Promise<{ session_id: string; messages: any[]; count: number }> {
    // Get auth token from localStorage
    const idToken = localStorage.getItem('id_token');
    const headers: HeadersInit = {};
    if (idToken) {
      headers['Authorization'] = `Bearer ${idToken}`;
    }

    const url = `/agentcore/sessions/${sessionId}/messages`;
    console.log(`[getSessionMessages] Calling: ${url}`);
    const response = await fetch(url, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      throw new Error('Failed to get session messages');
    }

    return response.json();
  },

  // Update session title
  async updateSessionTitle(sessionId: string, title: string): Promise<void> {
    const response = await authenticatedFetch(`${API_URL}/agentcore/sessions/${sessionId}/title?title=${encodeURIComponent(title)}`, {
      method: 'PUT',
    });

    if (!response.ok) {
      throw new Error('Failed to update session title');
    }
  },

  // Delete session
  async deleteSession(sessionId: string): Promise<void> {
    const response = await authenticatedFetch(`${API_URL}/agentcore/sessions/${sessionId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to delete session');
    }
  },
};

/**
 * Normalize functions to convert between local and DynamoDB formats
 */
function normalizeConversation(conv: any): Conversation {
  // Auto-generate title from first user message if title is "New Chat" or empty
  let title = conv.title || 'New Chat';
  const messages = conv.messages || [];
  
  if ((title === 'New Chat' || !title || title.trim() === '') && messages.length > 0) {
    // Find first user message
    const firstUserMessage = messages.find((msg: any) => msg.role === 'user');
    if (firstUserMessage && firstUserMessage.content) {
      // Generate title from first message (max 50 chars)
      const content = firstUserMessage.content.trim();
      title = content.length > 50 ? content.substring(0, 50) + '...' : content;
    }
  }
  
  return {
    id: conv.id || conv.session_id,
    session_id: conv.session_id || conv.id,
    title: title,
    messages: messages,
    createdAt: conv.createdAt || conv.created_at || Date.now(),
    updatedAt: conv.updatedAt || conv.updated_at || Date.now(),
    created_at: conv.created_at,
    updated_at: conv.updated_at,
    message_count: conv.message_count || messages.length || 0,
    user_id: conv.user_id,
    status: conv.status || 'active',
  };
}

function normalizeMessage(msg: any): Message {
  return {
    id: msg.id || msg.message_id,
    message_id: msg.message_id || msg.id,
    content: msg.content,
    role: msg.role,
    timestamp: msg.timestamp || msg.created_at || Date.now(),
    created_at: msg.created_at,
    metadata: msg.metadata,
  };
}

/**
 * Enhanced Conversation Store
 */
export const useConversationStore = create<ConversationState>()(
  persist(
    (set, get) => ({
      conversations: [],
      activeConversationId: null,
      isLoading: false,
      isSyncing: false,
      lastSyncTime: null,

      /**
       * Create new conversation
       * - Creates session in DynamoDB if available
       * - Falls back to local storage
       */
      createConversation: async (firstMessage) => {
        try {
          // Try to create session in backend
          const session = await api.createSession(
            firstMessage ? firstMessage.slice(0, 50) + (firstMessage.length > 50 ? '...' : '') : 'New Chat'
          );

          const newConversation: Conversation = normalizeConversation({
            ...session,
            messages: [],
          });

          set((state) => ({
            conversations: [newConversation, ...state.conversations],
            activeConversationId: newConversation.id,
          }));

          return newConversation.id;
        } catch (error) {
          console.error('Failed to create session in backend, using local:', error);

          // Fallback to local creation
          const id = `conv-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
          const now = new Date().toISOString();

          const newConversation: Conversation = {
            id,
            title: firstMessage ? firstMessage.slice(0, 50) + (firstMessage.length > 50 ? '...' : '') : 'New Conversation',
            messages: [],
            createdAt: now,
            updatedAt: now,
          };

          set((state) => ({
            conversations: [newConversation, ...state.conversations],
            activeConversationId: id,
          }));

          return id;
        }
      },

      /**
       * Add message to conversation
       * - Messages are saved to DynamoDB by backend during chat
       * - Update local state immediately for UI responsiveness
       */
      addMessage: async (conversationId, message) => {
        const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const now = Date.now();

        const fullMessage: Message = {
          ...message,
          id: messageId,
          timestamp: now,
        };

        set((state) => ({
          conversations: state.conversations.map((conv) =>
            conv.id === conversationId
              ? {
                  ...conv,
                  messages: [...conv.messages, fullMessage],
                  updatedAt: now,
                  message_count: (conv.message_count || 0) + 1,
                  // Update title with first user message if it's still default
                  title: (conv.title === 'New Conversation' || conv.title === 'New Chat') && message.role === 'user'
                    ? message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '')
                    : conv.title,
                }
              : conv
          ),
        }));

        // Backend saves messages automatically during chat
        // No need to call API here
      },

      /**
       * Set active conversation
       */
      setActiveConversation: (id) => {
        set({ activeConversationId: id });

        // Load messages from backend if not already loaded
        if (id) {
          const conv = get().getConversation(id);
          if (conv && conv.messages.length === 0) {
            get().loadConversationMessages(id);
          }
        }
      },

      /**
       * Update conversation title
       */
      updateConversationTitle: async (id, title) => {
        try {
          await api.updateSessionTitle(id, title);

          set((state) => ({
            conversations: state.conversations.map((conv) =>
              conv.id === id ? { ...conv, title, updatedAt: Date.now() } : conv
            ),
          }));
        } catch (error) {
          console.error('Failed to update title in backend, updating local only:', error);

          // Fallback to local update
          set((state) => ({
            conversations: state.conversations.map((conv) =>
              conv.id === id ? { ...conv, title, updatedAt: Date.now() } : conv
            ),
          }));
        }
      },

      /**
       * Delete conversation
       */
      deleteConversation: async (id) => {
        try {
          await api.deleteSession(id);

          set((state) => ({
            conversations: state.conversations.filter((conv) => conv.id !== id),
            activeConversationId: state.activeConversationId === id ? null : state.activeConversationId,
          }));
        } catch (error) {
          console.error('Failed to delete session in backend, deleting local only:', error);

          // Fallback to local deletion
          set((state) => ({
            conversations: state.conversations.filter((conv) => conv.id !== id),
            activeConversationId: state.activeConversationId === id ? null : state.activeConversationId,
          }));
        }
      },

      /**
       * Set loading state
       */
      setLoading: (isLoading) => {
        set({ isLoading });
      },

      /**
       * Sync conversations from backend
       */
      syncConversations: async () => {
        try {
          set({ isSyncing: true });

          const { sessions } = await api.listSessions();

          const normalizedConversations = sessions.map(normalizeConversation);

          // Load messages for each conversation that has messages but not loaded yet
          const conversationsWithMessages = await Promise.all(
            normalizedConversations.map(async (conv) => {
              // If conversation has message_count > 0 but no messages loaded, load them
              if ((conv.message_count || 0) > 0 && conv.messages.length === 0) {
                try {
                  const { messages } = await api.getSessionMessages(conv.id);
                  const normalizedMessages = (messages || []).map(normalizeMessage);
                  const updatedConv = { ...conv, messages: normalizedMessages };
                  
                  // Auto-generate title from first message if title is still "New Chat"
                  if ((updatedConv.title === 'New Chat' || !updatedConv.title || updatedConv.title.trim() === '') && normalizedMessages.length > 0) {
                    const firstUserMessage = normalizedMessages.find((msg: any) => msg.role === 'user');
                    if (firstUserMessage && firstUserMessage.content) {
                      const content = firstUserMessage.content.trim();
                      updatedConv.title = content.length > 50 ? content.substring(0, 50) + '...' : content;
                    }
                  }
                  
                  return updatedConv;
                } catch (error) {
                  console.error(`Failed to load messages for conversation ${conv.id}:`, error);
                  return conv;
                }
              }
              return conv;
            })
          );

          set({
            conversations: conversationsWithMessages,
            isSyncing: false,
            lastSyncTime: new Date().toISOString(),
          });

          console.log(`✅ Synced ${sessions.length} conversations from backend with messages`);
        } catch (error) {
          console.error('❌ Failed to sync conversations:', error);

          // Clear stale cache on sync error to force fresh load next time
          set({
            conversations: [],
            isSyncing: false,
            lastSyncTime: null,
          });

          // Clear localStorage to force fresh data on next load
          try {
            localStorage.removeItem('conversation-store-enhanced');
          } catch (e) {
            console.warn('Failed to clear localStorage:', e);
          }
        }
      },

      /**
       * Load messages for a conversation
       */
      loadConversationMessages: async (id) => {
        try {
          const { messages } = await api.getSessionMessages(id);

          const normalizedMessages = (messages || []).map(normalizeMessage);

          set((state) => ({
            conversations: state.conversations.map((conv) =>
              conv.id === id
                ? { ...conv, messages: normalizedMessages }
                : conv
            ),
          }));

          console.log(`✅ Loaded ${normalizedMessages.length} messages for conversation ${id}`);
        } catch (error) {
          console.error('Failed to load conversation messages:', error);
        }
      },

      /**
       * Get active conversation
       */
      getActiveConversation: () => {
        const state = get();
        return state.conversations.find((conv) => conv.id === state.activeConversationId) || null;
      },

      /**
       * Get conversation by ID
       */
      getConversation: (id) => {
        const state = get();
        return state.conversations.find((conv) => conv.id === id) || null;
      },
    }),
    {
      name: 'conversation-store-enhanced',
      partialize: (state) => ({
        conversations: state.conversations,
        activeConversationId: state.activeConversationId,
        lastSyncTime: state.lastSyncTime,
      }),
    }
  )
);

/**
 * Auto-sync on app load
 */
if (typeof window !== 'undefined') {
  // Helper function to check if user is authenticated
  const isAuthenticated = () => {
    const idToken = localStorage.getItem('id_token');
    const accessToken = localStorage.getItem('access_token');
    const devvAuth = localStorage.getItem('devv_authenticated');
    const devvSid = localStorage.getItem('DEVV_CODE_SID');
    return !!(idToken || accessToken || devvAuth === 'true' || devvSid);
  };

  // Sync conversations when app loads (only if authenticated)
  setTimeout(() => {
    if (isAuthenticated()) {
      const store = useConversationStore.getState();
      store.syncConversations().catch(console.error);
    }
  }, 1000);

  // Periodic sync every 5 minutes (only if authenticated)
  setInterval(() => {
    if (isAuthenticated()) {
      const store = useConversationStore.getState();
      if (!store.isSyncing) {
        store.syncConversations().catch(console.error);
      }
    }
  }, 5 * 60 * 1000);
}
