// Role-Based Access Control (RBAC) System
import React from 'react';
import { useAuthStore } from '../store/auth-store';

export interface UserRole {
  id: string;
  name: string;
  permissions: string[];
}

export interface UserProfile {
  uid: string;
  email: string;
  name: string;
  role: string;
  permissions: string[];
  authMethod?: string;
  sub?: string; // Legacy Cognito field
}

// Define available permissions
export const PERMISSIONS = {
  // Admin permissions
  ADMIN_PANEL_ACCESS: 'admin:panel:access',
  PROMPT_CREATE: 'prompt:create',
  PROMPT_EDIT: 'prompt:edit',
  PROMPT_DELETE: 'prompt:delete',
  PROMPT_VIEW_ALL: 'prompt:view:all',
  USER_MANAGE: 'user:manage',
  
  // User permissions  
  CHAT_ACCESS: 'chat:access',
  PROMPT_USE: 'prompt:use',
  SETTINGS_BASIC: 'settings:basic',
  INTEGRATION_MANAGE: 'integration:manage',
  
  // Integration permissions
  GITHUB_INTEGRATION: 'integration:github',
  JIRA_INTEGRATION: 'integration:jira',
  DRIVE_INTEGRATION: 'integration:drive',
} as const;

// Define roles with their permissions
export const ROLES: Record<string, UserRole> = {
  admin: {
    id: 'admin',
    name: 'Administrator',
    permissions: [
      PERMISSIONS.ADMIN_PANEL_ACCESS,
      PERMISSIONS.PROMPT_CREATE,
      PERMISSIONS.PROMPT_EDIT,
      PERMISSIONS.PROMPT_DELETE,
      PERMISSIONS.PROMPT_VIEW_ALL,
      PERMISSIONS.USER_MANAGE,
      PERMISSIONS.CHAT_ACCESS,
      PERMISSIONS.PROMPT_USE,
      PERMISSIONS.SETTINGS_BASIC,
      PERMISSIONS.INTEGRATION_MANAGE,
      PERMISSIONS.GITHUB_INTEGRATION,
      PERMISSIONS.JIRA_INTEGRATION,
      PERMISSIONS.DRIVE_INTEGRATION,
    ]
  },
  user: {
    id: 'user',
    name: 'End User',
    permissions: [
      PERMISSIONS.CHAT_ACCESS,
      PERMISSIONS.PROMPT_USE,
      PERMISSIONS.SETTINGS_BASIC,
      PERMISSIONS.INTEGRATION_MANAGE,
      PERMISSIONS.GITHUB_INTEGRATION,
      PERMISSIONS.JIRA_INTEGRATION,
    ]
  }
};

/**
 * Get current user profile with role and permissions
 * Uses RBAC from database (auth-store) instead of hardcoded email check
 */
export function getCurrentUser(): UserProfile | null {
  try {
    // IMPORTANT: Use auth-store data (from database) for admin status
    // This ensures RBAC works correctly with database admin flag
    const authStore = useAuthStore.getState();
    
    // Check Devv authentication first
    const devvUser = localStorage.getItem('devv_user');
    const devvSid = localStorage.getItem('DEVV_CODE_SID');
    
    if (devvUser || devvSid) {
      const parsed = devvUser ? JSON.parse(devvUser) : null;
      const email = parsed?.email || 'user@example.com';
      
      // Use admin status from auth-store (database) instead of hardcoded check
      const isAdmin = authStore.isAdmin || false;
      const role = isAdmin ? 'admin' : 'user';
      
      return {
        uid: parsed?.uid || 'devv-user',
        email,
        name: parsed?.name || parsed?.email || 'User',
        role,
        permissions: ROLES[role]?.permissions || [],
        authMethod: 'Devv.ai Email'
      };
    }
    
    // Check Cognito authentication
    const cognitoUser = localStorage.getItem('user');
    const cognitoToken = localStorage.getItem('access_token');
    
    if (cognitoUser && cognitoToken) {
      const parsed = JSON.parse(cognitoUser);
      const email = parsed.email;
      
      // Use admin status from auth-store (database) instead of hardcoded check
      const isAdmin = authStore.isAdmin || false;
      const role = isAdmin ? 'admin' : 'user';
      
      return {
        uid: parsed.sub,
        email,
        name: parsed.name || parsed.email,
        role,
        permissions: ROLES[role]?.permissions || [],
        authMethod: 'Company SSO (Cognito)',
        sub: parsed.sub
      };
    }
    
    return null;
  } catch (error) {
    console.error('Error getting current user:', error);
    return null;
  }
}

/**
 * Check if user has specific permission
 */
export function hasPermission(permission: string): boolean {
  const user = getCurrentUser();
  return user?.permissions?.includes(permission) || false;
}

/**
 * Check if user has admin role
 * Uses RBAC from database (auth-store) instead of hardcoded email check
 */
export function isAdmin(): boolean {
  try {
    // Use auth-store data (from database) for admin status
    const authStore = useAuthStore.getState();
    return authStore.isAdmin || false;
  } catch (error) {
    console.error('Error checking admin status:', error);
    // Fallback to permission check
    return hasPermission(PERMISSIONS.ADMIN_PANEL_ACCESS);
  }
}

/**
 * Check if user is admin based on email
 * BYPASSED FOR DEVELOPMENT - gavinpham has admin access
 */
function checkIsAdmin(email: string): boolean {
  console.log('🔍 Checking admin status for email:', email);

  // Define admin emails
  const adminEmails = [
    'admin@ancileo.com',
    'gavin.pham@ancileo.com',
    // Add more admin emails as needed
  ];

  // Check exact match first
  if (adminEmails.includes(email.toLowerCase())) {
    console.log('✅ Admin detected: email in admin list');
    return true;
  }

  // Check if email contains 'admin' for demo purposes
  if (email.toLowerCase().includes('admin')) {
    console.log('✅ Admin detected: contains "admin"');
    return true;
  }

  console.log('❌ Not admin user');
  return false;
}

/**
 * Require permission middleware for components
 * CRITICAL FIX: Use React hook to subscribe to auth-store changes
 * This prevents "Access Denied" flash when isAdmin is still loading from backend
 */
export function requirePermission(permission: string) {
  return function (Component: React.ComponentType) {
    return function PermissionWrapper(props: any) {
      // CRITICAL: Use React hook to subscribe to auth-store
      // This makes component re-render when isAdmin/isLoading changes
      const { isLoading, isAdmin } = useAuthStore();

      // Show loading spinner while checking permissions
      if (isLoading) {
        return (
          <div className="flex items-center justify-center min-h-screen bg-gray-100">
            <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full text-center">
              <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading permissions...</p>
            </div>
          </div>
        );
      }

      // CRITICAL FIX: Separate authentication and authorization concerns
      // - Cognito handles SSO authentication (user identity)
      // - Database handles authorization (admin status, roles)
      // For admin panel access, check database isAdmin instead of JWT token permissions
      const hasAccess = permission === PERMISSIONS.ADMIN_PANEL_ACCESS
        ? isAdmin  // Use database is_admin field from auth-store
        : hasPermission(permission);  // Use JWT permissions for other features

      if (!hasAccess) {
        return (
          <div className="flex items-center justify-center min-h-screen bg-gray-100">
            <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full text-center">
              <div className="text-red-500 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 15.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h2 className="text-xl font-bold text-gray-900 mb-2">Access Denied</h2>
              <p className="text-gray-600 mb-4">
                You don't have permission to access this page.
              </p>
              <p className="text-sm text-gray-500">
                Required permission: <code className="bg-gray-100 px-2 py-1 rounded">{permission}</code>
              </p>
              <div className="mt-6">
                <button
                  onClick={() => window.history.back()}
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  Go Back
                </button>
              </div>
            </div>
          </div>
        );
      }

      return <Component {...props} />;
    };
  };
}