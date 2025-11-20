import React, { useState } from 'react';
import {
  Zap,
  Github,
  ExternalLink,
  Loader2,
  AlertCircle,
  Clock,
  GitPullRequest,
  Bug,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { useIntegrationStore } from '@/store/integration-store';
import { integrationService, JiraIssue, GitHubPullRequest, GitHubCommit } from '@/lib/integration-service';
import { useToast } from '@/hooks/use-toast';
import IntegrationStatus from './IntegrationStatus';

interface ChatShortcutsProps {
  onInsertMessage: (message: string) => void;
}

export default function ChatShortcuts({ onInsertMessage }: ChatShortcutsProps) {
  const { toast } = useToast();
  const { isConnected } = useIntegrationStore();
  const [loading, setLoading] = useState<string | null>(null);
  const [repoInput, setRepoInput] = useState('');
  const [showRepoDialog, setShowRepoDialog] = useState(false);

  const shortcuts = [
    {
      id: 'jira-issues',
      title: 'My Jira Issues',
      description: 'Show my assigned tickets (top 10)',
      icon: Bug,
      provider: 'jira' as const,
      action: () => handleJiraIssues(),
    },
    {
      id: 'github-prs',
      title: 'My Open PRs',
      description: 'Show my pull requests (last 10)',
      icon: GitPullRequest,
      provider: 'github' as const,
      action: () => handleGitHubPRs(),
    },
    {
      id: 'repo-changelog',
      title: 'Repo Changelog',
      description: 'Recent commits (last 7 days)',
      icon: Clock,
      provider: 'github' as const,
      action: () => handleRepoChangelog(),
    },
  ];

  const handleJiraIssues = async () => {
    if (!isConnected('jira')) {
      toast({
        title: 'Jira Not Connected',
        description: 'Please connect your Jira account first.',
        variant: 'destructive',
      });
      return;
    }

    setLoading('jira-issues');
    try {
      const issues = await integrationService.getMyAssignedJiraIssues(10);
      const message = formatJiraIssuesForChat(issues);
      onInsertMessage(message);
      toast({
        title: 'Jira Issues Loaded',
        description: `Found ${issues.length} assigned issues`,
      });
    } catch (error) {
      toast({
        title: 'Failed to Load Issues',
        description: (error as Error).message,
        variant: 'destructive',
      });
    } finally {
      setLoading(null);
    }
  };

  const handleGitHubPRs = async () => {
    if (!isConnected('github')) {
      toast({
        title: 'GitHub Not Connected',
        description: 'Please connect your GitHub account first.',
        variant: 'destructive',
      });
      return;
    }

    setLoading('github-prs');
    try {
      const prs = await integrationService.getMyOpenPRs(10);
      const message = formatGitHubPRsForChat(prs);
      onInsertMessage(message);
      toast({
        title: 'GitHub PRs Loaded',
        description: `Found ${prs.length} open pull requests`,
      });
    } catch (error) {
      toast({
        title: 'Failed to Load PRs',
        description: (error as Error).message,
        variant: 'destructive',
      });
    } finally {
      setLoading(null);
    }
  };

  const handleRepoChangelog = () => {
    if (!isConnected('github')) {
      toast({
        title: 'GitHub Not Connected',
        description: 'Please connect your GitHub account first.',
        variant: 'destructive',
      });
      return;
    }

    setShowRepoDialog(true);
  };

  const handleRepoChangelogSubmit = async () => {
    if (!repoInput.trim()) {
      toast({
        title: 'Repository Required',
        description: 'Please enter a repository name (owner/repo)',
        variant: 'destructive',
      });
      return;
    }

    setLoading('repo-changelog');
    setShowRepoDialog(false);
    
    try {
      const commits = await integrationService.getRepoChangelog(repoInput.trim(), '7d');
      const message = formatRepoChangelogForChat(commits, repoInput.trim());
      onInsertMessage(message);
      toast({
        title: 'Repository Changelog Loaded',
        description: `Found ${commits.length} recent commits`,
      });
      setRepoInput('');
    } catch (error) {
      toast({
        title: 'Failed to Load Changelog',
        description: (error as Error).message,
        variant: 'destructive',
      });
    } finally {
      setLoading(null);
    }
  };

  const formatJiraIssuesForChat = (issues: JiraIssue[]): string => {
    if (issues.length === 0) {
      return "I don't have any Jira issues assigned to me right now.";
    }

    let message = `Here are my ${issues.length} assigned Jira issues:\n\n`;
    
    issues.forEach((issue, index) => {
      message += `${index + 1}. **${issue.key}**: ${issue.summary}\n`;
      message += `   - Status: ${issue.status}\n`;
      message += `   - Priority: ${issue.priority}\n`;
      message += `   - Updated: ${new Date(issue.updated).toLocaleDateString()}\n`;
      message += `   - Link: ${issue.url}\n\n`;
    });

    return message;
  };

  const formatGitHubPRsForChat = (prs: GitHubPullRequest[]): string => {
    if (prs.length === 0) {
      return "I don't have any open pull requests on GitHub right now.";
    }

    let message = `Here are my ${prs.length} open pull requests:\n\n`;
    
    prs.forEach((pr, index) => {
      message += `${index + 1}. **#${pr.number}**: ${pr.title}\n`;
      message += `   - Repository: ${pr.repo}\n`;
      message += `   - State: ${pr.state}\n`;
      message += `   - Updated: ${new Date(pr.updated_at).toLocaleDateString()}\n`;
      message += `   - Link: ${pr.url}\n\n`;
    });

    return message;
  };

  const formatRepoChangelogForChat = (commits: GitHubCommit[], repo: string): string => {
    if (commits.length === 0) {
      return `No recent commits found in ${repo} for the last 7 days.`;
    }

    let message = `Here are the recent commits in ${repo} (last 7 days):\n\n`;
    
    commits.forEach((commit, index) => {
      message += `${index + 1}. **${commit.message.split('\n')[0]}**\n`;
      message += `   - Author: ${commit.author}\n`;
      message += `   - Date: ${new Date(commit.date).toLocaleDateString()}\n`;
      message += `   - SHA: \`${commit.sha.substring(0, 7)}\`\n`;
      message += `   - Link: ${commit.url}\n\n`;
    });

    return message;
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center text-lg">
          <Zap className="h-5 w-5 mr-2" />
          Quick Actions
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Integration Status */}
        <div className="flex flex-col space-y-2">
          <Label className="text-xs font-medium text-muted-foreground">INTEGRATIONS</Label>
          <div className="flex flex-col space-y-2">
            <IntegrationStatus provider="github" className="w-full justify-start" />
            <IntegrationStatus provider="jira" className="w-full justify-start" />
          </div>
        </div>

        {/* Shortcuts */}
        <div className="border-t pt-3">
          <Label className="text-xs font-medium text-muted-foreground mb-2 block">SHORTCUTS</Label>
          <div className="space-y-2">
            {shortcuts.map((shortcut) => {
              const Icon = shortcut.icon;
              const connected = isConnected(shortcut.provider);
              const isLoading = loading === shortcut.id;

              return (
                <Button
                  key={shortcut.id}
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start h-auto p-3 text-left"
                  onClick={shortcut.action}
                  disabled={isLoading}
                >
                  <div className="flex items-start space-x-3">
                    {isLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin mt-0.5 text-primary" />
                    ) : (
                      <Icon className={`h-4 w-4 mt-0.5 ${connected ? 'text-primary' : 'text-muted-foreground'}`} />
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-sm">{shortcut.title}</span>
                        {!connected && <AlertCircle className="h-3 w-3 text-orange-500" />}
                      </div>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {shortcut.description}
                      </p>
                    </div>
                  </div>
                </Button>
              );
            })}
          </div>
        </div>

        {/* Repository Dialog */}
        <Dialog open={showRepoDialog} onOpenChange={setShowRepoDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Repository Changelog</DialogTitle>
              <DialogDescription>
                Enter the repository name to view recent commits (last 7 days).
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="repo">Repository</Label>
                <Input
                  id="repo"
                  placeholder="owner/repository-name"
                  value={repoInput}
                  onChange={(e) => setRepoInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleRepoChangelogSubmit()}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Format: owner/repository-name (e.g., microsoft/vscode)
                </p>
              </div>
              <div className="flex space-x-2">
                <Button onClick={handleRepoChangelogSubmit} disabled={!repoInput.trim() || !!loading}>
                  {loading === 'repo-changelog' && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
                  Load Changelog
                </Button>
                <Button variant="outline" onClick={() => setShowRepoDialog(false)}>
                  Cancel
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </CardContent>
    </Card>
  );
}