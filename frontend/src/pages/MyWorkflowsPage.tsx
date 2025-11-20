import React from 'react';
import { useNavigate } from 'react-router-dom';
import MyWorkflowsPanel from '@/components/user/MyWorkflowsPanel';
import { buildLogoutUrl } from '@/lib/auth-utils';

export default function MyWorkflowsPage() {
  const navigate = useNavigate();

  const handleLogout = async () => {
    const devvSid = localStorage.getItem('DEVV_CODE_SID');
    const cognitoToken = localStorage.getItem('access_token');

    if (devvSid) {
      try {
        const { auth } = await import('@devvai/devv-code-backend');
        await auth.logout();
      } catch (error) {
        console.log('Devv logout not available, clearing localStorage');
      }

      localStorage.removeItem('devv_authenticated');
      localStorage.removeItem('devv_user');
      localStorage.removeItem('DEVV_CODE_SID');

      navigate('/login');
    } else if (cognitoToken) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('id_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');

      const logoutUrl = await buildLogoutUrl();
      window.location.href = logoutUrl;
    } else {
      localStorage.clear();
      navigate('/login');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-6">
              <h1 className="text-xl font-bold text-slate-900">AAP</h1>
              <div className="flex gap-2">
                <button
                  onClick={() => navigate('/dashboard')}
                  className="px-3 py-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors"
                >
                  Dashboard
                </button>
                <button
                  onClick={() => navigate('/chat')}
                  className="px-3 py-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors"
                >
                  Chat
                </button>
                <button
                  onClick={() => navigate('/my-workflows')}
                  className="px-3 py-2 text-green-600 bg-green-50 rounded-md font-medium"
                >
                  My Workflows
                </button>
              </div>
            </div>
            <div className="flex items-center">
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

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <MyWorkflowsPanel />
        </div>
      </main>
    </div>
  );
}
