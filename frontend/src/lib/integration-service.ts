import { callBackendAPI } from './auth-utils';

// Type definitions for integration responses
export interface JiraIssue {
  key: string;
  summary: string;
  status: string;
  priority: string;
  assignee: string;
  updated: string;
  url: string;
}

export interface GitHubPullRequest {
  repo: string;
  title: string;
  number: number;
  state: string;
  updated_at: string;
  url: string;
}

export interface GitHubCommit {
  author: string;
  message: string;
  date: string;
  url: string;
  sha: string;
}

export interface DriveFile {
  id: string;
  name: string;
  mimeType: string;
  webViewLink: string;
  modifiedTime: string;
  size?: string;
}

export interface IntegrationServiceError extends Error {
  provider: string;
  action: string;
  code?: string;
}

class IntegrationService {
  private createError(provider: string, action: string, message: string, code?: string): IntegrationServiceError {
    const error = new Error(message) as IntegrationServiceError;
    error.provider = provider;
    error.action = action;
    error.code = code;
    return error;
  }

  // Jira Integration Methods
  async getMyAssignedJiraIssues(limit: number = 10, idToken?: string): Promise<JiraIssue[]> {
    try {
      console.log('Fetching Jira issues from backend API');
      
      const response = await callBackendAPI('/integrations/jira/my-issues', {
        method: 'GET'
      }, idToken);
      
      if (response.success && response.data) {
        return this.transformJiraIssues(response.data.slice(0, limit));
      }
      
      throw new Error('Failed to fetch Jira issues');
    } catch (error) {
      console.error('Error fetching Jira issues:', error);
      console.log('Falling back to demo mode');
      return this.getMockJiraIssues(limit);
    }
  }

  // GitHub Integration Methods  
  async getMyOpenPRs(limit: number = 10, idToken?: string): Promise<GitHubPullRequest[]> {
    try {
      console.log('Fetching GitHub PRs from backend API');
      
      const response = await callBackendAPI('/integrations/github/my-prs', {
        method: 'GET'
      }, idToken);
      
      if (response.success && response.data) {
        return this.transformGitHubPRs(response.data.slice(0, limit));
      }
      
      throw new Error('Failed to fetch GitHub PRs');
    } catch (error) {
      console.error('Error fetching GitHub PRs:', error);
      console.log('Falling back to demo mode');
      return this.getMockGitHubPRs(limit);
    }
  }

  async getRepoChangelog(repo: string, since: string = '7d', idToken?: string): Promise<GitHubCommit[]> {
    try {
      console.log(`Fetching ${repo} changelog from backend API`);
      
      const response = await callBackendAPI(`/integrations/github/repo-changelog?repo=${encodeURIComponent(repo)}&since=${since}`, {
        method: 'GET'
      }, idToken);
      
      if (response.success && response.data) {
        return this.transformGitHubCommits(response.data);
      }
      
      throw new Error('Failed to fetch repo changelog');
    } catch (error) {
      console.error('Error fetching repo changelog:', error);
      console.log('Falling back to demo mode');
      return this.getMockGitHubCommits(repo);
    }
  }

  // Natural Language Intent Processing
  async processIntent(message: string): Promise<{
    action?: string;
    provider?: string;
    parameters?: any;
    confidence: number;
  }> {
    const normalizedMessage = message.toLowerCase().trim();
    
    // Simple intent matching - in production, this could use AI
    const intents = [
      {
        patterns: [/show.*jira.*ticket/, /my.*jira.*issue/, /assigned.*issue/],
        action: 'myAssignedIssues',
        provider: 'jira',
        confidence: 0.9
      },
      {
        patterns: [/my.*pull.*request/, /open.*pr/, /github.*pr/],
        action: 'myOpenPRs',
        provider: 'github',
        confidence: 0.9
      },
      {
        patterns: [/what.*changed/, /repo.*changelog/, /recent.*commit/],
        action: 'repoChangelog',
        provider: 'github',
        confidence: 0.8,
        requiresRepo: true
      }
    ];

    for (const intent of intents) {
      for (const pattern of intent.patterns) {
        if (pattern.test(normalizedMessage)) {
          const result: any = {
            action: intent.action,
            provider: intent.provider,
            confidence: intent.confidence
          };

          // Extract repository if needed
          if (intent.requiresRepo) {
            const repoMatch = normalizedMessage.match(/(\w+\/\w+)/);
            if (repoMatch) {
              result.parameters = { repo: repoMatch[1] };
            } else {
              result.confidence = 0.5; // Lower confidence if repo not found
              result.needsRepo = true;
            }
          }

          return result;
        }
      }
    }

    return { confidence: 0 };
  }

  // Data transformation methods
  private transformJiraIssues(rawIssues: any[]): JiraIssue[] {
    return rawIssues.map(issue => ({
      key: issue.key,
      summary: issue.fields?.summary || issue.summary,
      status: issue.fields?.status?.name || issue.status,
      priority: issue.fields?.priority?.name || issue.priority || 'Medium',
      assignee: issue.fields?.assignee?.displayName || issue.assignee || 'Unassigned',
      updated: issue.fields?.updated || issue.updated,
      url: `https://your-company.atlassian.net/browse/${issue.key}`
    }));
  }

  private transformGitHubPRs(rawPRs: any[]): GitHubPullRequest[] {
    return rawPRs.map(pr => ({
      repo: pr.base?.repo?.full_name || pr.repo,
      title: pr.title,
      number: pr.number,
      state: pr.state,
      updated_at: pr.updated_at,
      url: pr.html_url
    }));
  }

  private transformGitHubCommits(rawCommits: any[]): GitHubCommit[] {
    return rawCommits.map(commit => ({
      author: commit.commit?.author?.name || commit.author,
      message: commit.commit?.message || commit.message,
      date: commit.commit?.author?.date || commit.date,
      url: commit.html_url,
      sha: commit.sha
    }));
  }

  // Mock data for demo purposes
  private getMockJiraIssues(limit: number): JiraIssue[] {
    const mockIssues = [
      {
        key: 'AAP-123',
        summary: 'Implement user authentication system',
        status: 'In Progress',
        priority: 'High',
        assignee: 'John Doe',
        updated: '2024-01-15T10:30:00Z',
        url: 'https://aap-company.atlassian.net/browse/AAP-123'
      },
      {
        key: 'AAP-124',
        summary: 'Fix login redirect issue',
        status: 'To Do',
        priority: 'Medium',
        assignee: 'Jane Smith',
        updated: '2024-01-15T09:15:00Z',
        url: 'https://aap-company.atlassian.net/browse/AAP-124'
      },
      {
        key: 'AAP-125',
        summary: 'Add integration testing',
        status: 'In Review',
        priority: 'Low',
        assignee: 'Bob Wilson',
        updated: '2024-01-14T16:45:00Z',
        url: 'https://aap-company.atlassian.net/browse/AAP-125'
      }
    ];

    return mockIssues.slice(0, limit);
  }

  private getMockGitHubPRs(limit: number): GitHubPullRequest[] {
    const mockPRs = [
      {
        repo: 'company/aap-frontend',
        title: 'Add OAuth integration',
        number: 42,
        state: 'open',
        updated_at: '2024-01-15T11:20:00Z',
        url: 'https://github.com/company/aap-frontend/pull/42'
      },
      {
        repo: 'company/aap-backend',
        title: 'Fix API rate limiting',
        number: 38,
        state: 'open',
        updated_at: '2024-01-14T14:30:00Z',
        url: 'https://github.com/company/aap-backend/pull/38'
      }
    ];

    return mockPRs.slice(0, limit);
  }

  private getMockGitHubCommits(repo: string): GitHubCommit[] {
    return [
      {
        author: 'Alice Johnson',
        message: 'feat: add user profile management',
        date: '2024-01-15T13:45:00Z',
        url: `https://github.com/${repo}/commit/abc123`,
        sha: 'abc123'
      },
      {
        author: 'Charlie Brown',
        message: 'fix: resolve authentication timeout',
        date: '2024-01-14T16:20:00Z',
        url: `https://github.com/${repo}/commit/def456`,
        sha: 'def456'
      },
      {
        author: 'Diana Lee',
        message: 'docs: update API documentation',
        date: '2024-01-13T10:15:00Z',
        url: `https://github.com/${repo}/commit/ghi789`,
        sha: 'ghi789'
      }
    ];
  }
}

// Export singleton instance
export const integrationService = new IntegrationService();