import React, { useState, useEffect } from 'react';
import { ChevronDown, MessageSquare, Search, X, Wand2, Github, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { useIntegrationStore } from '@/store/integration-store';
import { useAuthStore } from '@/store/auth-store';
import { getUserRepositories, suggestRepository, formatRepoName } from '@/lib/github-utils';

interface Prompt {
  code: string;
  name: string;
  categories: string[];
  content: string;
  variables?: string[]; // Make optional since we'll parse from content
  output_folder?: string;
}

interface PromptSelectorProps {
  onPromptSelect?: (prompt: Prompt, variables: Record<string, string>) => void;
  variant?: 'inline' | 'panel';
}

const PromptSelector: React.FC<PromptSelectorProps> = ({ onPromptSelect, variant = 'inline' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [filteredPrompts, setFilteredPrompts] = useState<Prompt[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
  const [variables, setVariables] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [githubRepos, setGithubRepos] = useState<any[]>([]);
  const { toast } = useToast();
  const { isConnected } = useIntegrationStore();
  const { user } = useAuthStore();

  // Use relative URL for API calls - nginx will route to backend
  const API_URL = '/api';

  useEffect(() => {
    if (variant === 'panel' && prompts.length === 0) {
      loadPrompts();
    }
    if (isOpen && prompts.length === 0) {
      loadPrompts();
    }
    if (isOpen && isConnected('github') && githubRepos.length === 0) {
      loadGitHubRepos();
    }
  }, [isOpen, variant]);

  const loadGitHubRepos = async () => {
    try {
      const repos = await getUserRepositories();
      setGithubRepos(repos);
    } catch (error) {
      console.error('Failed to load GitHub repos:', error);
    }
  };

  useEffect(() => {
    // Filter prompts based on search term
    const filtered = prompts.filter(prompt =>
      prompt.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      prompt.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      prompt.categories.some(cat => cat.toLowerCase().includes(searchTerm.toLowerCase()))
    );
    setFilteredPrompts(filtered);
  }, [prompts, searchTerm]);

  // Parse variables from prompt content
  const parseVariables = (content: string): string[] => {
    const matches = content.match(/\{\{(\w+)\}\}/g);
    if (!matches) return [];

    const variables = matches.map(match => match.replace(/\{\{|\}\}/g, ''));
    return [...new Set(variables)]; // Remove duplicates
  };

  const loadPrompts = async () => {

    setLoading(true);
    try {
      // Add timeout to prevent hanging requests
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      // Get user email from localStorage if available
      let userEmail = user?.email;
      if (!userEmail) {
        try {
          const userData = localStorage.getItem('user');
          if (userData) {
            const parsed = JSON.parse(userData);
            userEmail = parsed.email;
          }
        } catch (e) {
          console.error('Error parsing user data:', e);
        }
      }

      // Build URL with user_email parameter for role-based filtering
      const url = userEmail
        ? `${API_URL}/prompts?user_email=${encodeURIComponent(userEmail)}`
        : `${API_URL}/prompts`;

      // Get auth token for API request
      const idToken = localStorage.getItem('id_token');
      const headers: HeadersInit = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      };
      if (idToken) {
        headers['Authorization'] = `Bearer ${idToken}`;
      }

      const response = await fetch(url, {
        signal: controller.signal,
        headers,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      const processedPrompts = (data.prompts || []).map((prompt: any) => ({
        ...prompt,
        variables: parseVariables(prompt.content || '')
      }));
      
      setPrompts(processedPrompts);
      
      if (processedPrompts.length === 0) {
        console.info('No prompts found in database');
        toast({
          title: "No Prompts",
          description: "No prompts found in database. Create some in Admin Panel.",
        });
      }
    } catch (error) {
      // Enhanced error handling with specific error types
      let errorMessage = 'Unknown error';
      let userMessage = 'Backend connection failed';

      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorMessage = 'Connection timeout (10s)';
          userMessage = 'Backend connection timeout. Please check if backend is running.';
        } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
          errorMessage = 'Network error - backend not reachable';
          userMessage = 'Cannot reach backend server. Running in demo mode.';
        } else if (error.message.includes('CORS')) {
          errorMessage = 'CORS policy error';
          userMessage = 'Backend CORS configuration issue. Contact admin.';
        } else {
          errorMessage = error.message;
          userMessage = error.message;
        }
      }

      // Only log actual errors, not expected demo mode
      if (!errorMessage.includes('demo') && !errorMessage.includes('not configured')) {
        console.warn('Prompts loading failed:', errorMessage, '- Using demo mode');
      }
      
      // Load demo data with user notification
      loadDemoPrompts(userMessage);
    } finally {
      setLoading(false);
    }
  };

  const loadDemoPrompts = (errorMessage?: string) => {
    // Demo data for development
    const demoPrompts = [
        {
          code: 'demo_hr_contract',
          name: 'HR Contract Generator',
          categories: ['hr'],
          content: 'Generate a {{contract_type}} contract for {{employee_name}} in the {{position}} role with salary {{salary}}.',
        },
        {
          code: 'demo_code_review',
          name: 'Code Review Assistant', 
          categories: ['dev', 'tech_lead'],
          content: 'Please review this {{language}} code for {{project_name}}:\n\n{{code_snippet}}\n\nFocus on: {{review_focus}}',
        },
        {
          code: 'demo_git_scan',
          name: 'Git Repository Scanner',
          categories: ['dev', 'pm'],
          content: 'Scan the Git repository {{repo_url}} for changes in the last {{time_period}}. Focus on {{scan_focus}}.',
        },
        {
          code: 'demo_meeting_summary',
          name: 'Meeting Summary',
          categories: ['pm', 'all'],
          content: 'Create a summary of the meeting about {{meeting_topic}} held on {{date}} with {{participants}}. Key decisions: {{decisions}}',
        }
    ].map(prompt => ({
      ...prompt,
      variables: parseVariables(prompt.content)
    }));
    
    setPrompts(demoPrompts);
    
    // Only show error toast if there was an actual error (not just demo mode)
    if (errorMessage) {
      toast({
        title: "Demo Mode",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  const handlePromptClick = (prompt: Prompt) => {
    setSelectedPrompt(prompt);
    
    // Initialize variables with auto-fill suggestions
    const initialVariables: Record<string, string> = {};
    prompt.variables?.forEach(variable => {
      // Auto-fill GitHub repository URLs if GitHub is connected
      if (isConnected('github') && githubRepos.length > 0) {
        const suggestion = suggestRepository(variable, githubRepos);
        initialVariables[variable] = suggestion;
      } else {
        initialVariables[variable] = '';
      }
    });
    setVariables(initialVariables);
  };

  const handleVariableChange = (variable: string, value: string) => {
    setVariables(prev => ({
      ...prev,
      [variable]: value
    }));
  };

  const handleUsePrompt = () => {
    if (!selectedPrompt) return;

    // Check if all required variables are filled
    const requiredVariables = selectedPrompt.variables || [];
    const missingVariables = requiredVariables.filter(v => !variables[v] || !variables[v].trim());
    
    if (missingVariables.length > 0) {
      toast({
        title: "Missing Variables",
        description: `Please fill: ${missingVariables.join(', ')}`,
        variant: "destructive",
      });
      return;
    }

    if (onPromptSelect) {
      onPromptSelect(selectedPrompt, variables);
    }
    setIsOpen(false);
    setSelectedPrompt(null);
    setVariables({});
  };

  const isGitHubVariable = (variable: string): boolean => {
    const gitVarNames = ['repo_url', 'repository', 'project_url', 'git_url'];
    return gitVarNames.some(name => variable.toLowerCase().includes(name));
  };

  const getRepositoryOptions = (variable: string) => {
    if (!isGitHubVariable(variable) || githubRepos.length === 0) return [];
    return githubRepos.slice(0, 5); // Limit to 5 options
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      hr: 'bg-pink-100 text-pink-800',
      dev: 'bg-blue-100 text-blue-800', 
      qa: 'bg-green-100 text-green-800',
      pm: 'bg-purple-100 text-purple-800',
      ba: 'bg-orange-100 text-orange-800',
      tech_lead: 'bg-indigo-100 text-indigo-800',
      devops: 'bg-gray-100 text-gray-800',
      finance: 'bg-yellow-100 text-yellow-800',
      admin: 'bg-red-100 text-red-800',
      all: 'bg-emerald-100 text-emerald-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  // Panel variant - display as list
  if (variant === 'panel') {
    return (
      <div className="space-y-3">
        {/* Search box */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search prompts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-input bg-background rounded-md text-sm focus:ring-2 focus:ring-ring focus:border-transparent"
          />
        </div>

        {/* Prompts list */}
        {loading ? (
          <div className="p-4 text-center text-muted-foreground text-sm">
            Loading prompts...
          </div>
        ) : filteredPrompts.length === 0 ? (
          <div className="p-4 text-center text-muted-foreground text-sm">
            {searchTerm ? 'No prompts found matching your search' : 'No prompts available'}
          </div>
        ) : (
          <div className="max-h-[400px] overflow-y-auto space-y-1 pr-1">
            {filteredPrompts.map(prompt => (
              <Button
                key={prompt.code}
                variant="ghost"
                onClick={() => handlePromptClick(prompt)}
                className="w-full justify-start text-left h-auto py-3 px-3 hover:bg-accent"
              >
                <div className="flex-1">
                  <div className="font-medium text-sm mb-1">{prompt.name}</div>
                  <div className="flex flex-wrap gap-1">
                    {(prompt.categories || []).slice(0, 2).map(category => (
                      <span
                        key={category}
                        className={`px-2 py-0.5 text-xs rounded-full ${getCategoryColor(category)}`}
                      >
                        {category}
                      </span>
                    ))}
                  </div>
                </div>
              </Button>
            ))}
          </div>
        )}
        
        {/* Variable form modal for panel variant */}
        {selectedPrompt && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[80vh] overflow-y-auto">
              <div className="p-4 border-b flex items-center justify-between">
                <h3 className="font-semibold">{selectedPrompt.name}</h3>
                <button
                  onClick={() => {
                    setSelectedPrompt(null);
                    setVariables({});
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="p-4 space-y-3">
                {(selectedPrompt.variables || []).map(variable => {
                  const repoOptions = getRepositoryOptions(variable);
                  const isGitVar = isGitHubVariable(variable);
                  
                  return (
                    <div key={variable}>
                      <label className="block text-xs font-medium text-gray-700 mb-1 flex items-center gap-1">
                        {variable.replace(/_/g, ' ')}
                        {isGitVar && isConnected('github') && (
                          <Github className="w-3 h-3 text-green-600" />
                        )}
                      </label>
                      
                      {repoOptions.length > 0 ? (
                        <select
                          value={variables[variable] || ''}
                          onChange={(e) => handleVariableChange(variable, e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="">Select repository...</option>
                          {repoOptions.map((repo) => (
                            <option key={repo.html_url} value={repo.html_url}>
                              {formatRepoName(repo.full_name)}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <input
                          type="text"
                          placeholder={`Enter ${variable.replace(/_/g, ' ')}...`}
                          value={variables[variable] || ''}
                          onChange={(e) => handleVariableChange(variable, e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      )}
                    </div>
                  );
                })}
              </div>
              
              <div className="p-4 border-t bg-gray-50 flex gap-2">
                <Button
                  onClick={handleUsePrompt}
                  className="flex-1"
                >
                  Use Template
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setSelectedPrompt(null);
                    setVariables({});
                  }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Inline variant - button with dropdown
  return (
    <div className="relative">
      <Button
        variant="outline"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-sm"
        size="sm"
      >
        <Wand2 className="w-4 h-4" />
        Use Prompt
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </Button>

      {isOpen && (
        <div className="absolute bottom-full right-0 mb-2 w-96 max-h-[500px] bg-white border border-gray-200 rounded-lg shadow-lg z-50">
          <div className="p-4 border-b">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-medium text-gray-900 flex items-center gap-2">
                <MessageSquare className="w-4 h-4" />
                Select Prompt Template
              </h3>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search prompts..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div className="max-h-60 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center text-gray-500">
                Loading prompts...
              </div>
            ) : filteredPrompts.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                {searchTerm ? 'No prompts found' : 'No prompts available'}
              </div>
            ) : (
              filteredPrompts.map(prompt => (
                <button
                  key={prompt.code}
                  onClick={() => handlePromptClick(prompt)}
                  className={`w-full p-3 text-left hover:bg-gray-50 border-b border-gray-100 transition-colors ${
                    selectedPrompt?.code === prompt.code ? 'bg-blue-50 border-blue-200' : ''
                  }`}
                >
                  <div className="font-medium text-sm text-gray-900 mb-1">
                    {prompt.name}
                  </div>
                  <div className="flex flex-wrap gap-1 mb-2">
                    {(prompt.categories || []).map(category => (
                      <span
                        key={category}
                        className={`px-2 py-0.5 text-xs rounded-full ${getCategoryColor(category)}`}
                      >
                        {category}
                      </span>
                    ))}
                  </div>
                  <div className="text-xs text-gray-500">
                    Variables: {(prompt.variables?.length || 0) > 0 ? prompt.variables!.join(', ') : 'None'}
                  </div>
                </button>
              ))
            )}
          </div>

          {selectedPrompt && (
            <div className="p-4 border-t bg-gray-50">
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium text-sm text-gray-900 mb-2">
                    Fill Variables for: {selectedPrompt.name}
                  </h4>
                </div>

{(selectedPrompt.variables || []).map(variable => {
                  const repoOptions = getRepositoryOptions(variable);
                  const isGitVar = isGitHubVariable(variable);
                  
                  return (
                    <div key={variable}>
                      <label className="block text-xs font-medium text-gray-700 mb-1 flex items-center gap-1">
                        {variable.replace(/_/g, ' ')}
                        {isGitVar && isConnected('github') && (
                          <Github className="w-3 h-3 text-green-600" />
                        )}
                      </label>
                      
                      {repoOptions.length > 0 ? (
                        <div className="space-y-1">
                          <select
                            value={variables[variable] || ''}
                            onChange={(e) => handleVariableChange(variable, e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          >
                            <option value="">Select repository...</option>
                            {repoOptions.map((repo) => (
                              <option key={repo.html_url} value={repo.html_url}>
                                {formatRepoName(repo.full_name)} - {repo.description || 'No description'}
                              </option>
                            ))}
                          </select>
                          <input
                            type="text"
                            placeholder="Or enter custom URL..."
                            value={variables[variable] || ''}
                            onChange={(e) => handleVariableChange(variable, e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>
                      ) : (
                        <div className="relative">
                          <input
                            type="text"
                            placeholder={`Enter ${variable.replace(/_/g, ' ')}...`}
                            value={variables[variable] || ''}
                            onChange={(e) => handleVariableChange(variable, e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                          {isGitVar && !isConnected('github') && (
                            <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
                              <ExternalLink className="w-4 h-4 text-gray-400" />
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}

                <div className="flex gap-2 mt-4">
                  <Button
                    size="sm"
                    onClick={handleUsePrompt}
                    className="flex-1"
                  >
                    Use This Prompt
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setSelectedPrompt(null);
                      setVariables({});
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PromptSelector;