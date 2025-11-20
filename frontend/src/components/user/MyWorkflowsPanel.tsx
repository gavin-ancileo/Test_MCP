import React, { useState, useEffect } from 'react';
import { Play, Power, PowerOff, Clock, CheckCircle, XCircle, Loader, ChevronDown, ChevronUp, Copy } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { authenticatedFetch } from '@/lib/auth-utils';

interface Workflow {
  id: string;
  name: string;
  active: boolean;
  tags?: string[];
  user_enabled?: boolean; // User's subscription status
  webhook_url?: string; // User's unique webhook URL (when enabled)
  cloned_workflow_id?: string; // ID of user's cloned workflow
}

interface WorkflowExecution {
  id: number;
  workflow_id: string;
  status: 'success' | 'failed' | 'running';
  started_at: string;
  stopped_at?: string;
  duration_seconds?: number;
  mode: string;
}

const MyWorkflowsPanel: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedWorkflow, setExpandedWorkflow] = useState<string | null>(null);
  const [executions, setExecutions] = useState<Record<string, WorkflowExecution[]>>({});
  const [loadingExecutions, setLoadingExecutions] = useState<Record<string, boolean>>({});
  const [triggeringWorkflow, setTriggeringWorkflow] = useState<string | null>(null);
  const { toast } = useToast();

  const API_URL = '';

  useEffect(() => {
    loadWorkflows();
  }, []);

  const loadWorkflows = async () => {
    setLoading(true);
    try {
      const response = await authenticatedFetch(`${API_URL}/agentcore/user-workflows`);

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setWorkflows(data.workflows || []);
    } catch (error) {
      console.error('Load workflows error:', error);
      toast({
        title: "Error",
        description: "Failed to load workflows. Please try again.",
        variant: "destructive",
      });
      setWorkflows([]);
    } finally {
      setLoading(false);
    }
  };

  const toggleWorkflow = async (workflowId: string) => {
    try {
      const response = await authenticatedFetch(`${API_URL}/agentcore/user-workflows/${workflowId}/toggle`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || 'Failed to toggle workflow';

        // Check if it's an OAuth connection error (400 status)
        if (response.status === 400 && errorMessage.includes('connect')) {
          toast({
            title: "OAuth Connection Required",
            description: errorMessage,
            variant: "destructive",
          });
          return;
        }

        throw new Error(errorMessage);
      }

      const data = await response.json();

      toast({
        title: "Success",
        description: `Workflow ${data.enabled ? 'enabled' : 'disabled'} successfully`,
      });

      // Refresh workflows to get updated status
      loadWorkflows();
    } catch (error) {
      console.error('Toggle error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to toggle workflow';
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  const triggerWorkflow = async (workflowId: string, workflowName: string) => {
    setTriggeringWorkflow(workflowId);
    try {
      const response = await authenticatedFetch(`${API_URL}/agentcore/user-workflows/${workflowId}/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to trigger workflow');
      }

      toast({
        title: "Success",
        description: `Workflow "${workflowName}" triggered successfully`,
      });

      // Refresh executions for this workflow if expanded
      if (expandedWorkflow === workflowId) {
        setTimeout(() => loadExecutions(workflowId), 2000);
      }
    } catch (error) {
      console.error('Trigger error:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to trigger workflow",
        variant: "destructive",
      });
    } finally {
      setTriggeringWorkflow(null);
    }
  };

  const loadExecutions = async (workflowId: string) => {
    setLoadingExecutions((prev) => ({ ...prev, [workflowId]: true }));
    try {
      const response = await authenticatedFetch(`${API_URL}/agentcore/user-workflows/${workflowId}/executions?limit=10`);

      if (!response.ok) throw new Error('Failed to load executions');

      const data = await response.json();
      setExecutions((prev) => ({ ...prev, [workflowId]: data.executions || [] }));
    } catch (error) {
      console.error('Load executions error:', error);
      toast({
        title: "Error",
        description: "Failed to load execution history",
        variant: "destructive",
      });
    } finally {
      setLoadingExecutions((prev) => ({ ...prev, [workflowId]: false }));
    }
  };

  const toggleExecutions = (workflowId: string) => {
    if (expandedWorkflow === workflowId) {
      setExpandedWorkflow(null);
    } else {
      setExpandedWorkflow(workflowId);
      if (!executions[workflowId]) {
        loadExecutions(workflowId);
      }
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return 'N/A';
    if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`;
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}m ${secs}s`;
  };

  const formatTimestamp = (isoString?: string) => {
    if (!isoString) return 'N/A';
    const date = new Date(isoString);
    return date.toLocaleString();
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-600" />;
      case 'running':
        return <Loader className="w-4 h-4 text-blue-600 animate-spin" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const copyWebhookUrl = (url: string) => {
    navigator.clipboard.writeText(url);
    toast({
      title: "Copied",
      description: "Webhook URL copied to clipboard",
    });
  };

  const getIntegrationName = (workflow: Workflow): string => {
    const name = workflow.name.toLowerCase();
    if (name.includes('drive')) return 'Google Drive';
    if (name.includes('github')) return 'GitHub';
    if (name.includes('jira')) return 'Jira';
    return 'external service';
  };

  const getScheduleInfo = (workflow: Workflow): string | null => {
    const name = workflow.name.toLowerCase();
    // Most workflows run hourly by default
    if (name.includes('monitor') || name.includes('commits') || name.includes('issues') || name.includes('changes')) {
      return 'Runs every 1 hour';
    }
    return null;
  };

  // Filter workflows by user's enabled status
  const enabledWorkflows = workflows.filter(w => w.user_enabled);
  const availableWorkflows = workflows.filter(w => !w.user_enabled);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">My Workflows</h2>
        <p className="text-gray-600 mt-1">Manage and run your automated workflows</p>
      </div>

      {loading ? (
        <div className="p-8 text-center">
          <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-gray-500">Loading workflows...</p>
        </div>
      ) : (
        <>
          {/* Enabled Workflows */}
          {enabledWorkflows.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 bg-green-50 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Active Workflows ({enabledWorkflows.length})</h3>
                <p className="text-sm text-gray-600">Workflows you have enabled</p>
              </div>
              <div className="divide-y divide-gray-200">
                {enabledWorkflows.map((workflow) => (
                  <div key={workflow.id} className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <h4 className="text-lg font-medium text-gray-900">{workflow.name}</h4>
                          <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                            Enabled
                          </span>
                          {workflow.active && (
                            <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                              Active in N8N
                            </span>
                          )}
                          {getScheduleInfo(workflow) && (
                            <span className="px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-800 flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {getScheduleInfo(workflow)}
                            </span>
                          )}
                        </div>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {(workflow.tags || []).map((tag) => (
                            <span
                              key={tag}
                              className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="flex gap-2 ml-4">
                        <button
                          onClick={() => triggerWorkflow(workflow.id, workflow.name)}
                          disabled={triggeringWorkflow === workflow.id}
                          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          title="Run Now"
                        >
                          {triggeringWorkflow === workflow.id ? (
                            <Loader className="w-4 h-4 animate-spin" />
                          ) : (
                            <Play className="w-4 h-4" />
                          )}
                          Run Now
                        </button>
                        <button
                          onClick={() => toggleExecutions(workflow.id)}
                          className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                          title="View History"
                        >
                          {expandedWorkflow === workflow.id ? (
                            <ChevronUp className="w-4 h-4" />
                          ) : (
                            <ChevronDown className="w-4 h-4" />
                          )}
                        </button>
                        <button
                          onClick={() => toggleWorkflow(workflow.id)}
                          className="p-2 text-yellow-600 hover:text-yellow-900 transition-colors"
                          title="Disable"
                        >
                          <PowerOff className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    {/* Webhook URL */}
                    {workflow.user_enabled && workflow.webhook_url && (
                      <div className="mt-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                        <label className="block text-xs font-medium text-gray-700 mb-2">Your Webhook URL:</label>
                        <div className="flex items-center gap-2">
                          <code className="flex-1 text-xs bg-white px-3 py-2 rounded border border-blue-300 font-mono overflow-x-auto">
                            {workflow.webhook_url}
                          </code>
                          <button
                            onClick={() => copyWebhookUrl(workflow.webhook_url!)}
                            className="p-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors flex-shrink-0"
                            title="Copy URL"
                          >
                            <Copy className="w-4 h-4" />
                          </button>
                        </div>
                        <p className="text-xs text-gray-600 mt-2">
                          Configure this URL in your {getIntegrationName(workflow)} settings to receive notifications.
                        </p>
                      </div>
                    )}

                    {/* Execution History */}
                    {expandedWorkflow === workflow.id && (
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        <h5 className="text-sm font-medium text-gray-700 mb-3">Execution History</h5>
                        {loadingExecutions[workflow.id] ? (
                          <div className="text-center py-4">
                            <Loader className="w-5 h-5 animate-spin mx-auto text-blue-500" />
                          </div>
                        ) : executions[workflow.id] && executions[workflow.id].length > 0 ? (
                          <div className="space-y-2">
                            {executions[workflow.id].map((execution) => (
                              <div
                                key={execution.id}
                                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                              >
                                <div className="flex items-center gap-3">
                                  {getStatusIcon(execution.status)}
                                  <div>
                                    <div className="text-sm font-medium text-gray-900">
                                      {formatTimestamp(execution.started_at)}
                                    </div>
                                    <div className="text-xs text-gray-500">
                                      Mode: {execution.mode}
                                    </div>
                                  </div>
                                </div>
                                <div className="flex items-center gap-3">
                                  <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(execution.status)}`}>
                                    {execution.status}
                                  </span>
                                  <span className="text-xs text-gray-500">
                                    {formatDuration(execution.duration_seconds)}
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-sm text-gray-500 text-center py-4">No executions yet</p>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Available Workflows */}
          {availableWorkflows.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Available Workflows ({availableWorkflows.length})</h3>
                <p className="text-sm text-gray-600">Click to enable workflows</p>
              </div>
              <div className="divide-y divide-gray-200">
                {availableWorkflows.map((workflow) => (
                  <div key={workflow.id} className="p-6 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <h4 className="text-lg font-medium text-gray-900">{workflow.name}</h4>
                          <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-600">
                            Disabled
                          </span>
                          {getScheduleInfo(workflow) && (
                            <span className="px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-800 flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {getScheduleInfo(workflow)}
                            </span>
                          )}
                        </div>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {(workflow.tags || []).map((tag) => (
                            <span
                              key={tag}
                              className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                      <button
                        onClick={() => toggleWorkflow(workflow.id)}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        title="Enable"
                      >
                        <Power className="w-4 h-4" />
                        Enable
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* No workflows */}
          {workflows.length === 0 && (
            <div className="p-8 text-center bg-white rounded-lg border border-gray-200">
              <p className="text-gray-500 mb-4">No workflows available</p>
              <p className="text-sm text-gray-400">Contact your administrator to create workflows</p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default MyWorkflowsPanel;
