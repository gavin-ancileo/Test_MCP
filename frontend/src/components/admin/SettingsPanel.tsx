import React, { useState, useEffect } from 'react';
import { Save, TestTube, Server, Key, Database, Github, ExternalLink } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import HealthCheck from '@/components/HealthCheck';
import { authenticatedFetch } from '@/lib/auth-utils';

const SettingsPanel: React.FC = () => {
  const [settings, setSettings] = useState({
    openai_api_key: '',
    backend_url: '',
    github_client_id: '',
    jira_base_url: '',
    drive_folder_id: '',
  });
  const [loading, setLoading] = useState(false);
  const [testResults, setTestResults] = useState<Record<string, string>>({});
  const { toast } = useToast();

  // Use relative URL for API calls - nginx will route to backend
  const API_URL = '/api';

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = () => {
    // Load from localStorage
    const savedSettings = {
      openai_api_key: localStorage.getItem('openai_api_key') || '',
      backend_url: localStorage.getItem('backend_url') || API_URL,
      github_client_id: localStorage.getItem('github_client_id') || '',
      jira_base_url: localStorage.getItem('jira_base_url') || '',
      drive_folder_id: localStorage.getItem('drive_folder_id') || '',
    };
    setSettings(savedSettings);
  };

  const saveSettings = () => {
    // Save to localStorage
    Object.entries(settings).forEach(([key, value]) => {
      if (value) {
        localStorage.setItem(key, value);
      } else {
        localStorage.removeItem(key);
      }
    });

    toast({
      title: "Success",
      description: "Settings saved successfully",
    });
  };

  const testApiKey = async () => {
    if (!settings.openai_api_key) {
      toast({
        title: "Error",
        description: "Please enter an OpenAI API key first",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('https://api.openai.com/v1/models', {
        headers: {
          'Authorization': `Bearer ${settings.openai_api_key}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setTestResults(prev => ({ ...prev, openai: 'API key is valid ✅' }));
        toast({
          title: "Success",
          description: "OpenAI API key is valid",
        });
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      const errorMsg = `API key test failed: ${error}`;
      setTestResults(prev => ({ ...prev, openai: errorMsg }));
      toast({
        title: "Error",
        description: errorMsg,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const testBackendConnection = async () => {
    if (!settings.backend_url) {
      toast({
        title: "Error", 
        description: "Please enter a backend URL first",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const response = await authenticatedFetch(`${settings.backend_url}/healthz`);
      
      if (response.ok) {
        const data = await response.json();
        setTestResults(prev => ({ 
          ...prev, 
          backend: `Backend is healthy ✅ (${data.status})` 
        }));
        toast({
          title: "Success",
          description: "Backend connection successful",
        });
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      const errorMsg = `Backend test failed: ${error}`;
      setTestResults(prev => ({ ...prev, backend: errorMsg }));
      toast({
        title: "Error",
        description: errorMsg,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Admin Settings</h2>
        <p className="text-gray-600 mt-1">Configure system settings and integrations</p>
      </div>

      {/* Backend Configuration */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Server className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-medium text-gray-900">Backend Configuration</h3>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Backend API URL
            </label>
            <input
              type="url"
              placeholder="http://localhost:8000/api"
              value={settings.backend_url}
              onChange={(e) => setSettings(prev => ({ ...prev, backend_url: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              Current: <code>{API_URL}</code>
            </p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => {
                setSettings(prev => ({ ...prev, backend_url: API_URL }));
                localStorage.setItem('backend_url', API_URL);
              }}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <Save className="w-4 h-4 inline mr-2" />
              Save Backend URL
            </button>
            <button
              onClick={testBackendConnection}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              <TestTube className="w-4 h-4" />
              Test Connection
            </button>
          </div>

          {testResults.backend && (
            <div className="mt-3 p-3 bg-gray-100 rounded-lg">
              <code className="text-sm">{testResults.backend}</code>
            </div>
          )}
        </div>
      </div>

      {/* Health Check Component */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Database className="w-5 h-5 text-green-600" />
          <h3 className="text-lg font-medium text-gray-900">System Health</h3>
        </div>
        <HealthCheck />
      </div>

      {/* OpenAI Configuration */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Key className="w-5 h-5 text-purple-600" />
          <h3 className="text-lg font-medium text-gray-900">OpenAI Configuration</h3>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              OpenAI API Key
            </label>
            <input
              type="password"
              placeholder="sk-..."
              value={settings.openai_api_key}
              onChange={(e) => setSettings(prev => ({ ...prev, openai_api_key: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              Your API key is stored locally and never sent to our servers
            </p>
          </div>

          <div className="flex gap-3">
            <button
              onClick={saveSettings}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <Save className="w-4 h-4 inline mr-2" />
              Save Settings
            </button>
            <button
              onClick={testApiKey}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              <TestTube className="w-4 h-4" />
              Test API Key
            </button>
          </div>

          {testResults.openai && (
            <div className="mt-3 p-3 bg-gray-100 rounded-lg">
              <code className="text-sm">{testResults.openai}</code>
            </div>
          )}
        </div>
      </div>

      {/* Integration Settings */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Github className="w-5 h-5 text-gray-800" />
          <h3 className="text-lg font-medium text-gray-900">Integration Settings</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              GitHub Client ID
            </label>
            <input
              type="text"
              placeholder="GitHub OAuth App Client ID"
              value={settings.github_client_id}
              onChange={(e) => setSettings(prev => ({ ...prev, github_client_id: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Jira Base URL
            </label>
            <input
              type="url"
              placeholder="https://company.atlassian.net"
              value={settings.jira_base_url}
              onChange={(e) => setSettings(prev => ({ ...prev, jira_base_url: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Google Drive Folder ID
            </label>
            <input
              type="text"
              placeholder="1ViGWBhDzjbNit-oy0YTMaB8PSke8PVrs"
              value={settings.drive_folder_id}
              onChange={(e) => setSettings(prev => ({ ...prev, drive_folder_id: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              Default folder ID for document uploads
            </p>
          </div>
        </div>

        <div className="mt-6">
          <button
            onClick={saveSettings}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Save className="w-4 h-4 inline mr-2" />
            Save Integration Settings
          </button>
        </div>
      </div>

      {/* API Documentation */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-amber-900 mb-4">📚 Required Backend APIs</h3>
        <div className="space-y-3 text-sm">
          <div>
            <strong className="text-amber-800">Prompts Management:</strong>
            <ul className="ml-4 mt-1 space-y-1 text-amber-700">
              <li>• <code>GET /prompts</code> - List all prompts</li>
              <li>• <code>POST /prompts</code> - Create new prompt</li>
              <li>• <code>PUT /prompts/{`{code}`}</code> - Update prompt</li>
              <li>• <code>DELETE /prompts/{`{code}`}</code> - Delete prompt</li>
            </ul>
          </div>
          
          <div>
            <strong className="text-amber-800">Testing & AI:</strong>
            <ul className="ml-4 mt-1 space-y-1 text-amber-700">
              <li>• <code>POST /test-prompt</code> - Test prompt with variables</li>
              <li>• <code>GET /healthz</code> - Health check endpoint</li>
            </ul>
          </div>

          <div>
            <strong className="text-amber-800">Users (Optional):</strong>
            <ul className="ml-4 mt-1 space-y-1 text-amber-700">
              <li>• <code>GET /users</code> - List users</li>
              <li>• <code>PUT /users/{`{uid}`}/role</code> - Update user role</li>
            </ul>
          </div>
        </div>
        
        <div className="mt-4 flex items-start gap-2 text-xs text-amber-700">
          <ExternalLink className="w-3 h-3 mt-0.5 flex-shrink-0" />
          <span>Deploy these endpoints to your backend at: <code>{API_URL}</code></span>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;