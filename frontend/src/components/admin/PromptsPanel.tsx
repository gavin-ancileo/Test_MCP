import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Copy, Play, Eye, Search, Filter } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import PromptModal from './PromptModal';
import { authenticatedFetch } from '@/lib/auth-utils';

export interface Prompt {
  code: string;
  name: string;
  categories: string[];
  content: string;
  output_folder?: string;
  variables: string[];
  created_at?: string;
  updated_at?: string;
}

const PromptsPanel: React.FC = () => {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null);
  const { toast } = useToast();

  // Use /api/prompts endpoint - nginx routes to mcp-server with proper auth headers
  const API_URL = '/api';

  // Categories for filtering
  const categories = ['hr', 'dev', 'qa', 'pm', 'ba', 'tech_lead', 'devops', 'finance', 'cybersecurity', 'support', 'admin', 'all'];

  useEffect(() => {
    loadPrompts();
  }, []);

  const loadPrompts = async () => {
    setLoading(true);
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      // Get auth token from localStorage
      const idToken = localStorage.getItem('id_token');
      const headers: HeadersInit = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      };
      if (idToken) {
        headers['Authorization'] = `Bearer ${idToken}`;
      }

      const response = await fetch(`${API_URL}/prompts`, {
        signal: controller.signal,
        headers,
      });

      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setPrompts(data.prompts || []);
      
      if ((data.prompts || []).length === 0) {
        console.info('No prompts found in database');
      }
    } catch (error) {
      let errorMessage = 'Unknown error';
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorMessage = 'Connection timeout (10s)';
        } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
          errorMessage = 'Network error - backend not reachable';
        } else {
          errorMessage = error.message;
        }
      }

      console.warn('Admin prompts loading failed:', errorMessage);
      setPrompts([]); // Empty array for admin panel when backend fails
      toast({
        title: "Error",
        description: "Failed to load prompts. Check if backend is running.",
        variant: "destructive",
      });
      
      // Demo data for development
      setPrompts([
        {
          code: 'demo_hr_contract',
          name: 'HR Contract Generator',
          categories: ['hr'],
          content: 'Generate a {{contract_type}} contract for {{employee_name}} in the {{position}} role.',
          variables: ['contract_type', 'employee_name', 'position'],
          created_at: '2024-01-15T10:30:00Z'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingPrompt(null);
    setModalOpen(true);
  };

  const handleEdit = (prompt: Prompt) => {
    setEditingPrompt(prompt);
    setModalOpen(true);
  };

  const handleDelete = async (code: string) => {
    if (!confirm(`Delete prompt "${code}"? This action cannot be undone.`)) return;

    try {
      const response = await authenticatedFetch(`${API_URL}/prompts/${code}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete prompt');

      toast({
        title: "Success",
        description: "Prompt deleted successfully",
      });
      
      loadPrompts();
    } catch (error) {
      console.error('Delete error:', error);
      toast({
        title: "Error", 
        description: "Failed to delete prompt",
        variant: "destructive",
      });
    }
  };

  const handleDuplicate = async (prompt: Prompt) => {
    const newCode = window.prompt(`Enter new code for duplicated prompt:`, `${prompt.code}_copy`);
    if (!newCode || !newCode.trim()) return;

    const duplicateData = {
      ...prompt,
      code: newCode.trim(),
      name: `${prompt.name} (Copy)`,
    };

    try {
      const response = await authenticatedFetch(`${API_URL}/prompts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(duplicateData),
      });

      if (!response.ok) throw new Error('Failed to duplicate prompt');

      toast({
        title: "Success",
        description: "Prompt duplicated successfully",
      });
      
      loadPrompts();
    } catch (error) {
      console.error('Duplicate error:', error);
      toast({
        title: "Error",
        description: "Failed to duplicate prompt",
        variant: "destructive",
      });
    }
  };

  const handleSavePrompt = async (promptData: Partial<Prompt>) => {
    try {
      const url = editingPrompt 
        ? `${API_URL}/prompts/${editingPrompt.code}`
        : `${API_URL}/prompts`;
      
      const method = editingPrompt ? 'PUT' : 'POST';
      
      // Get auth token from localStorage
      const idToken = localStorage.getItem('id_token');
      const headers: HeadersInit = { 'Content-Type': 'application/json' };
      if (idToken) {
        headers['Authorization'] = `Bearer ${idToken}`;
      }
      
      const response = await fetch(url, {
        method,
        headers,
        body: JSON.stringify(promptData),
      });

      if (!response.ok) throw new Error(`Failed to ${editingPrompt ? 'update' : 'create'} prompt`);

      toast({
        title: "Success",
        description: `Prompt ${editingPrompt ? 'updated' : 'created'} successfully`,
      });
      
      setModalOpen(false);
      setEditingPrompt(null);
      loadPrompts();
    } catch (error) {
      console.error('Save error:', error);
      toast({
        title: "Error",
        description: `Failed to ${editingPrompt ? 'update' : 'create'} prompt`,
        variant: "destructive",
      });
    }
  };

  // Filter prompts based on search and category
  const filteredPrompts = prompts.filter(prompt => {
    const matchesSearch = prompt.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         prompt.code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = !selectedCategory || prompt.categories.includes(selectedCategory);
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Prompts Management</h2>
          <p className="text-gray-600 mt-1">Create, edit, and manage AI prompts</p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Create Prompt
        </button>
      </div>

      {/* Search and Filter */}
      <div className="flex gap-4 items-center">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search prompts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent w-full"
          />
        </div>
        
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="pl-10 pr-8 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
          >
            <option value="">All Categories</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat.toUpperCase()}</option>
            ))}
          </select>
        </div>

        <button
          onClick={loadPrompts}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          Refresh
        </button>
      </div>

      {/* Prompts Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-gray-500">Loading prompts...</p>
          </div>
        ) : filteredPrompts.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-gray-500 mb-4">No prompts found</p>
            <button
              onClick={handleCreate}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create Your First Prompt
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Code</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Categories</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Variables</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {(filteredPrompts || []).map((prompt) => (
                  <tr key={prompt.code} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">
                        {prompt.code}
                      </code>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">{prompt.name}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {(prompt.categories || []).map((cat) => (
                          <span
                            key={cat}
                            className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full"
                          >
                            {cat}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-600">
                        {(prompt.variables && prompt.variables.length > 0) ? prompt.variables.join(', ') : 'No variables'}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleEdit(prompt)}
                          className="p-1 text-blue-600 hover:text-blue-900 transition-colors"
                          title="Edit"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDuplicate(prompt)}
                          className="p-1 text-green-600 hover:text-green-900 transition-colors"
                          title="Duplicate"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(prompt.code)}
                          className="p-1 text-red-600 hover:text-red-900 transition-colors"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal */}
      <PromptModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditingPrompt(null);
        }}
        onSave={handleSavePrompt}
        prompt={editingPrompt}
      />
    </div>
  );
};

export default PromptsPanel;