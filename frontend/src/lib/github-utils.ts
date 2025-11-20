// GitHub utilities for auto-filling repository URLs
import { authenticatedFetch } from './auth-utils';

interface GitHubRepo {
  name: string;
  full_name: string;
  html_url: string;
  description?: string;
  updated_at: string;
  private: boolean;
}

// Mock GitHub repositories for demo
const mockRepositories: GitHubRepo[] = [
  {
    name: 'aap-frontend',
    full_name: 'company/aap-frontend',
    html_url: 'https://github.com/company/aap-frontend',
    description: 'AAP Frontend Application',
    updated_at: '2024-01-15T10:30:00Z',
    private: false
  },
  {
    name: 'aap-backend',
    full_name: 'company/aap-backend',
    html_url: 'https://github.com/company/aap-backend',
    description: 'AAP Backend API',
    updated_at: '2024-01-14T15:20:00Z',
    private: true
  },
  {
    name: 'docs',
    full_name: 'company/docs',
    html_url: 'https://github.com/company/docs',
    description: 'Project Documentation',
    updated_at: '2024-01-12T09:15:00Z',
    private: false
  }
];

export async function getUserRepositories(): Promise<GitHubRepo[]> {
  try {
    // In production, this would call the backend API
    // For now, return mock data
    const API_URL = import.meta.env.VITE_AGENTCORE_URL;
    
    if (API_URL) {
      try {
        const response = await authenticatedFetch(`${API_URL}/integrations/github/my-repos`);
        if (response.ok) {
          const data = await response.json();
          return data.repositories || mockRepositories;
        }
      } catch (error) {
        console.log('GitHub API not available, using demo data');
      }
    }
    
    // Return mock data for demo
    return mockRepositories;
  } catch (error) {
    console.error('Error fetching repositories:', error);
    return mockRepositories;
  }
}

export function getRepositoryUrl(repoName: string, repositories: GitHubRepo[]): string {
  const repo = repositories.find(r => 
    r.name === repoName || 
    r.full_name === repoName ||
    r.name.toLowerCase().includes(repoName.toLowerCase())
  );
  
  return repo?.html_url || '';
}

export function suggestRepository(variableName: string, repositories: GitHubRepo[]): string {
  // Smart suggestions based on variable names
  const suggestions: Record<string, string[]> = {
    'repo_url': repositories.map(r => r.html_url),
    'repository': repositories.map(r => r.html_url),
    'project_url': repositories.map(r => r.html_url),
    'git_url': repositories.map(r => r.html_url),
    'frontend': repositories.filter(r => r.name.includes('frontend')).map(r => r.html_url),
    'backend': repositories.filter(r => r.name.includes('backend')).map(r => r.html_url),
    'api': repositories.filter(r => r.name.includes('api')).map(r => r.html_url),
    'docs': repositories.filter(r => r.name.includes('doc')).map(r => r.html_url),
  };

  const normalizedVar = variableName.toLowerCase();
  
  // Find best match
  for (const [key, urls] of Object.entries(suggestions)) {
    if (normalizedVar.includes(key) && urls.length > 0) {
      return urls[0]; // Return first match
    }
  }
  
  // Default to first repo if no specific match
  return repositories.length > 0 ? repositories[0].html_url : '';
}

export function formatRepoName(fullName: string): string {
  return fullName.split('/').pop() || fullName;
}