"""
OpenAI service
Handles OpenAI API calls with function calling
"""

import json
import openai
from typing import Dict, Union, Optional
from config import CONFIG
from tools.definitions import OPENAI_TOOLS
from tools.executor import execute_tool

# DynamoDB for conversation history
try:
    import boto3
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    conversations_table = dynamodb.Table(CONFIG.get('DYNAMODB_TABLE', 'aap-conversations-prod'))
except Exception as e:
    print(f"WARNING: DynamoDB connection failed: {e}")
    conversations_table = None

# Initialize OpenAI
if CONFIG.get('OPENAI_API_KEY'):
    openai.api_key = CONFIG['OPENAI_API_KEY']


async def call_openai_with_tools(
    message: str, 
    conversation_id: str, 
    user: Dict
) -> Union[str, Dict]:
    """Call OpenAI with function calling enabled
    
    Returns:
        - If tools were used: dict with 'content', 'source'='mcp-tool', 'tools_used'
        - If no tools: dict with 'content', 'source'='openai-tools', 'tools_used'=[]
    """
    
    # Load conversation history
    history = []
    if conversations_table:
        try:
            response = conversations_table.get_item(Key={'conversationId': conversation_id})
            item = response.get('Item')
            if item and 'messages' in item:
                for msg in item.get('messages', [])[-20:]:
                    if msg.get('role') and msg.get('content'):
                        history.append({"role": msg['role'], "content": msg['content']})
                print(f"[Docs] Loaded {len(history)} messages from DynamoDB")
        except Exception as e:
            print(f"WARNING: Failed to load history: {e}")
    
    # Add current message
    history.append({"role": "user", "content": message})
    
    # System prompt - CRITICAL: Agent MUST call tools, never say "not connected"
    system_prompt = f"""You are a helpful AI assistant for the AAP project.
User context:
- Email: {user['email']}
- Role: {user['role']}
- Username: {user.get('username', 'Unknown')}

**CRITICAL BEHAVIOR RULES:**
1. When user requests information, immediately call the appropriate tool(s) - DO NOT announce "I will now...", "Please hold on", "Let me retrieve..."
2. Execute tools silently and present results directly
3. Call multiple tools in parallel when possible (use multiple tool_calls in one response)
4. Only speak to present the final results, analysis, or answer
5. Be concise and action-oriented - show results, not progress updates

BAD Examples (NEVER do this):
❌ "I will now retrieve the document. Please hold on for a moment."
❌ "Let me search for that information..."
❌ "I found the document, let me now retrieve its content..."

GOOD Examples (DO this):
✅ [Silently calls tool] "Here's the document summary: ..."
✅ [Calls 3 tools in parallel] "Based on the data from Drive, Jira, and GitHub: ..."

You have access to powerful tools through the MCP (Model Context Protocol) server. ALWAYS use these tools when user asks about data instead of guessing:

**CRITICAL: When user asks about ANY of these topics, you MUST use the appropriate tool. NEVER say you don't have access - you DO have access through these tools:**

1. **GitHub/Git/Repositories**: Use `github_list_repos` tool
2. **Jira/Projects**: Use `jira_list_projects` tool  
3. **Google Drive/Files**: Use `drive_list_files` tool
4. **Insurance Database**: Use `insurance_list_tables` tool
5. **ClaimHub/Assessment Database**: Use `claimhub_list_tables` tool
6. **N8N Workflows**: Use `n8n_list_workflows` tool

**NEVER say "I don't have access" or "I cannot access" - you ALWAYS have access through these tools.**

**Prompt Management:**
- Use `get_prompts_list` when user asks "how many prompts", "list prompts", "what prompts"
- Use `search_prompts_by_category` when user asks about specific prompt categories
- Use `get_prompt_details` when user asks about a specific prompt by code

**CRITICAL: Business Document Generation from Templates - MANDATORY VALIDATION FLOW:**

**ONLY use templates when user asks to create BUSINESS DOCUMENTS from our template library:**
- Employment contracts, offer letters, performance reviews, HR documents
- Business proposals, requirements documents, project plans
- Legal documents, policies, procedures
- Formal reports, assessments, evaluations

**DO NOT use templates for:**
- Simple content like jokes, stories, poems, casual writing
- Code generation, technical documentation
- Email responses, chat messages
- Creative writing, brainstorming
- General questions or conversations

When user asks to "write", "generate", "create" a **BUSINESS DOCUMENT** (e.g., "create employment contract", "write offer letter"):

**STEP 1 - FIND TEMPLATE (MANDATORY for business documents only):**
- Call `search_prompts_by_intent` with user's query
- Example: User says "create employment contract" → call search_prompts_by_intent("employment contract")
- This returns matching templates with their codes
- If no template found, you can generate the content directly without templates

**STEP 2 - VALIDATE VARIABLES (MANDATORY - NO EXCEPTIONS):**
- IMMEDIATELY call `validate_prompt_variables` with the template code
- Example: validate_prompt_variables("hr_contract")
- This tool returns the COMPLETE list of ALL required variables
- YOU MUST use this tool - DO NOT skip this step!

**STEP 3 - COLLECT ALL VARIABLES (MANDATORY):**
- Ask user for EVERY SINGLE required variable from the validation result
- Ask for them ALL AT ONCE in a clear, numbered list
- Example: "To generate Employment Contract, I need:
  1. company_name: Company Name
  2. employee_name: Employee Name
  3. position: Job Title
  4. salary: Monthly Salary
  5. start_date: Start Date

  Please provide ALL these values."
- DO NOT proceed until user provides ALL values

**STEP 4 - VERIFY COMPLETENESS (MANDATORY):**
- Check that user has provided ALL required variables
- If ANY variable is missing → Ask again for the missing ones
- DO NOT make up values, DO NOT use placeholders, DO NOT assume

**STEP 5 - GENERATE FINAL DOCUMENT (ONLY AFTER STEPS 1-4):**
- ONLY after you have 100% of required variables
- ❌ DO NOT SAY: "With all information complete, I will generate...", "Let me generate the document...", or wait for user to say "go"
- ✅ IMMEDIATELY call `generate_from_prompt_template` and present the complete document
- Fill the template with user's actual values
- Return COMPLETE document with NO placeholders like [Company Name] or {{variable}}

**ABSOLUTELY FORBIDDEN:**
- ❌ NEVER return template with placeholders like [Company Address] or {{variable}}
- ❌ NEVER skip calling validate_prompt_variables
- ❌ NEVER generate document without collecting ALL required variables
- ❌ NEVER make up or assume variable values
- ❌ NEVER say "please fill in the placeholders" - YOU must get the values first!
- ❌ NEVER announce "I will generate" in STEP 5 - JUST DO IT!

**Example CORRECT flow:**
User: "create employment contract"
You: [Call search_prompts_by_intent("employment contract")]
You: [Call validate_prompt_variables("hr_contract")]
You: "To generate Employment Contract, I need: 1. company_name, 2. employee_name, 3. position, 4. salary, 5. start_date. Please provide ALL these values."
User: "Ancileo, Gavin, Data Engineer, 2000 MYR, 12 months"
You: [Verify all 5 variables received] [IMMEDIATELY call generate_from_prompt_template] → [Present complete contract with NO placeholders, NO announcements]

**GitHub Integration:**
- Use `github_list_repos` when user asks "any project in github", "list repositories", "my github repos"
- Use `github_search_code` when user asks to search code
- Use `github_read_file` when user asks to read a file

**Jira Integration:**
- Use `jira_list_projects` when user asks "any project in jira", "list jira projects", "my jira projects"
- Use `jira_search_issues` when user asks about Jira issues
- Use `jira_get_issue` when user asks about a specific issue

**Google Drive Integration:**
- Use `drive_list_files` when user asks "any file in my drive", "list drive files", "my drive files", "files in drive"
- Use `drive_search_files` when user asks to search for files
- **CRITICAL**: Use `drive_read_file` when user wants to:
  * Read file content (e.g., "read this file", "show me the content")
  * Analyze file (e.g., "analyze this document", "analyze Business Requirements Document")
  * Summarize file (e.g., "summarize this doc", "what's in this file")
  * Extract information from file
  * ANY task that requires knowing the file's content
  * You MUST call `drive_read_file(file_id)` FIRST before analyzing/summarizing
  * DO NOT say "file type is unknown" - call the tool to actually read the content!

**Insurance Database (MySQL) - ANALYTICAL QUERY WORKFLOW:**

MANDATORY WORKFLOW for analytical questions (e.g., "how many accounts created today", "claims this week"):
1. **Discover schema**: Call `insurance_list_tables()` to see available tables
2. **Get table structure**: Call `insurance_get_table_schema(table_name)` to see column names and types
3. **Review schema**: Find the correct date/time column (created_at, updated_at, date_created, etc.)
4. **Generate MySQL query**: Use proper MySQL DATE functions and correct column names
5. **Execute**: Call `insurance_query(sql)` with the generated query

CRITICAL MySQL DATE Functions (DO NOT use PostgreSQL syntax):
- Today: `WHERE DATE(created_at) = CURDATE()`
- This week: `WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)`
- This month: `WHERE MONTH(created_at) = MONTH(CURDATE()) AND YEAR(created_at) = YEAR(CURDATE())`

Simple Queries (skip schema if table name is obvious):
- Use `insurance_list_tables` for "how many tables", "tables in insurance db"
- Use `insurance_query` for "SELECT * FROM known_table LIMIT 10"

**ClaimHub Database (PostgreSQL - database name: assessment) - ANALYTICAL QUERY WORKFLOW:**

MANDATORY WORKFLOW for analytical questions (e.g., "how many claims today", "assessments this month"):
1. **Discover schema**: Call `claimhub_list_tables()` to see available tables
2. **Get table structure**: Call `claimhub_get_table_schema(table_name)` to see column names and types
3. **Review schema**: Find the correct date/time column (created_at, updated_at, timestamp, etc.)
4. **Generate PostgreSQL query**: Use proper PostgreSQL DATE functions and correct column names
5. **Execute**: Call `claimhub_query(sql)` with the generated query

CRITICAL PostgreSQL DATE Functions (DO NOT use MySQL syntax):
- Today: `WHERE DATE(created_at) = CURRENT_DATE`
- This week: `WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'`
- This month: `WHERE DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE)`

Simple Queries (skip schema if table name is obvious):
- Use `claimhub_list_tables` for "how many tables", "tables in claimdb", "tables in assessment"
- Use `claimhub_query` for "SELECT * FROM known_table LIMIT 10"

IMPORTANT: "claimdb" refers to the ClaimHub database (assessment database)

**N8N Workflow Automation:**
- Use `n8n_list_workflows` when user asks "how many n8n wf do i have", "list n8n workflows", "my n8n workflows", "n8n workflows"
- Use `n8n_get_workflow` when user asks about a specific workflow
- Use `n8n_trigger_workflow` when user asks to run a workflow
- Use `n8n_create_workflow` when user wants to create a new workflow

**CRITICAL RULES - YOU MUST FOLLOW THESE EXACTLY:**

1. **MANDATORY TOOL USAGE - NEVER SAY "NOT CONNECTED"**:
   - If user asks "any file in my drive" → YOU MUST call `drive_list_files` tool. DO NOT say "not connected" - call the tool first!
   - If user asks "any project in jira" → YOU MUST call `jira_list_projects` tool. DO NOT say "not connected" - call the tool first!
   - If user asks "any project in git/github" → YOU MUST call `github_list_repos` tool. DO NOT say "not connected" - call the tool first!
   - If user asks "tables in claimdb/assessment" → YOU MUST call `claimhub_list_tables` tool. DO NOT say anything else!
   - If user asks "tables in insurance" → YOU MUST call `insurance_list_tables` tool. DO NOT say anything else!

2. **DATABASES ARE NOT GITHUB - ABSOLUTELY NEVER CONFUSE THEM**:
   - "tables in claimdb" = DATABASE query → use `claimhub_list_tables` tool. NEVER mention GitHub, git, repos, or code!
   - "tables in assessment" = DATABASE query → use `claimhub_list_tables` tool. NEVER mention GitHub!
   - "tables in insurance" = DATABASE query → use `insurance_list_tables` tool. NEVER mention GitHub!
   - Databases contain DATA (tables, records, rows). GitHub contains CODE (files, repositories). They are COMPLETELY DIFFERENT!

3. **GITHUB IS FOR CODE ONLY**:
   - "any project in git/github" = GITHUB query → use `github_list_repos` tool
   - "repositories" or "repos" = GITHUB query → use `github_list_repos` tool
   - GitHub is for CODE repositories, NOT databases!

4. **YOU MUST ALWAYS USE TOOLS - NEVER GUESS**:
   - When user asks about integrations, databases, or GitHub → YOU MUST call the appropriate tool
   - DO NOT say "I don't have access" or "not connected" without calling the tool first
   - The tools will return real data or error messages - let the tools tell you, don't guess!

5. **EXAMPLES OF CORRECT BEHAVIOR**:
   - User: "any file in my drive" → YOU MUST call `drive_list_files` tool → Return the tool result
   - User: "tables in claimdb" → YOU MUST call `claimhub_list_tables` tool → Return the tool result (NEVER mention GitHub!)
   - User: "any project in github" → YOU MUST call `github_list_repos` tool → Return the tool result

6. **REMEMBER**: You have access to all these tools through the MCP server. Always use them instead of guessing or saying "not connected".

7. **RESPONSE LENGTH & INTELLIGENCE**:
   - You have 8000 tokens for responses - use them wisely to provide comprehensive, detailed answers
   - For long prompts or complex queries, provide thorough, well-structured explanations with:
     * Clear context and background information
     * Step-by-step instructions when applicable
     * Real examples and use cases
     * Best practices and recommendations
     * Common pitfalls and how to avoid them
   - Use bullet points, numbered lists, sections, and formatting for better readability
   - Structure long responses with: Summary → Detailed Explanation → Examples → Best Practices
   - Be concise for simple questions, but comprehensive for complex topics
   - When explaining prompts, workflows, or technical concepts:
     * Explain what it does and why it matters
     * Provide multiple examples in different contexts
     * Include troubleshooting tips
     * Link related concepts together
   - Always prioritize being helpful and thorough - users appreciate detailed, actionable information
   - If explaining a complex prompt, break it down into parts: purpose, variables, expected output, use cases"""

    messages = [{"role": "system", "content": system_prompt}] + history

    # CRITICAL: Validate messages array to prevent silent bot failures
    # Check that all messages have required fields and correct structure
    try:
        for i, msg in enumerate(messages):
            if not isinstance(msg, dict):
                print(f"[ERROR] Message at index {i} is not a dict: {type(msg)}")
                raise ValueError(f"Invalid message format at index {i}: expected dict, got {type(msg)}")

            if "role" not in msg:
                print(f"[ERROR] Message at index {i} missing 'role' field: {msg}")
                raise ValueError(f"Message at index {i} missing required 'role' field")

            if msg["role"] not in ["system", "user", "assistant", "tool"]:
                print(f"[ERROR] Message at index {i} has invalid role: {msg['role']}")
                raise ValueError(f"Message at index {i} has invalid role: {msg['role']}")

            # Check content field for non-tool messages
            if msg["role"] != "tool" and "content" not in msg:
                print(f"[ERROR] Message at index {i} missing 'content' field: {msg}")
                raise ValueError(f"Message at index {i} missing required 'content' field")

            # Validate tool messages have required fields
            if msg["role"] == "tool":
                if "tool_call_id" not in msg:
                    print(f"[ERROR] Tool message at index {i} missing 'tool_call_id': {msg}")
                    raise ValueError(f"Tool message at index {i} missing required 'tool_call_id' field")
                if "name" not in msg:
                    print(f"[ERROR] Tool message at index {i} missing 'name': {msg}")
                    raise ValueError(f"Tool message at index {i} missing required 'name' field")
                if "content" not in msg:
                    print(f"[ERROR] Tool message at index {i} missing 'content': {msg}")
                    raise ValueError(f"Tool message at index {i} missing required 'content' field")

        print(f"[OK] Message array validation passed: {len(messages)} messages")
    except ValueError as validation_error:
        print(f"[CRITICAL] Message array validation failed: {validation_error}")
        raise

    # SIMPLIFIED Force Tool Detection
    # Only force when user explicitly asks about integration data
    user_message_lower = message.lower()

    def detect_integration_query(msg: str) -> bool:
        """
        Detect if message is asking about integration data.
        Returns True if we should force OpenAI to use a tool, False otherwise.

        Strategy: Force tool_choice="required" when user asks about integrations.
        Let OpenAI choose the right tool (list vs query vs search).
        """
        msg = msg.lower()

        # Google Drive queries
        if "drive" in msg or "gdrive" in msg or "google drive" in msg:
            return True

        # GitHub / Git queries
        if "github" in msg or "git" in msg or ("repo" in msg and ("my" in msg or "list" in msg or "show" in msg)):
            return True

        # Jira queries
        if "jira" in msg:
            return True

        # ClaimHub/ClaimDB queries (both list tables and data queries)
        if "claimdb" in msg or "claimhub" in msg or "claim hub" in msg:
            return True

        # Insurance DB queries (both list tables and data queries)
        if "insurance" in msg and ("db" in msg or "database" in msg or "table" in msg or "data" in msg or "query" in msg):
            return True

        # N8N queries
        if "n8n" in msg or "workflow" in msg:
            return True

        return False

    force_tool = detect_integration_query(user_message_lower)

    if force_tool:
        print(f"[ALERT] INTEGRATION QUERY DETECTED - Forcing tool usage")
        print(f"[ALERT] Query: {message[:100]}")

    # MULTI-TURN TOOL CALLING: Allow LLM to call tools iteratively (up to 5 rounds)
    # This enables complex workflows like: get_schema → query → analyze_results
    # When force_tool=True, require OpenAI to call at least one tool on first iteration
    MAX_ITERATIONS = 5
    iteration = 0
    tool_calls_made = []

    tool_choice_param = "required" if force_tool else "auto"

    while iteration < MAX_ITERATIONS:
        iteration += 1
        print(f"[OpenAI] Iteration {iteration}/{MAX_ITERATIONS}")
        print(f"[OpenAI] Message count: {len(messages)}, tool_choice: {tool_choice_param}")
        if iteration == 1:
            print(f"[OpenAI] User message: {message[:100]}...")

        try:
            response = openai.ChatCompletion.create(
                model=CONFIG.get('OPENAI_MODEL', 'gpt-4o-mini'),
                messages=messages,
                tools=OPENAI_TOOLS,
                tool_choice=tool_choice_param,
                temperature=0.7,
                max_tokens=8000  # Increased for very long responses
            )
            print(f"[OpenAI] Call succeeded")
        except Exception as api_error:
            print(f"[ERROR] OpenAI API call failed on iteration {iteration}: {api_error}")
            print(f"[ERROR] Error type: {type(api_error).__name__}")
            import traceback
            traceback.print_exc()

            # If tools were already executed, return partial results
            if tool_calls_made:
                partial_summary = f"I executed {len(tool_calls_made)} tool(s): {', '.join(tool_calls_made)}. However, I encountered an API error: {type(api_error).__name__}. Please try again."
                return {
                    "content": partial_summary,
                    "source": "mcp-tool",
                    "tools_used": tool_calls_made
                }
            raise

        response_message = response.choices[0].message

        # Check if LLM wants to call more tools
        # Use getattr() to safely check for tool_calls attribute (may not exist if no tools called)
        tool_calls = getattr(response_message, 'tool_calls', None)
        if tool_calls:
            print(f"[Tool] Tool calls requested: {len(response_message.tool_calls)}")

            # Convert OpenAI message object to dict before appending
            assistant_message_dict = {
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in response_message.tool_calls
                ]
            }
            messages.append(assistant_message_dict)

            # Execute each tool call with error handling
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Failed to parse tool arguments for {tool_name}: {e}")
                    tool_args = {}

                print(f"  -> Executing: {tool_name}({tool_args})")

                # Execute tool with error handling
                try:
                    print(f"[Tool] [execute_tool] Calling {tool_name} with args: {tool_args}")
                    tool_result = await execute_tool(tool_name, tool_args, user)
                    # Ensure tool_result is a string
                    if not isinstance(tool_result, str):
                        tool_result = str(tool_result) if tool_result else "Tool execution returned empty result"
                    print(f"[OK] [execute_tool] {tool_name} returned: {tool_result[:200]}...")
                except Exception as tool_error:
                    print(f"[ERROR] Tool {tool_name} failed: {tool_error}")
                    import traceback
                    traceback.print_exc()
                    # Return error message that Agent can understand
                    tool_result = f"Error: {tool_name} failed - {str(tool_error)}. Please check if the integration is connected properly."

                tool_calls_made.append(tool_name)

                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": tool_result
                })

            # After first iteration, switch to "auto" to let LLM decide when to stop
            tool_choice_param = "auto"

            # Continue loop - LLM may call more tools or return final response
            continue
        else:
            # No more tool calls - LLM has final response
            print(f"[OpenAI] No more tool calls, returning final response")
            print(f"[OpenAI] Total tools executed: {', '.join(tool_calls_made) if tool_calls_made else 'none'}")

            # Validate content is not None or empty
            result_content = response_message.content
            if not result_content or result_content.strip() == "":
                if tool_calls_made:
                    # If tools were called, create summary
                    result_content = f"I executed {len(tool_calls_made)} tool(s): {', '.join(tool_calls_made)}. Please check the results above."
                else:
                    print(f"[WARNING] OpenAI returned empty content with no tools called")
                    result_content = "I apologize, but I was unable to generate a response. Please try rephrasing your question or provide more details."

            return {
                "content": result_content,
                "source": "mcp-tool" if tool_calls_made else "openai-tools",
                "tools_used": tool_calls_made
            }

    # Max iterations reached - return final response
    print(f"[WARNING] Max iterations ({MAX_ITERATIONS}) reached")
    print(f"[OpenAI] Total tools executed: {', '.join(tool_calls_made)}")

    # Return last response even if max iterations reached
    return {
        "content": "I executed multiple tool calls but reached the maximum iteration limit. Please try breaking your request into smaller steps.",
        "source": "mcp-tool",
        "tools_used": tool_calls_made
    }

