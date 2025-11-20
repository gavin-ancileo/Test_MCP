import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, Copy, Play, Eye, Search, Power, PowerOff, Code } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { authenticatedFetch } from '@/lib/auth-utils';

export interface Workflow {
  id: string;
  name: string;
  active: boolean;
  nodes: any[];
  connections: any;
  createdAt?: string;
  updatedAt?: string;
  tags?: string[];
}

const WorkflowsPanel: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingWorkflow, setEditingWorkflow] = useState<Workflow | null>(null);
  const [workflowJson, setWorkflowJson] = useState('');
  const [testModalOpen, setTestModalOpen] = useState(false);
  const [testWorkflowId, setTestWorkflowId] = useState('');
  const [testPayload, setTestPayload] = useState('{}');
  const [activatingWorkflowId, setActivatingWorkflowId] = useState<string | null>(null);
  const { toast } = useToast();

  // Use empty URL - nginx routes /agentcore to backend
  const API_URL = '';

  useEffect(() => {
    loadWorkflows();
  }, []);

  const loadWorkflows = async () => {
    setLoading(true);
    try {
      // Direct REST API call to n8n endpoint
      const response = await authenticatedFetch(`${API_URL}/agentcore/n8n/workflows`);

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}: ${response.statusText}`);
      }

      const workflows = await response.json();
      setWorkflows(workflows);
    } catch (error) {
      console.error('Load workflows error:', error);
      toast({
        title: "Error",
        description: "Failed to load workflows. Check if n8n service is running.",
        variant: "destructive",
      });
      setWorkflows([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingWorkflow(null);
    setWorkflowJson('');
    setModalOpen(true);
  };

  const handleEdit = (workflow: Workflow) => {
    setEditingWorkflow(workflow);
    setWorkflowJson(JSON.stringify(workflow, null, 2));
    setModalOpen(true);
  };

  const handleDelete = async (workflowId: string) => {
    if (!confirm(`Delete workflow "${workflowId}"? This action cannot be undone.`)) return;

    try {
      const response = await authenticatedFetch(`${API_URL}/agentcore/n8n/workflows/${workflowId}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete workflow');

      toast({
        title: "Success",
        description: "Workflow deleted successfully",
      });

      loadWorkflows();
    } catch (error) {
      console.error('Delete error:', error);
      toast({
        title: "Error",
        description: "Failed to delete workflow",
        variant: "destructive",
      });
    }
  };

  const handleActivate = async (workflowId: string, activate: boolean) => {
    const action = activate ? 'activate' : 'deactivate';

    // Optimistic update: Update UI immediately for instant feedback
    setWorkflows(workflows.map(w =>
      w.id === workflowId ? { ...w, active: activate } : w
    ));
    setActivatingWorkflowId(workflowId);

    try {
      const response = await authenticatedFetch(`${API_URL}/agentcore/n8n/workflows/${workflowId}/activate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ active: activate }),
      });

      if (!response.ok) throw new Error(`Failed to ${action} workflow`);

      toast({
        title: "Success",
        description: `Workflow ${action}d successfully`,
      });

      // Clear loading state immediately - no need to wait
      setActivatingWorkflowId(null);

    } catch (error) {
      console.error(`${action} error:`, error);

      // Rollback optimistic update on error
      setWorkflows(workflows.map(w =>
        w.id === workflowId ? { ...w, active: !activate } : w
      ));
      setActivatingWorkflowId(null);

      toast({
        title: "Error",
        description: `Failed to ${action} workflow`,
        variant: "destructive",
      });
    }
  };

  const handleTest = (workflowId: string) => {
    setTestWorkflowId(workflowId);
    setTestPayload('{}');
    setTestModalOpen(true);
  };

  const handleRunTest = async () => {
    try {
      const payload = JSON.parse(testPayload);
      const response = await authenticatedFetch(`${API_URL}/agentcore/n8n/workflows/${testWorkflowId}/trigger`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error('Failed to trigger workflow');

      const data = await response.json();
      toast({
        title: "Success",
        description: "Workflow triggered successfully. Check n8n for execution results.",
      });

      setTestModalOpen(false);
    } catch (error) {
      console.error('Test error:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to trigger workflow",
        variant: "destructive",
      });
    }
  };

  const handleSaveWorkflow = async () => {
    try {
      let workflowData;
      try {
        workflowData = JSON.parse(workflowJson);
      } catch (e) {
        toast({
          title: "Error",
          description: "Invalid JSON format",
          variant: "destructive",
        });
        return;
      }

      // Use database-direct edit endpoint for updates (bypasses n8n API limitations)
      const url = editingWorkflow
        ? `${API_URL}/agentcore/n8n/workflows/${editingWorkflow.id}/edit-db`
        : `${API_URL}/agentcore/n8n/workflows`;

      const response = await authenticatedFetch(url, {
        method: editingWorkflow ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(workflowData),
      });

      if (!response.ok) throw new Error(`Failed to ${editingWorkflow ? 'update' : 'create'} workflow`);

      const result = await response.json();

      toast({
        title: "Success",
        description: editingWorkflow
          ? "Workflow updated in database. Changes will appear after n8n cache refresh."
          : "Workflow created successfully",
      });

      setModalOpen(false);
      setEditingWorkflow(null);
      setWorkflowJson('');

      // Optimistic update for edit (same pattern as activate)
      if (editingWorkflow) {
        setWorkflows(workflows.map(w =>
          w.id === editingWorkflow.id ? { ...w, ...workflowData } : w
        ));
      } else {
        loadWorkflows(); // Only reload for create
      }
    } catch (error) {
      console.error('Save error:', error);
      toast({
        title: "Error",
        description: `Failed to ${editingWorkflow ? 'update' : 'create'} workflow`,
        variant: "destructive",
      });
    }
  };

  const copyWebhookUrl = (workflowId: string) => {
    const webhookUrl = `http://aap-n8n.aap.local:5678/webhook/${workflowId}`;
    navigator.clipboard.writeText(webhookUrl);
    toast({
      title: "Copied",
      description: "Webhook URL copied to clipboard",
    });
  };

  // Filter workflows based on search
  const filteredWorkflows = workflows.filter(workflow => {
    return workflow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
           workflow.id.toLowerCase().includes(searchTerm.toLowerCase());
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">n8n Workflows Management</h2>
          <p className="text-gray-600 mt-1">Create, edit, and manage n8n automation workflows</p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Create Workflow
        </button>
      </div>

      {/* Search */}
      <div className="flex gap-4 items-center">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search workflows..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent w-full"
          />
        </div>
        
        <button
          onClick={loadWorkflows}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          Refresh
        </button>
      </div>

      {/* Workflows Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-gray-500">Loading workflows...</p>
          </div>
        ) : filteredWorkflows.length === 0 ? (
          <div className="p-8 text-center">
            <p className="text-gray-500 mb-4">No workflows found</p>
            <button
              onClick={handleCreate}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create Your First Workflow
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tags</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredWorkflows.map((workflow) => (
                  <tr key={workflow.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <code className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">
                        {workflow.id}
                      </code>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">{workflow.name}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        workflow.active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {workflow.active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {(workflow.tags || []).map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleActivate(workflow.id, !workflow.active)}
                          disabled={activatingWorkflowId === workflow.id}
                          className={`p-1 transition-colors ${
                            activatingWorkflowId === workflow.id
                              ? 'text-gray-400 cursor-not-allowed'
                              : workflow.active
                                ? 'text-yellow-600 hover:text-yellow-900'
                                : 'text-green-600 hover:text-green-900'
                          }`}
                          title={
                            activatingWorkflowId === workflow.id
                              ? "Processing..."
                              : workflow.active ? "Deactivate" : "Activate"
                          }
                        >
                          {workflow.active ? <PowerOff className="w-4 h-4" /> : <Power className="w-4 h-4" />}
                        </button>
                        <button
                          onClick={() => handleTest(workflow.id)}
                          className="p-1 text-blue-600 hover:text-blue-900 transition-colors"
                          title="Test"
                        >
                          <Play className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => copyWebhookUrl(workflow.id)}
                          className="p-1 text-purple-600 hover:text-purple-900 transition-colors"
                          title="Copy Webhook URL"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleEdit(workflow)}
                          className="p-1 text-green-600 hover:text-green-900 transition-colors"
                          title="Edit workflow (updates database directly)"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(workflow.id)}
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

      {/* Create/Edit Modal */}
      {modalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold mb-4">
              {editingWorkflow ? 'Edit Workflow' : 'Create Workflow'}
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Workflow JSON
                </label>
                <textarea
                  value={workflowJson}
                  onChange={(e) => setWorkflowJson(e.target.value)}
                  className="w-full h-96 font-mono text-sm border border-gray-300 rounded-lg p-4"
                  placeholder='{"name": "My Workflow", "nodes": [...], "connections": {...}}'
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  onClick={() => {
                    setModalOpen(false);
                    setEditingWorkflow(null);
                    setWorkflowJson('');
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveWorkflow}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  {editingWorkflow ? 'Update' : 'Create'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Test Modal */}
      {testModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
            <h3 className="text-xl font-bold mb-4">Test Workflow: {testWorkflowId}</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Test Payload (JSON)
                </label>
                <textarea
                  value={testPayload}
                  onChange={(e) => setTestPayload(e.target.value)}
                  className="w-full h-48 font-mono text-sm border border-gray-300 rounded-lg p-4"
                  placeholder='{"key": "value"}'
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  onClick={() => setTestModalOpen(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleRunTest}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Run Test
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkflowsPanel;

