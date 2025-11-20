import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCurrentUser, hasPermission, PERMISSIONS } from '@/lib/rbac';
import { buildLogoutUrl } from '../lib/auth-utils';

interface User {
  email: string;
  uid?: string;
  sub?: string;
  name: string;
  authMethod?: string;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const currentUser = getCurrentUser();
    if (currentUser) {
      setUser({
        name: currentUser.name,
        email: currentUser.email,
        uid: currentUser.uid,
        authMethod: currentUser.authMethod
      });
    }
  }, []);

  const handleLogout = async () => {
    const devvSid = localStorage.getItem('DEVV_CODE_SID');
    const cognitoToken = localStorage.getItem('access_token');
    
    if (devvSid) {
      // Handle Devv logout
      try {
        const { auth } = await import('@devvai/devv-code-backend');
        await auth.logout();
      } catch (error) {
        console.log('Devv logout not available, clearing localStorage');
      }
      
      // Clear Devv authentication data
      localStorage.removeItem('devv_authenticated');
      localStorage.removeItem('devv_user');
      localStorage.removeItem('DEVV_CODE_SID');
      
      navigate('/login');
    } else if (cognitoToken) {
      // Handle Cognito logout
      localStorage.removeItem('access_token');
      localStorage.removeItem('id_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');

      // Redirect to Cognito logout URL using environment variables
      const logoutUrl = await buildLogoutUrl();
      window.location.href = logoutUrl;
    } else {
      // Fallback: clear everything and redirect
      localStorage.clear();
      navigate('/login');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-slate-900">AAP Dashboard</h1>
            </div>
            <div className="flex items-center gap-4">
              {user && (
                <span className="text-slate-700 font-medium">
                  {user.name || user.email}
                </span>
              )}
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
            <h2 className="text-2xl font-bold mb-4 text-slate-900">Welcome to AAP!</h2>
            {user && (
              <div className="space-y-3">
                <p className="text-slate-700">
                  <strong className="text-slate-900">Name:</strong> {user.name || 'User'}
                </p>
                <p className="text-slate-700">
                  <strong className="text-slate-900">Email:</strong> {user.email}
                </p>
              </div>
            )}
            
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
              <p className="text-green-800">
                ✅ Authentication successful! You're now logged in.
              </p>
            </div>

            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
              <h3 className="font-semibold text-blue-900 mb-3">Quick Navigation:</h3>
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={() => navigate('/chat')}
                  className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors font-medium"
                >
                  Start New Chat
                </button>

                <button
                  onClick={() => navigate('/my-workflows')}
                  className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors font-medium"
                >
                  My Workflows
                </button>

                {hasPermission(PERMISSIONS.ADMIN_PANEL_ACCESS) && (
                  <button
                    onClick={() => navigate('/admin')}
                    className="px-4 py-2 bg-purple-500 text-white rounded-md hover:bg-purple-600 transition-colors font-medium"
                  >
                    Admin Panel
                  </button>
                )}

                <button
                  onClick={() => navigate('/settings')}
                  className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors font-medium"
                >
                  Settings
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}