<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AAP Admin Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .api-status {
            margin-top: 15px;
            display: flex;
            gap: 20px;
            align-items: center;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(255,255,255,0.2);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4ade80;
        }
        
        .status-dot.error {
            background: #f87171;
        }
        
        .debug-btn {
            background: rgba(255,255,255,0.3);
            border: 1px solid white;
            color: white;
            padding: 5px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .debug-btn:hover {
            background: rgba(255,255,255,0.4);
        }
        
        .tabs {
            background: #f8f9fa;
            display: flex;
            border-bottom: 2px solid #dee2e6;
        }
        
        .tab {
            padding: 15px 30px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            color: #6c757d;
            transition: all 0.3s;
        }
        
        .tab:hover {
            color: #667eea;
            background: rgba(102, 126, 234, 0.1);
        }
        
        .tab.active {
            color: #667eea;
            border-bottom: 3px solid #667eea;
            margin-bottom: -2px;
        }
        
        .content {
            padding: 30px;
        }
        
        .tab-panel {
            display: none;
        }
        
        .tab-panel.active {
            display: block;
        }
        
        .message {
            padding: 12px 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            display: none;
            font-weight: 500;
        }
        
        .message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            display: block;
        }
        
        .message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            display: block;
        }
        
        .message.info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
            display: block;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #2d3748;
            font-size: 14px;
        }
        
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .form-group textarea {
            min-height: 250px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            resize: vertical;
        }
        
        .form-group .help-text {
            font-size: 12px;
            color: #718096;
            margin-top: 5px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #e2e8f0;
            color: #4a5568;
        }
        
        .btn-secondary:hover {
            background: #cbd5e0;
        }
        
        .btn-danger {
            background: #fc8181;
            color: white;
        }
        
        .btn-danger:hover {
            background: #f56565;
        }
        
        .btn-info {
            background: #4299e1;
            color: white;
        }
        
        .btn-info:hover {
            background: #3182ce;
        }
        
        .btn-small {
            padding: 6px 12px;
            font-size: 12px;
        }
        
        .prompt-list {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .prompt-item {
            padding: 15px 20px;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.2s;
        }
        
        .prompt-item:last-child {
            border-bottom: none;
        }
        
        .prompt-item:hover {
            background: #f7fafc;
        }
        
        .prompt-info h4 {
            margin-bottom: 5px;
            color: #2d3748;
            font-size: 16px;
        }
        
        .prompt-info .meta {
            font-size: 12px;
            color: #718096;
        }
        
        .prompt-actions {
            display: flex;
            gap: 8px;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #718096;
        }
        
        .empty-state h3 {
            color: #4a5568;
            margin-bottom: 10px;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
        }
        
        .modal.active {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 12px;
            width: 90%;
            max-width: 700px;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .modal-header h2 {
            color: #2d3748;
        }
        
        .close-btn {
            background: none;
            border: none;
            font-size: 28px;
            cursor: pointer;
            color: #718096;
            width: 36px;
            height: 36px;
        }
        
        .close-btn:hover {
            color: #2d3748;
        }
        
        .test-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .test-section {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px;
        }
        
        .test-section h3 {
            margin-bottom: 15px;
            color: #2d3748;
            font-size: 18px;
        }
        
        .variable-field {
            margin-bottom: 12px;
        }
        
        .variable-field label {
            display: block;
            margin-bottom: 4px;
            font-size: 13px;
            color: #4a5568;
            font-weight: 500;
        }
        
        .variable-field input {
            width: 100%;
            padding: 8px;
            border: 1px solid #cbd5e0;
            border-radius: 4px;
            font-size: 13px;
        }
        
        .output-box {
            background: white;
            border: 1px solid #cbd5e0;
            border-radius: 8px;
            padding: 15px;
            min-height: 350px;
            font-family: monospace;
            font-size: 13px;
            white-space: pre-wrap;
            word-wrap: break-word;
            color: #2d3748;
            line-height: 1.5;
        }
        
        .loading {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 3px solid #e2e8f0;
            border-radius: 50%;
            border-top-color: #667eea;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .debug-panel {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            font-family: monospace;
            font-size: 12px;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .debug-log {
            margin-bottom: 5px;
            padding: 3px 0;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .debug-log.error {
            color: #e53e3e;
        }
        
        .debug-log.success {
            color: #38a169;
        }
        
        .debug-log.info {
            color: #3182ce;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AAP Prompt Management System</h1>
            <p>AI Assistant Platform - Manage and test your prompts</p>
            <div class="api-status">
                <div class="status-item">
                    <span class="status-dot" id="apiStatus"></span>
                    <span>API Server</span>
                </div>
                <div class="status-item">
                    <span class="status-dot" id="modelsStatus"></span>
                    <span>Models Engine</span>
                </div>
                <button class="debug-btn" onclick="testConnection()">Test Connection</button>
                <button class="debug-btn" onclick="toggleDebug()">Toggle Debug</button>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="switchTab('create')">Create Prompt</button>
            <button class="tab" onclick="switchTab('manage')">Manage Prompts</button>
            <button class="tab" onclick="switchTab('test')">Test Prompt</button>
        </div>
        
        <div class="content">
            <div id="message" class="message"></div>
            
            <div id="debugPanel" class="debug-panel" style="display: none;">
                <strong>Debug Console:</strong>
                <div id="debugLog"></div>
            </div>
            
            <!-- Create Tab -->
            <div id="create" class="tab-panel active">
                <h2>Create New Prompt</h2>
                <br>
                
                <div class="form-group">
                    <label>Prompt Code *</label>
                    <input type="text" id="promptCode" placeholder="e.g., dev_code_review">
                    <div class="help-text">Unique identifier, lowercase with underscores only</div>
                </div>
                
                <div class="form-group">
                    <label>Prompt Name *</label>
                    <input type="text" id="promptName" placeholder="e.g., Code Review Assistant">
                </div>
                
                <div class="form-group">
                    <label>Category</label>
                    <select id="promptCategory">
                        <option value="general">General</option>
                        <option value="development">Development</option>
                        <option value="qa">Quality Assurance</option>
                        <option value="hr">Human Resources</option>
                        <option value="pm">Project Management</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Prompt Content *</label>
                    <textarea id="promptContent" placeholder="Enter your prompt content here.&#10;&#10;Use {{variable_name}} for dynamic values.&#10;&#10;Example:&#10;Review the code for {{repository}} pull request #{{pr_number}}"></textarea>
                    <div class="help-text">Use {{variable}} syntax for dynamic values that can be replaced during execution</div>
                </div>
                
                <div style="display: flex; gap: 10px;">
                    <button class="btn btn-primary" onclick="savePrompt()">Save Prompt</button>
                    <button class="btn btn-secondary" onclick="clearForm()">Clear Form</button>
                </div>
            </div>
            
            <!-- Manage Tab -->
            <div id="manage" class="tab-panel">
                <h2>Manage Existing Prompts</h2>
                <br>
                <button class="btn btn-info btn-small" onclick="loadPrompts()" style="margin-bottom: 15px;">Refresh List</button>
                
                <div class="prompt-list" id="promptList">
                    <div class="empty-state">
                        <div class="loading"></div>
                        <h3>Loading prompts...</h3>
                    </div>
                </div>
            </div>
            
            <!-- Test Tab -->
            <div id="test" class="tab-panel">
                <h2>Test Prompt Execution</h2>
                <br>
                
                <div class="test-container">
                    <div class="test-section">
                        <h3>Configuration</h3>
                        
                        <div class="form-group">
                            <label>Select Prompt</label>
                            <select id="testPromptSelect" onchange="loadPromptForTest()">
                                <option value="">-- Select a prompt --</option>
                            </select>
                        </div>
                        
                        <div id="variableInputs"></div>
                        
                        <div class="form-group">
                            <label>AI Model</label>
                            <select id="modelSelect">
                                <option value="amazon.nova-micro-v1:0">Amazon Nova Micro (Fast)</option>
                                <option value="amazon.nova-lite-v1:0">Amazon Nova Lite</option>
                                <option value="amazon.nova-pro-v1:0">Amazon Nova Pro</option>
                                <option value="anthropic.claude-v2">Claude v2</option>
                                <option value="anthropic.claude-instant-v1">Claude Instant</option>
                            </select>
                        </div>
                        
                        <button class="btn btn-primary" onclick="executeTest()" style="width: 100%;">Execute Test</button>
                    </div>
                    
                    <div class="test-section">
                        <h3>Output</h3>
                        <div class="output-box" id="testOutput">Select a prompt and configure inputs to see results here...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Edit Modal -->
    <div id="editModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Edit Prompt</h2>
                <button class="close-btn" onclick="closeModal()">&times;</button>
            </div>
            
            <div class="form-group">
                <label>Prompt Code</label>
                <input type="text" id="editCode" disabled>
            </div>
            
            <div class="form-group">
                <label>Prompt Name</label>
                <input type="text" id="editName">
            </div>
            
            <div class="form-group">
                <label>Category</label>
                <select id="editCategory">
                    <option value="general">General</option>
                    <option value="development">Development</option>
                    <option value="qa">Quality Assurance</option>
                    <option value="hr">Human Resources</option>
                    <option value="pm">Project Management</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Prompt Content</label>
                <textarea id="editContent"></textarea>
            </div>
            
            <div style="display: flex; gap: 10px;">
                <button class="btn btn-primary" onclick="updatePrompt()">Save Changes</button>
                <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            </div>
        </div>
    </div>

    <script>
        // Configuration
        var API_BASE = 'https://btjl2wxpwraof2lt64yjjvjvbe0rwbjn.lambda-url.ap-southeast-1.on.aws';
        var MODELS_URL = 'https://ngt2e53h6vwwe2wnu7lpzp62du0mujya.lambda-url.ap-southeast-1.on.aws';
        
        // State
        var state = {
            prompts: [],
            currentEditCode: null,
            currentTestPrompt: null,
            debugMode: false
        };
        
        // Debug logging
        function debugLog(message, type) {
            console.log('[DEBUG] ' + message);
            
            if (state.debugMode) {
                var debugDiv = document.getElementById('debugLog');
                var timestamp = new Date().toLocaleTimeString();
                var logEntry = document.createElement('div');
                logEntry.className = 'debug-log ' + (type || 'info');
                logEntry.textContent = timestamp + ' - ' + message;
                debugDiv.insertBefore(logEntry, debugDiv.firstChild);
                
                // Keep only last 50 logs
                while (debugDiv.children.length > 50) {
                    debugDiv.removeChild(debugDiv.lastChild);
                }
            }
        }
        
        // Toggle debug panel
        function toggleDebug() {
            state.debugMode = !state.debugMode;
            document.getElementById('debugPanel').style.display = state.debugMode ? 'block' : 'none';
            debugLog('Debug mode: ' + (state.debugMode ? 'ON' : 'OFF'), 'info');
        }
        
        // Initialize
        window.onload = function() {
            debugLog('Dashboard initialized', 'info');
            debugLog('API Base: ' + API_BASE, 'info');
            debugLog('Models URL: ' + MODELS_URL, 'info');
            
            checkAPIStatus();
            loadPrompts();
            
            // Check API status every 30 seconds
            setInterval(checkAPIStatus, 30000);
        };
        
        // Check API Status
        function checkAPIStatus() {
            debugLog('Checking API status...', 'info');
            
            // Check main API
            fetch(API_BASE + '/health')
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    debugLog('API health check success: ' + JSON.stringify(data), 'success');
                    document.getElementById('apiStatus').className = 'status-dot';
                })
                .catch(function(error) {
                    debugLog('API health check failed: ' + error.message, 'error');
                    document.getElementById('apiStatus').className = 'status-dot error';
                });
            
            // Check models API
            fetch(MODELS_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: 'test', max_tokens: 1 })
            })
                .then(function(response) {
                    debugLog('Models API check success', 'success');
                    document.getElementById('modelsStatus').className = 'status-dot';
                })
                .catch(function(error) {
                    debugLog('Models API check failed: ' + error.message, 'error');
                    document.getElementById('modelsStatus').className = 'status-dot error';
                });
        }
        
        // Test connection manually
        function testConnection() {
            debugLog('Manual connection test started', 'info');
            
            // Test API
            fetch(API_BASE + '/health')
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    alert('API Connection OK!\n\nStatus: ' + data.status + '\nDatabase: ' + data.database);
                    debugLog('API test success: ' + JSON.stringify(data), 'success');
                })
                .catch(function(error) {
                    alert('API Connection Failed!\n\n' + error.message);
                    debugLog('API test failed: ' + error.message, 'error');
                });
            
            // Test Models
            fetch(MODELS_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: 'Hello', max_tokens: 10 })
            })
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    alert('Models API OK!\n\n' + JSON.stringify(data).substring(0, 200));
                    debugLog('Models test success', 'success');
                })
                .catch(function(error) {
                    alert('Models API Failed!\n\n' + error.message);
                    debugLog('Models test failed: ' + error.message, 'error');
                });
        }
        
        // Show message
        function showMessage(text, type) {
            debugLog('Message: ' + text + ' (type: ' + type + ')', type);
            var msg = document.getElementById('message');
            msg.textContent = text;
            msg.className = 'message ' + type;
            
            setTimeout(function() {
                msg.className = 'message';
            }, 5000);
        }
        
        // Switch tab
        function switchTab(tabName) {
            debugLog('Switching to tab: ' + tabName, 'info');
            
            // Update tabs
            var tabs = document.querySelectorAll('.tab');
            for (var i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active');
            }
            event.target.classList.add('active');
            
            // Update panels
            var panels = document.querySelectorAll('.tab-panel');
            for (var i = 0; i < panels.length; i++) {
                panels[i].classList.remove('active');
            }
            document.getElementById(tabName).classList.add('active');
            
            // Load data if needed
            if (tabName === 'manage') {
                loadPrompts();
            } else if (tabName === 'test') {
                loadTestPrompts();
            }
        }
        
        // Load prompts
        function loadPrompts() {
            debugLog('Loading prompts from API...', 'info');
            
            fetch(API_BASE + '/api/prompts')
                .then(function(response) {
                    debugLog('Prompts API response status: ' + response.status, 'info');
                    if (!response.ok) {
                        throw new Error('API returned status ' + response.status);
                    }
                    return response.json();
                })
                .then(function(data) {
                    debugLog('Prompts loaded: ' + JSON.stringify(data).substring(0, 200), 'success');
                    state.prompts = data.prompts || [];
                    displayPrompts();
                })
                .catch(function(error) {
                    debugLog('Failed to load prompts: ' + error.message, 'error');
                    console.error('Error:', error);
                    showMessage('Failed to load prompts: ' + error.message, 'error');
                    
                    // Show error in list
                    var list = document.getElementById('promptList');
                    list.innerHTML = '<div class="empty-state">' +
                        '<h3>Failed to load prompts</h3>' +
                        '<p>' + error.message + '</p>' +
                        '<button class="btn btn-primary" onclick="loadPrompts()">Retry</button>' +
                        '</div>';
                });
        }
        
        // Display prompts
        function displayPrompts() {
            debugLog('Displaying ' + state.prompts.length + ' prompts', 'info');
            
            var list = document.getElementById('promptList');
            
            if (state.prompts.length === 0) {
                list.innerHTML = '<div class="empty-state">' +
                    '<h3>No prompts found</h3>' +
                    '<p>Create your first prompt to get started</p>' +
                    '</div>';
                return;
            }
            
            var html = '';
            for (var i = 0; i < state.prompts.length; i++) {
                var prompt = state.prompts[i];
                var createdDate = '';
                if (prompt.created_at) {
                    createdDate = ' | Created: ' + new Date(prompt.created_at).toLocaleDateString();
                }
                
                html += '<div class="prompt-item">';
                html += '<div class="prompt-info">';
                html += '<h4>' + (prompt.name || 'Unnamed') + '</h4>';
                html += '<div class="meta">';
                html += 'Code: ' + prompt.code;
                html += ' | Category: ' + (prompt.category || 'general');
                html += createdDate;
                html += '</div>';
                html += '</div>';
                html += '<div class="prompt-actions">';
                html += '<button class="btn btn-secondary btn-small" onclick="editPrompt(\'' + prompt.code + '\')">Edit</button> ';
                html += '<button class="btn btn-info btn-small" onclick="testPromptQuick(\'' + prompt.code + '\')">Test</button> ';
                html += '<button class="btn btn-danger btn-small" onclick="deletePrompt(\'' + prompt.code + '\')">Delete</button>';
                html += '</div>';
                html += '</div>';
            }
            
            list.innerHTML = html;
        }
        
        // Save prompt
        function savePrompt() {
            debugLog('Saving prompt...', 'info');
            
            var code = document.getElementById('promptCode').value.trim();
            var name = document.getElementById('promptName').value.trim();
            var category = document.getElementById('promptCategory').value;
            var content = document.getElementById('promptContent').value.trim();
            
            // Validation
            if (!code || !name || !content) {
                showMessage('Please fill in all required fields', 'error');
                return;
            }
            
            // Validate code format
            if (!/^[a-z0-9_]+$/.test(code)) {
                showMessage('Prompt code must be lowercase letters, numbers, and underscores only', 'error');
                return;
            }
            
            var promptData = {
                code: code,
                name: name,
                category: category,
                content: content,
                description: 'Created from dashboard on ' + new Date().toLocaleDateString(),
                arguments: []
            };
            
            debugLog('Prompt data: ' + JSON.stringify(promptData), 'info');
            
            fetch(API_BASE + '/api/prompts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(promptData)
            })
                .then(function(response) {
                    debugLog('Save response status: ' + response.status, 'info');
                    return response.json();
                })
                .then(function(data) {
                    debugLog('Save response: ' + JSON.stringify(data), 'info');
                    
                    if (data.success || data.prompt_id) {
                        showMessage('Prompt "' + name + '" saved successfully!', 'success');
                        clearForm();
                        loadPrompts();
                        
                        // Switch to manage tab after save
                        setTimeout(function() {
                            var tabs = document.querySelectorAll('.tab');
                            tabs[1].click();
                        }, 1000);
                    } else {
                        showMessage('Failed to save: ' + (data.error || 'Unknown error'), 'error');
                    }
                })
                .catch(function(error) {
                    debugLog('Save error: ' + error.message, 'error');
                    console.error('Error:', error);
                    showMessage('Failed to save prompt: ' + error.message, 'error');
                });
        }
        
        // Clear form
        function clearForm() {
            document.getElementById('promptCode').value = '';
            document.getElementById('promptName').value = '';
            document.getElementById('promptCategory').value = 'general';
            document.getElementById('promptContent').value = '';
            debugLog('Form cleared', 'info');
        }
        
        // Edit prompt
        function editPrompt(code) {
            debugLog('Loading prompt for edit: ' + code, 'info');
            
            fetch(API_BASE + '/api/prompts/' + code)
                .then(function(response) {
                    return response.json();
                })
                .then(function(prompt) {
                    debugLog('Prompt loaded: ' + JSON.stringify(prompt).substring(0, 200), 'success');
                    
                    state.currentEditCode = code;
                    document.getElementById('editCode').value = prompt.code || code;
                    document.getElementById('editName').value = prompt.name || '';
                    document.getElementById('editCategory').value = prompt.category || 'general';
                    document.getElementById('editContent').value = prompt.content || prompt.description || '';
                    
                    document.getElementById('editModal').classList.add('active');
                })
                .catch(function(error) {
                    debugLog('Failed to load prompt: ' + error.message, 'error');
                    console.error('Error:', error);
                    showMessage('Failed to load prompt', 'error');
                });
        }
        
        // Update prompt
        function updatePrompt() {
            debugLog('Updating prompt: ' + state.currentEditCode, 'info');
            
            var updateData = {
                name: document.getElementById('editName').value,
                category: document.getElementById('editCategory').value,
                content: document.getElementById('editContent').value,
                description: document.getElementById('editContent').value.substring(0, 200)
            };
            
            fetch(API_BASE + '/api/prompts/' + state.currentEditCode, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updateData)
            })
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    debugLog('Update response: ' + JSON.stringify(data), 'info');
                    
                    if (data.success || !data.error) {
                        showMessage('Prompt updated successfully!', 'success');
                        closeModal();
                        loadPrompts();
                    } else {
                        showMessage('Failed to update: ' + (data.error || 'Unknown error'), 'error');
                    }
                })
                .catch(function(error) {
                    debugLog('Update error: ' + error.message, 'error');
                    console.error('Error:', error);
                    showMessage('Failed to update prompt', 'error');
                });
        }
        
        // Delete prompt
        function deletePrompt(code) {
            if (!confirm('Are you sure you want to delete prompt "' + code + '"?')) {
                return;
            }
            
            debugLog('Deleting prompt: ' + code, 'info');
            
            fetch(API_BASE + '/api/prompts/' + code, {
                method: 'DELETE'
            })
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    debugLog('Delete response: ' + JSON.stringify(data), 'info');
                    
                    if (data.success || !data.error) {
                        showMessage('Prompt deleted successfully!', 'success');
                        loadPrompts();
                    } else {
                        showMessage('Failed to delete: ' + (data.error || 'Unknown error'), 'error');
                    }
                })
                .catch(function(error) {
                    debugLog('Delete error: ' + error.message, 'error');
                    console.error('Error:', error);
                    showMessage('Failed to delete prompt', 'error');
                });
        }
        
        // Close modal
        function closeModal() {
            document.getElementById('editModal').classList.remove('active');
            state.currentEditCode = null;
        }
        
        // Load test prompts
        function loadTestPrompts() {
            debugLog('Loading prompts for testing...', 'info');
            
            fetch(API_BASE + '/api/prompts')
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    var select = document.getElementById('testPromptSelect');
                    select.innerHTML = '<option value="">-- Select a prompt --</option>';
                    
                    var prompts = data.prompts || [];
                    for (var i = 0; i < prompts.length; i++) {
                        var option = document.createElement('option');
                        option.value = prompts[i].code;
                        option.textContent = (prompts[i].name || prompts[i].code) + ' (' + prompts[i].code + ')';
                        select.appendChild(option);
                    }
                    
                    debugLog('Loaded ' + prompts.length + ' prompts for testing', 'success');
                })
                .catch(function(error) {
                    debugLog('Failed to load test prompts: ' + error.message, 'error');
                    console.error('Error:', error);
                });
        }
        
        // Load prompt for test
        function loadPromptForTest() {
            var code = document.getElementById('testPromptSelect').value;
            
            if (!code) {
                document.getElementById('variableInputs').innerHTML = '';
                document.getElementById('testOutput').textContent = 'Select a prompt to begin testing...';
                return;
            }
            
            debugLog('Loading prompt for test: ' + code, 'info');
            
            fetch(API_BASE + '/api/prompts/' + code)
                .then(function(response) {
                    return response.json();
                })
                .then(function(prompt) {
                    debugLog('Test prompt loaded: ' + JSON.stringify(prompt).substring(0, 200), 'success');
                    
                    state.currentTestPrompt = prompt;
                    
                    // Get content
                    var content = prompt.content || prompt.prompt_content || prompt.description || '';
                    
                    if (!content) {
                        showMessage('This prompt has no content to test', 'error');
                        document.getElementById('variableInputs').innerHTML = '';
                        return;
                    }
                    
                    // Extract variables
                    var matches = content.match(/\{\{(\w+)\}\}/g) || [];
                    var variables = [];
                    var seen = {};
                    
                    for (var i = 0; i < matches.length; i++) {
                        var varName = matches[i].replace(/\{\{|\}\}/g, '');
                        if (!seen[varName]) {
                            seen[varName] = true;
                            variables.push(varName);
                        }
                    }
                    
                    debugLog('Found ' + variables.length + ' variables', 'info');
                    
                    // Generate input fields
                    var html = '';
                    if (variables.length > 0) {
                        html += '<h4 style="margin-bottom: 10px;">Input Variables:</h4>';
                        for (var i = 0; i < variables.length; i++) {
                            html += '<div class="variable-field">';
                            html += '<label>' + variables[i] + '</label>';
                            html += '<input type="text" id="var_' + variables[i] + '" placeholder="Enter ' + variables[i] + '">';
                            html += '</div>';
                        }
                    } else {
                        html += '<p style="color: #718096; font-style: italic;">No variables found in this prompt</p>';
                    }
                    
                    document.getElementById('variableInputs').innerHTML = html;
                    document.getElementById('testOutput').textContent = 'Ready to execute test...';
                })
                .catch(function(error) {
                    debugLog('Failed to load test prompt: ' + error.message, 'error');
                    console.error('Error:', error);
                    showMessage('Failed to load prompt', 'error');
                });
        }
        
        // Execute test
        function executeTest() {
            if (!state.currentTestPrompt) {
                showMessage('Please select a prompt first', 'error');
                return;
            }
            
            debugLog('Executing test...', 'info');
            
            // Get content
            var content = state.currentTestPrompt.content || state.currentTestPrompt.description || '';
            
            // Replace variables
            var inputs = document.querySelectorAll('#variableInputs input');
            for (var i = 0; i < inputs.length; i++) {
                var varName = inputs[i].id.replace('var_', '');
                var value = inputs[i].value;
                content = content.split('{{' + varName + '}}').join(value);
                debugLog('Replaced {{' + varName + '}} with: ' + value, 'info');
            }
            
            var model = document.getElementById('modelSelect').value;
            
            debugLog('Final prompt: ' + content.substring(0, 200), 'info');
            debugLog('Using model: ' + model, 'info');
            
            document.getElementById('testOutput').textContent = 'Executing test...\n\nModel: ' + model + '\n\nPlease wait...';
            
            fetch(MODELS_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: content,
                    model: model,
                    max_tokens: 1000,
                    temperature: 0.7
                })
            })
                .then(function(response) {
                    debugLog('Model response status: ' + response.status, 'info');
                    return response.json();
                })
                .then(function(data) {
                    debugLog('Model response: ' + JSON.stringify(data).substring(0, 200), 'success');
                    
                    if (data.success && data.response) {
                        var output = '=== TEST EXECUTION RESULT ===\n\n';
                        output += 'Model: ' + (data.model || model) + '\n';
                        output += 'Timestamp: ' + new Date().toLocaleString() + '\n';
                        output += '================================\n\n';
                        output += data.response;
                        
                        document.getElementById('testOutput').textContent = output;
                        showMessage('Test executed successfully!', 'success');
                    } else {
                        document.getElementById('testOutput').textContent = 'Error: ' + (data.error || 'No response generated');
                        showMessage('Test failed: ' + (data.error || 'Unknown error'), 'error');
                    }
                })
                .catch(function(error) {
                    debugLog('Test execution error: ' + error.message, 'error');
                    console.error('Error:', error);
                    document.getElementById('testOutput').textContent = 'Network Error: ' + error.message;
                    showMessage('Test failed: ' + error.message, 'error');
                });
        }
        
        // Quick test
        function testPromptQuick(code) {
            debugLog('Quick test for prompt: ' + code, 'info');
            
            // Switch to test tab
            var tabs = document.querySelectorAll('.tab');
            tabs[2].click();
            
            // Set the prompt after a delay
            setTimeout(function() {
                document.getElementById('testPromptSelect').value = code;
                loadPromptForTest();
            }, 100);
        }
        
        // ESC key to close modal
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeModal();
            }
        });
    </script>
</body>
</html>