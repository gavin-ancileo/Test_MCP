import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { getCurrentUser, requirePermission, PERMISSIONS } from '@/lib/rbac';
import { useAuthStore } from '@/store/auth-store';
import PromptsPanel from './PromptsPanel';
import TestPanel from './TestPanel';
import SettingsPanel from './SettingsPanel';
import UsersPanel from './UsersPanel';
import WorkflowsPanel from './WorkflowsPanel';
import { Settings, MessageSquare, Users, TestTube, ArrowLeft, Workflow } from 'lucide-react';

interface AdminLayoutProps {}

const AdminLayout: React.FC<AdminLayoutProps> = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAdmin, isLoading } = useAuthStore();
  const [user, setUser] = useState(getCurrentUser());

  useEffect(() => {
    const currentUser = getCurrentUser();
    setUser(currentUser);
  }, [isAdmin]); // Re-run when isAdmin changes from auth store

  const currentPath = location.pathname;

  // Show loading while admin status is being fetched from backend
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading admin panel...</p>
        </div>
      </div>
    );
  }
  
  const tabs = [
    { id: 'prompts', label: 'Prompts', icon: MessageSquare, path: '/admin/prompts' },
    { id: 'workflows', label: 'Workflows', icon: Workflow, path: '/admin/workflows' },
    { id: 'test', label: 'Test', icon: TestTube, path: '/admin/test' },
    { id: 'users', label: 'Users', icon: Users, path: '/admin/users' },
    { id: 'settings', label: 'Settings', icon: Settings, path: '/admin/settings' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                <span className="text-sm font-medium">Back to Dashboard</span>
              </button>
              <div className="w-px h-6 bg-gray-300" />
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                AAP Admin Panel
              </h1>
            </div>
            <div className="flex items-center gap-4">
              {user && (
                <div className="text-right">
                  <div className="text-sm font-medium text-gray-900">{user.name}</div>
                  <div className="text-xs text-gray-500">{user.role} • {user.authMethod}</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          {/* Tab Navigation */}
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = currentPath.startsWith(tab.path);
                
                return (
                  <button
                    key={tab.id}
                    onClick={() => navigate(tab.path)}
                    className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                      isActive
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Content */}
          <div className="p-6">
            <Routes>
              <Route path="prompts/*" element={<PromptsPanel />} />
              <Route path="workflows" element={<WorkflowsPanel />} />
              <Route path="test" element={<TestPanel />} />
              <Route path="users" element={<UsersPanel />} />
              <Route path="settings" element={<SettingsPanel />} />
              <Route path="" element={<PromptsPanel />} />
            </Routes>
          </div>
        </div>
      </div>
    </div>
  );
};

// Apply permission requirement
export default requirePermission(PERMISSIONS.ADMIN_PANEL_ACCESS)(AdminLayout);