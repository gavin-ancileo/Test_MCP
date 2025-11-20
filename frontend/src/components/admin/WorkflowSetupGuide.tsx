import React, { useState } from 'react';
import { Copy, Check, Clock, Zap, FileText } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const WorkflowSetupGuide: React.FC = () => {
  const [copiedSection, setCopiedSection] = useState<string | null>(null);
  const { toast } = useToast();

  const copyToClipboard = (text: string, section: string) => {
    navigator.clipboard.writeText(text);
    setCopiedSection(section);
    toast({
      title: "Copied!",
      description: "Template JSON copied to clipboard",
    });
    setTimeout(() => setCopiedSection(null), 2000);
  };

  const scheduleIntervals = [
    { label: "Every 15 minutes", value: "minutes", interval: 15, use: "High-frequency monitoring" },
    { label: "Every 30 minutes", value: "minutes", interval: 30, use: "Active projects" },
    { label: "Every 1 hour", value: "hours", interval: 1, use: "Standard monitoring (recommended)" },
    { label: "Every 6 hours", value: "hours", interval: 6, use: "Low-priority updates" },
    { label: "Every 12 hours", value: "hours", interval: 12, use: "Daily summary (twice)" },
    { label: "Every 24 hours", value: "hours", interval: 24, use: "Daily digest" },
  ];

  const templates = {
    github: `{
  "name": "[TEMPLATE] GitHub Commits Monitor",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [{"field": "hours", "hoursInterval": 1}]
        }
      },
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "http://mcp-server.aap.local:8001/execute",
        "method": "POST",
        "bodyParametersJson": "{\\"tool_name\\": \\"github_list_commits\\", \\"arguments\\": {\\"hours\\": 1}}",
        "options": {"timeout": 30000}
      },
      "name": "Get Recent Commits",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [450, 300]
    },
    {
      "parameters": {
        "conditions": {
          "boolean": [{"value1": "={{ $json.commits && $json.commits.length > 0 }}", "value2": true}]
        }
      },
      "name": "Has Updates?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [650, 300]
    },
    {
      "parameters": {
        "subject": "GitHub: {{ $json.commits.length }} new commits",
        "emailType": "html",
        "message": "<h2>Recent Commits</h2><ul>{{ $json.commits.map(c => \`<li>\${c.repo}: \${c.message}</li>\`).join('') }}</ul>"
      },
      "name": "Send Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 2,
      "position": [850, 200]
    }
  ],
  "connections": {
    "Schedule Trigger": {"main": [[{"node": "Get Recent Commits", "type": "main", "index": 0}]]},
    "Get Recent Commits": {"main": [[{"node": "Has Updates?", "type": "main", "index": 0}]]},
    "Has Updates?": {"main": [[{"node": "Send Email", "type": "main", "index": 0}], []]}
  },
  "settings": {"executionOrder": "v1"}
}`,
    jira: `{
  "name": "[TEMPLATE] Jira Issues Monitor",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [{"field": "hours", "hoursInterval": 1}]
        }
      },
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "http://mcp-server.aap.local:8001/execute",
        "method": "POST",
        "bodyParametersJson": "{\\"tool_name\\": \\"jira_get_my_issues\\", \\"arguments\\": {\\"updated_since_hours\\": 1}}",
        "options": {"timeout": 30000}
      },
      "name": "Get Updated Issues",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [450, 300]
    },
    {
      "parameters": {
        "conditions": {
          "boolean": [{"value1": "={{ $json.issues && $json.issues.length > 0 }}", "value2": true}]
        }
      },
      "name": "Has Updates?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [650, 300]
    },
    {
      "parameters": {
        "subject": "Jira: {{ $json.issues.length }} issues updated",
        "emailType": "html",
        "message": "<h2>Updated Issues</h2><ul>{{ $json.issues.map(i => \`<li>\${i.key}: \${i.summary}</li>\`).join('') }}</ul>"
      },
      "name": "Send Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 2,
      "position": [850, 200]
    }
  ],
  "connections": {
    "Schedule Trigger": {"main": [[{"node": "Get Updated Issues", "type": "main", "index": 0}]]},
    "Get Updated Issues": {"main": [[{"node": "Has Updates?", "type": "main", "index": 0}]]},
    "Has Updates?": {"main": [[{"node": "Send Email", "type": "main", "index": 0}], []]}
  },
  "settings": {"executionOrder": "v1"}
}`,
    drive: `{
  "name": "[TEMPLATE] Google Drive Changes Monitor",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [{"field": "hours", "hoursInterval": 1}]
        }
      },
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "http://mcp-server.aap.local:8001/execute",
        "method": "POST",
        "bodyParametersJson": "{\\"tool_name\\": \\"google_drive_list_recent\\", \\"arguments\\": {\\"modified_since_hours\\": 1}}",
        "options": {"timeout": 30000}
      },
      "name": "Get Recent Changes",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4.1,
      "position": [450, 300]
    },
    {
      "parameters": {
        "conditions": {
          "boolean": [{"value1": "={{ $json.files && $json.files.length > 0 }}", "value2": true}]
        }
      },
      "name": "Has Updates?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [650, 300]
    },
    {
      "parameters": {
        "subject": "Drive: {{ $json.files.length }} files changed",
        "emailType": "html",
        "message": "<h2>Recent Changes</h2><ul>{{ $json.files.map(f => \`<li>\${f.name}</li>\`).join('') }}</ul>"
      },
      "name": "Send Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 2,
      "position": [850, 200]
    }
  ],
  "connections": {
    "Schedule Trigger": {"main": [[{"node": "Get Recent Changes", "type": "main", "index": 0}]]},
    "Get Recent Changes": {"main": [[{"node": "Has Updates?", "type": "main", "index": 0}]]},
    "Has Updates?": {"main": [[{"node": "Send Email", "type": "main", "index": 0}], []]}
  },
  "settings": {"executionOrder": "v1"}
}`
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Workflow Setup Guide</h1>
        <p className="text-gray-600 mt-2">Learn how to create and configure template workflows for multi-user monitoring</p>
      </div>

      {/* Overview */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-blue-900 mb-3">How It Works</h2>
        <div className="space-y-2 text-sm text-blue-800">
          <p>1. <strong>Admin creates template workflow</strong> with [TEMPLATE] prefix</p>
          <p>2. <strong>User enables workflow</strong> in My Workflows page</p>
          <p>3. <strong>System clones workflow</strong> with user's email and OAuth tokens</p>
          <p>4. <strong>Workflow runs automatically</strong> on schedule (15min - 24h)</p>
          <p>5. <strong>User receives email</strong> when there are updates</p>
        </div>
      </div>

      {/* Schedule Intervals */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <Clock className="w-5 h-5 text-gray-700" />
          <h2 className="text-xl font-semibold text-gray-900">Available Schedule Intervals</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {scheduleIntervals.map((schedule) => (
            <div key={`${schedule.value}-${schedule.interval}`} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="w-4 h-4 text-blue-600" />
                <h3 className="font-medium text-gray-900">{schedule.label}</h3>
              </div>
              <p className="text-sm text-gray-600">{schedule.use}</p>
              <code className="text-xs bg-gray-100 px-2 py-1 rounded mt-2 block">
                {`{"field": "${schedule.value}", "${schedule.value}Interval": ${schedule.interval}}`}
              </code>
            </div>
          ))}
        </div>
      </div>

      {/* Template Workflows */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center gap-2 mb-4">
          <FileText className="w-5 h-5 text-gray-700" />
          <h2 className="text-xl font-semibold text-gray-900">Template Workflows</h2>
        </div>

        <div className="space-y-6">
          {/* GitHub Template */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-medium text-gray-900">GitHub Commits Monitor</h3>
              <button
                onClick={() => copyToClipboard(templates.github, 'github')}
                className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
              >
                {copiedSection === 'github' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                {copiedSection === 'github' ? 'Copied!' : 'Copy Template'}
              </button>
            </div>
            <p className="text-sm text-gray-600 mb-3">Monitors GitHub commits and sends email summary when there are new commits</p>
            <pre className="bg-gray-50 p-3 rounded text-xs overflow-x-auto max-h-60">
              {templates.github}
            </pre>
          </div>

          {/* Jira Template */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-medium text-gray-900">Jira Issues Monitor</h3>
              <button
                onClick={() => copyToClipboard(templates.jira, 'jira')}
                className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
              >
                {copiedSection === 'jira' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                {copiedSection === 'jira' ? 'Copied!' : 'Copy Template'}
              </button>
            </div>
            <p className="text-sm text-gray-600 mb-3">Monitors Jira issues assigned to user and sends email when issues are updated</p>
            <pre className="bg-gray-50 p-3 rounded text-xs overflow-x-auto max-h-60">
              {templates.jira}
            </pre>
          </div>

          {/* Drive Template */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-medium text-gray-900">Google Drive Changes Monitor</h3>
              <button
                onClick={() => copyToClipboard(templates.drive, 'drive')}
                className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
              >
                {copiedSection === 'drive' ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                {copiedSection === 'drive' ? 'Copied!' : 'Copy Template'}
              </button>
            </div>
            <p className="text-sm text-gray-600 mb-3">Monitors Google Drive files and sends email when files are modified</p>
            <pre className="bg-gray-50 p-3 rounded text-xs overflow-x-auto max-h-60">
              {templates.drive}
            </pre>
          </div>
        </div>
      </div>

      {/* Setup Instructions */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Setup Instructions</h2>
        <ol className="space-y-3 list-decimal list-inside text-sm text-gray-700">
          <li><strong>Copy template JSON</strong> using the copy button above</li>
          <li><strong>Go to N8N Workflows</strong> page in admin panel</li>
          <li><strong>Click "Create Workflow"</strong></li>
          <li><strong>Paste the JSON</strong> into the workflow editor</li>
          <li><strong>Customize schedule interval</strong> if needed (change "hoursInterval" value)</li>
          <li><strong>Save workflow</strong> - it will appear in users' "My Workflows" page</li>
          <li><strong>Users enable workflow</strong> - system clones with their email and OAuth</li>
          <li><strong>Workflow runs automatically</strong> and sends email notifications</li>
        </ol>
      </div>

      {/* Important Notes */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-yellow-900 mb-3">Important Notes</h2>
        <ul className="space-y-2 text-sm text-yellow-800">
          <li>• Workflow name MUST start with <code className="bg-yellow-100 px-1">[TEMPLATE]</code> to appear for users</li>
          <li>• System automatically injects user_id into HTTP Request nodes</li>
          <li>• Email recipient is automatically set to user's email</li>
          <li>• User's OAuth tokens are used for MCP tool calls</li>
          <li>• Do NOT activate template workflows - they auto-activate when cloned</li>
        </ul>
      </div>
    </div>
  );
};

export default WorkflowSetupGuide;
