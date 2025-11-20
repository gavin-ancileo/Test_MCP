import React, { useState, useEffect } from 'react';
import { Play, RefreshCw } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Prompt } from './PromptsPanel';
import { authenticatedFetch } from '@/lib/auth-utils';

const TestPanel: React.FC = () => {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
  const [variables, setVariables] = useState<Record<string, string>>({});
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [model, setModel] = useState('gpt-4');
  const { toast } = useToast();

  const API_URL = import.meta.env.VITE_AGENTCORE_URL || 'http://localhost:8000/api';

  useEffect(() => {
    loadPrompts();
  }, []);

  const loadPrompts = async () => {
    if (!API_URL || API_URL === 'http://localhost:8000/api') {
      console.info('Backend not configured for test panel');
      loadDemoPrompts();
      return;
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      const response = await authenticatedFetch(`${API_URL}/prompts`, {
        signal: controller.signal,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });

      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setPrompts(data.prompts || []);
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

      console.warn('Test panel prompts loading failed:', errorMessage, '- Using demo prompts');
      loadDemoPrompts();
    }
  };

  const loadDemoPrompts = () => {
    // Demo data for development
    setPrompts([
        {
          code: 'demo_hr_contract',
          name: 'HR Contract Generator',
          categories: ['hr'],
          content: 'Generate a {{contract_type}} contract for {{employee_name}} in the {{position}} role with salary {{salary}}.',
          variables: ['contract_type', 'employee_name', 'position', 'salary']
        }
      ]);
  };

  const handlePromptSelect = (promptCode: string) => {
    const prompt = prompts.find(p => p.code === promptCode);
    if (prompt) {
      setSelectedPrompt(prompt);
      
      // Initialize variables
      const initialVariables: Record<string, string> = {};
      prompt.variables.forEach(variable => {
        initialVariables[variable] = '';
      });
      setVariables(initialVariables);
      setOutput('');
    }
  };

  const handleVariableChange = (variable: string, value: string) => {
    setVariables(prev => ({
      ...prev,
      [variable]: value
    }));
  };

  const runTest = async () => {
    if (!selectedPrompt) {
      toast({
        title: "Error",
        description: "Please select a prompt first",
        variant: "destructive",
      });
      return;
    }

    // Check if all variables are filled
    const missingVariables = selectedPrompt.variables.filter(v => !variables[v] || !variables[v].trim());
    if (missingVariables.length > 0) {
      toast({
        title: "Error", 
        description: `Please fill all variables: ${missingVariables.join(', ')}`,
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    setOutput('Processing prompt and generating response...\n\n');

    try {
      const response = await authenticatedFetch(`${API_URL}/test-prompt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt_code: selectedPrompt.code,
          variables: variables,
          model: model,
          generate_document: true
        }),
      });

      if (!response.ok) throw new Error('Failed to test prompt');

      const data = await response.json();
      
      if (data.success) {
        let outputText = `Prompt Test Results:\n\n`;
        outputText += `Prompt: ${data.prompt_name || selectedPrompt.name}\n`;
        outputText += `Model: ${model}\n\n`;
        outputText += `Variables Used:\n`;
        Object.entries(variables).forEach(([key, value]) => {
          outputText += `  ${key}: ${value}\n`;
        });
        outputText += `\n${'='.repeat(50)}\n\n`;
        outputText += `Generated Content:\n${data.filled_content}\n\n`;
        
        if (data.ai_response) {
          outputText += `${'='.repeat(50)}\nAI Analysis:\n${data.ai_response}\n\n`;
        }
        
        if (data.document_uploaded && data.document_url) {
          outputText += `✅ SUCCESS: Document uploaded to Google Drive!\n`;
          outputText += `📄 Drive Link: ${data.document_url}\n\n`;
        } else if (data.drive_error) {
          outputText += `⚠️  Content generated but Drive upload failed: ${data.drive_error}\n\n`;
        }

        setOutput(outputText);
        
        toast({
          title: "Success",
          description: "Prompt test completed successfully",
        });
      } else {
        throw new Error(data.error || 'Unknown error');
      }
    } catch (error) {
      console.error('Test error:', error);
      
      // Fallback: Show basic filled content
      let content = selectedPrompt.content;
      Object.entries(variables).forEach(([key, value]) => {
        content = content.replace(new RegExp(`{{${key}}}`, 'g'), value);
      });
      
      const outputText = `⚠️ Backend not available - Showing filled content only:\n\n${content}\n\nTo test with AI and document generation, ensure backend is running at:\n${API_URL}`;
      
      setOutput(outputText);
      
      toast({
        title: "Demo Mode",
        description: "Backend not available. Showing filled content only.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Test Prompts</h2>
        <p className="text-gray-600 mt-1">Test prompts with variables and AI models</p>
      </div>

      {/* Prompt Selection */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Prompt
          </label>
          <select
            value={selectedPrompt?.code || ''}
            onChange={(e) => handlePromptSelect(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">-- Select a prompt to test --</option>
            {(prompts || []).map(prompt => (
              <option key={prompt.code} value={prompt.code}>
                {prompt.name} ({prompt.code})
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={loadPrompts}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh Prompts
        </button>
      </div>

      {/* Variables Input */}
      {selectedPrompt && selectedPrompt.variables && selectedPrompt.variables.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Variables</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {(selectedPrompt.variables || []).map(variable => (
              <div key={variable}>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {variable}
                </label>
                <input
                  type="text"
                  placeholder={`Enter ${variable}`}
                  value={variables[variable] || ''}
                  onChange={(e) => handleVariableChange(variable, e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Test Configuration */}
      {selectedPrompt && (
        <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Test Configuration</h3>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              AI Model
            </label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full max-w-xs px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="gpt-4">GPT-4 (Recommended)</option>
              <option value="gpt-4-turbo">GPT-4 Turbo</option>
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            </select>
          </div>

          <button
            onClick={runTest}
            disabled={loading || !selectedPrompt}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Play className="w-4 h-4" />
            {loading ? 'Testing...' : 'Run Test'}
          </button>
        </div>
      )}

      {/* Output */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Output</h3>
        <div className="bg-gray-50 rounded-lg p-4 min-h-[400px] font-mono text-sm whitespace-pre-wrap overflow-auto">
          {output || 'Select a prompt and click "Run Test" to see results...'}
        </div>
      </div>
    </div>
  );
};

export default TestPanel;