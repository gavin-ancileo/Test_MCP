import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { Prompt } from './PromptsPanel';

interface PromptModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (promptData: Partial<Prompt>) => void;
  prompt?: Prompt | null;
}

const PromptModal: React.FC<PromptModalProps> = ({ isOpen, onClose, onSave, prompt }) => {
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    categories: [] as string[],
    content: '',
    output_folder: ''
  });

  const [detectedVariables, setDetectedVariables] = useState<string[]>([]);

  const categories = ['hr', 'dev', 'qa', 'pm', 'ba', 'tech_lead', 'devops', 'finance', 'cybersecurity', 'support', 'admin', 'all'];

  useEffect(() => {
    if (prompt) {
      setFormData({
        code: prompt.code,
        name: prompt.name,
        categories: prompt.categories,
        content: prompt.content,
        output_folder: prompt.output_folder || ''
      });
    } else {
      setFormData({
        code: '',
        name: '',
        categories: [],
        content: '',
        output_folder: ''
      });
    }
  }, [prompt]);

  useEffect(() => {
    // Detect variables in content
    const matches = formData.content.match(/\{\{(\w+)\}\}/g) || [];
    const variables = [...new Set(matches.map(match => match.replace(/\{\{|\}\}/g, '')))];
    setDetectedVariables(variables);
  }, [formData.content]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const promptData = {
      ...formData,
      variables: detectedVariables
    };
    
    onSave(promptData);
  };

  const toggleCategory = (category: string) => {
    setFormData(prev => ({
      ...prev,
      categories: prev.categories.includes(category)
        ? prev.categories.filter(c => c !== category)
        : [...prev.categories, category]
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-bold">
            {prompt ? 'Edit Prompt' : 'Create New Prompt'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Code */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Prompt Code *
            </label>
            <input
              type="text"
              required
              pattern="[a-z0-9_]+"
              placeholder="e.g., hr_contract_generate"
              value={formData.code}
              onChange={(e) => setFormData(prev => ({ ...prev, code: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={!!prompt} // Disable editing code for existing prompts
            />
            <p className="text-xs text-gray-500 mt-1">Lowercase letters, numbers, and underscores only</p>
          </div>

          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Prompt Name *
            </label>
            <input
              type="text"
              required
              placeholder="e.g., HR Contract Generator"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Categories */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Categories/Roles
            </label>
            <div className="grid grid-cols-3 md:grid-cols-4 gap-2">
              {categories.map(category => (
                <button
                  key={category}
                  type="button"
                  onClick={() => toggleCategory(category)}
                  className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                    formData.categories.includes(category)
                      ? 'bg-blue-100 border-blue-300 text-blue-800'
                      : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {category.toUpperCase()}
                </button>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-1">Select which roles can use this prompt</p>
          </div>

          {/* Output Folder */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Output Folder (Google Drive)
            </label>
            <input
              type="text"
              placeholder="drive://folder/1ViGWBhDzjbNit-oy0YTMaB8PSke8PVrs"
              value={formData.output_folder}
              onChange={(e) => setFormData(prev => ({ ...prev, output_folder: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">Google Drive folder URL for document output</p>
          </div>

          {/* Content */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Prompt Content *
            </label>
            <textarea
              required
              rows={12}
              placeholder="Enter your prompt content here...&#10;&#10;Example:&#10;Generate a {{document_type}} for {{client_name}} with the following requirements:&#10;- Project: {{project_name}}&#10;- Timeline: {{timeline}}&#10;- Budget: {{budget}}"
              value={formData.content}
              onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
            />
            <p className="text-xs text-gray-500 mt-1">Use {"{{variable}}"} for dynamic values</p>
          </div>

          {/* Detected Variables */}
          {detectedVariables.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="text-sm font-medium text-blue-900 mb-2">Detected Variables:</h4>
              <div className="flex flex-wrap gap-2">
                {detectedVariables.map(variable => (
                  <code key={variable} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                    {"{{"}{variable}{"}}"}
                  </code>
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              {prompt ? 'Save Changes' : 'Create Prompt'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PromptModal;