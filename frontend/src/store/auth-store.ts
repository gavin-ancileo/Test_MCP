import { create } from 'zustand';
import { authenticatedFetch } from '@/lib/auth-utils';

interface User {
  email: string;
  sub: string;
  name?: string;
}

interface AuthState {
  user: User | null;
  idToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  userRoles: string[];
  isAdmin: boolean;

  // Actions
  setUser: (user: User | null) => void;
  setIdToken: (token: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setUserRoles: (roles: string[], isAdmin: boolean) => void;
  fetchUserInfo: (email: string, name?: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

// Initialize from localStorage if available
const getInitialState = () => {
  if (typeof window === 'undefined') {
    return {
      user: null,
      idToken: null,
      isAuthenticated: false,
    };
  }

  const idToken = localStorage.getItem('id_token');
  const userStr = localStorage.getItem('user');
  let user: User | null = null;

  if (userStr) {
    try {
      const parsed = JSON.parse(userStr);
      user = {
        email: parsed.email || '',
        sub: parsed.sub || '',
        name: parsed.name,
      };
    } catch (e) {
      console.error('Failed to parse user from localStorage:', e);
    }
  }

  return {
    user,
    idToken,
    isAuthenticated: !!(user && idToken),
  };
};

const initialState = getInitialState();

export const useAuthStore = create<AuthState>((set) => ({
  user: initialState.user,
  idToken: initialState.idToken,
  isAuthenticated: initialState.isAuthenticated,
  isLoading: false,
  error: null,
  userRoles: [],
  isAdmin: false,

  setUser: (user) => set({ user, isAuthenticated: !!user }),

  setIdToken: (idToken) => set({ idToken, isAuthenticated: !!idToken }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),

  setUserRoles: (roles, isAdmin) => set({ userRoles: roles, isAdmin }),

  fetchUserInfo: async (email: string, name?: string) => {
    set({ isLoading: true });
    try {
      const response = await authenticatedFetch('/mcp-server/users/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name })
      });

      if (!response.ok) {
        throw new Error('Failed to fetch user info');
      }

      const data = await response.json();
      set({
        userRoles: data.roles || [],
        isAdmin: data.is_admin || false
      });

      console.log('User roles loaded:', data.roles, 'Admin:', data.is_admin);
    } catch (error) {
      console.error('Error fetching user info:', error);
      set({ userRoles: ['ALL'], isAdmin: false });
    } finally {
      set({ isLoading: false });
    }
  },

  clearError: () => set({ error: null }),

  logout: () => {
    // Clear localStorage
    if (typeof window !== 'undefined') {
      localStorage.removeItem('id_token');
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      localStorage.removeItem('devv_authenticated');
      localStorage.removeItem('DEVV_CODE_SID');
    }
    set({
      user: null,
      idToken: null,
      isAuthenticated: false,
      error: null,
      userRoles: [],
      isAdmin: false
    });
  },
}));