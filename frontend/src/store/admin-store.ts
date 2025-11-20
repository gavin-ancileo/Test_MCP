import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Prompt {
  code: string;
  name: string;
  categories: string[];
  content: string;
  outputFolder?: string;
  variables: string[];
  createdAt: string;
  updatedAt: string;
}

export interface User {
  id: string;
  email: string;
  roles: string[];
  lastLogin?: string;
  status: 'active' | 'inactive';
}

interface AdminState {
  // Prompts
  prompts: Prompt[];
  selectedPrompt: Prompt | null;
  
  // Users  
  users: User[];
  selectedUser: User | null;
  
  // UI State
  activeTab: 'prompts' | 'users' | 'test' | 'settings';
  isLoading: boolean;
  
  // Actions
  setActiveTab: (tab: 'prompts' | 'users' | 'test' | 'settings') => void;
  setLoading: (loading: boolean) => void;
  
  // Prompt actions
  addPrompt: (prompt: Omit<Prompt, 'variables' | 'createdAt' | 'updatedAt'>) => void;
  updatePrompt: (code: string, updates: Partial<Prompt>) => void;
  deletePrompt: (code: string) => void;
  setSelectedPrompt: (prompt: Prompt | null) => void;
  
  // User actions
  addUser: (user: Omit<User, 'id' | 'lastLogin'>) => void;
  updateUser: (id: string, updates: Partial<User>) => void;
  deleteUser: (id: string) => void;
  setSelectedUser: (user: User | null) => void;
  
  // Utility
  extractVariables: (content: string) => string[];
}

export const useAdminStore = create<AdminState>()(
  persist(
    (set, get) => ({
      // Initial state
      prompts: [],
      selectedPrompt: null,
      users: [],
      selectedUser: null,
      activeTab: 'prompts',
      isLoading: false,
      
      // Actions
      setActiveTab: (tab) => set({ activeTab: tab }),
      setLoading: (loading) => set({ isLoading: loading }),
      
      // Prompt actions
      addPrompt: (promptData) => {
        const variables = get().extractVariables(promptData.content);
        const prompt: Prompt = {
          ...promptData,
          variables,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };
        
        set((state) => ({
          prompts: [...state.prompts, prompt]
        }));
      },
      
      updatePrompt: (code, updates) => {
        set((state) => ({
          prompts: state.prompts.map(p => 
            p.code === code 
              ? { 
                  ...p, 
                  ...updates, 
                  variables: updates.content ? get().extractVariables(updates.content) : p.variables,
                  updatedAt: new Date().toISOString()
                }
              : p
          )
        }));
      },
      
      deletePrompt: (code) => {
        set((state) => ({
          prompts: state.prompts.filter(p => p.code !== code),
          selectedPrompt: state.selectedPrompt?.code === code ? null : state.selectedPrompt
        }));
      },
      
      setSelectedPrompt: (prompt) => set({ selectedPrompt: prompt }),
      
      // User actions
      addUser: (userData) => {
        const user: User = {
          ...userData,
          id: crypto.randomUUID(),
        };
        
        set((state) => ({
          users: [...state.users, user]
        }));
      },
      
      updateUser: (id, updates) => {
        set((state) => ({
          users: state.users.map(u => 
            u.id === id ? { ...u, ...updates } : u
          )
        }));
      },
      
      deleteUser: (id) => {
        set((state) => ({
          users: state.users.filter(u => u.id !== id),
          selectedUser: state.selectedUser?.id === id ? null : state.selectedUser
        }));
      },
      
      setSelectedUser: (user) => set({ selectedUser: user }),
      
      // Utility functions
      extractVariables: (content: string): string[] => {
        const matches = content.match(/\{\{(\w+)\}\}/g) || [];
        const variables = new Set<string>();
        
        matches.forEach(match => {
          const varName = match.replace(/\{\{|\}\}/g, '');
          variables.add(varName);
        });
        
        return Array.from(variables);
      },
    }),
    {
      name: 'admin-storage',
      partialize: (state) => ({
        prompts: state.prompts,
        users: state.users,
      }),
    }
  )
);