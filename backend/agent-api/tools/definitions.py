"""
OpenAI Function Calling Tools Definitions
All available tools that the LLM can use
"""

OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_prompts_list",
            "description": "Get list of all available prompt templates. Use when user asks 'how many prompts', 'list prompts', 'what prompts do we have', etc.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_prompt_details",
            "description": "Get detailed information about a specific prompt by its code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt_code": {
                        "type": "string",
                        "description": "The prompt code identifier (e.g., 'hr_offer_letter_detailed')"
                    }
                },
                "required": ["prompt_code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_prompts_by_category",
            "description": "Search prompts by category or keyword. Use when user asks about specific types (e.g., 'HR templates', 'Business Analysis docs').",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Keyword to search for in prompt names and categories"
                    }
                },
                "required": ["keyword"]
            }
        }
    },
    # GitHub MCP Tools
    {
        "type": "function",
        "function": {
            "name": "github_list_repos",
            "description": "List all GitHub repositories for the user. CRITICAL: ALWAYS use this tool when user asks about GitHub, git, repositories, code projects, or any question related to version control or code hosting. This tool connects to the user's GitHub account and retrieves their repositories. Use this tool whenever user mentions GitHub, git, repositories, repos, code projects, or asks about their code or projects. NEVER say 'not connected' or 'I don't have access' - you MUST call this tool first to check the actual connection status. The tool will return real data if connected, or an error message if not connected - let the tool tell you, don't guess!",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "github_search_code",
            "description": "Search code across GitHub repositories. Use when user wants to find specific code, functions, or files in their repos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'OAuth', 'function login', 'class User')"
                    },
                    "repo": {
                        "type": "string",
                        "description": "Optional: specific repository to search (format: owner/repo)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "github_read_file",
            "description": "Read file contents from a GitHub repository. Use when user asks to see code, read a file, or check file contents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository full name (format: owner/repo)"
                    },
                    "path": {
                        "type": "string",
                        "description": "File path in repository (e.g., 'src/main.py')"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch name (default: main)"
                    }
                },
                "required": ["repo", "path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "github_scan_repo",
            "description": "Scan entire GitHub repository and return all code files. Use when user asks to 'scan all code', 'read all files', 'show me all code in repo', 'analyze entire repository', 'scan repository', or wants to see the full codebase structure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {
                        "type": "string",
                        "description": "Repository full name (format: owner/repo)"
                    },
                    "branch": {
                        "type": "string",
                        "description": "Branch name (default: main)"
                    },
                    "max_files": {
                        "type": "integer",
                        "description": "Maximum number of files to scan (default: 100)"
                    }
                },
                "required": ["repo"]
            }
        }
    },
    # Jira MCP Tools
    {
        "type": "function",
        "function": {
            "name": "jira_list_projects",
            "description": "List all Jira projects the user has access to. CRITICAL: ALWAYS use this tool when user asks about Jira, project management, issues, tickets, or any question related to Jira or Atlassian. This tool connects to the user's Jira account and retrieves their projects. Use this tool whenever user mentions Jira, projects, issues, tickets, or asks about project management. NEVER say 'not connected' or 'I don't have access' - you MUST call this tool first to check the actual connection status. The tool will return real data if connected, or an error message if not connected - let the tool tell you, don't guess!",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "jira_search_issues",
            "description": "DEPRECATED: Use jira_api_call with endpoint '/search/jql' instead. This tool uses old API and WILL FAIL (410 Gone). For JQL searches, use: jira_api_call(endpoint='/search/jql', method='GET', params={'jql': 'your query', 'maxResults': 50})",
            "parameters": {
                "type": "object",
                "properties": {
                    "jql": {
                        "type": "string",
                        "description": "JQL query (e.g., 'project = AAP AND status = Open', 'assignee = currentUser()')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum results to return (default: 50)"
                    }
                },
                "required": ["jql"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "jira_get_issue",
            "description": "Get detailed information about a specific Jira issue. Use when user asks about a specific ticket by key.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Issue key (e.g., 'AAP-123', 'PROJ-456')"
                    }
                },
                "required": ["issue_key"]
            }
        }
    },
    # Insurance Database Tools (MySQL)
    {
        "type": "function",
        "function": {
            "name": "insurance_list_tables",
            "description": "List all tables in the Insurance database. CRITICAL: ALWAYS use this tool when user asks about insurance database, insurance db, or database tables. Use when user asks 'how many database do i have', 'tables in insurance', 'how many tables in insurance db', 'insurance database tables', 'how many tables in insurance database', 'insurance db tables', 'any tables in insurance', 'tables in my insurancedb', 'list insurance tables', or mentions 'insurance database' or 'insurance db'. NEVER say you don't have access - you DO have access through this tool.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "insurance_get_table_schema",
            "description": "Get detailed schema (column names, data types, nullable, keys) for a specific Insurance database table. MANDATORY: ALWAYS call this tool after insurance_list_tables and BEFORE insurance_query to understand table structure. This helps you generate correct SQL with proper column names and avoid errors.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Table name from insurance_list_tables (e.g., 'account', 'claim', 'policy')"
                    }
                },
                "required": ["table_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "insurance_query",
            "description": """Execute SELECT query on Insurance database (MySQL). FULL SQL SUPPORT including JOINs, subqueries, CTEs, window functions.

DATABASE TYPE: MySQL 8.0+ (Full Advanced SQL Support)

MANDATORY WORKFLOW FOR ANALYTICAL QUERIES:
1. Call insurance_list_tables() to see available tables
2. Call insurance_get_table_schema(table_name) to see columns/types for ALL tables you need
3. Review schema to find correct column names, foreign keys, relationships
4. Generate MySQL-compatible SELECT query with proper syntax

MYSQL DATE/TIME FUNCTIONS:
- Today: WHERE DATE(created_at) = CURDATE()
- This week: WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
- This month: WHERE MONTH(created_at) = MONTH(CURDATE()) AND YEAR(created_at) = YEAR(CURDATE())
- Yesterday: WHERE DATE(created_at) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
- Last 30 days: WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
- Specific date: WHERE DATE(created_at) = '2025-11-19'

BASIC QUERY EXAMPLES:
- Count today: SELECT COUNT(*) FROM account WHERE DATE(created_at) = CURDATE()
- Count this week: SELECT COUNT(*) FROM claim WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
- Group by date: SELECT DATE(created_at) as date, COUNT(*) as count FROM account WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) GROUP BY DATE(created_at) ORDER BY date
- Group by status: SELECT status, COUNT(*) as count FROM claim GROUP BY status
- Recent records: SELECT * FROM account ORDER BY created_at DESC LIMIT 10

⭐ ADVANCED SQL FEATURES (FULLY SUPPORTED):

1. CROSS-TABLE JOINS (Get schema first to find join keys):
   - INNER JOIN: SELECT a.*, c.* FROM account a INNER JOIN claim c ON a.id = c.account_id
   - LEFT JOIN: SELECT a.name, COUNT(c.id) as claim_count FROM account a LEFT JOIN claim c ON a.id = c.account_id GROUP BY a.id, a.name
   - Multiple JOINs: SELECT a.*, c.*, p.* FROM account a JOIN claim c ON a.id = c.account_id JOIN policy p ON c.policy_id = p.id

2. SUBQUERIES:
   - WHERE IN: SELECT * FROM account WHERE id IN (SELECT account_id FROM claim WHERE status = 'approved')
   - FROM subquery: SELECT status, AVG(claim_count) FROM (SELECT account_id, status, COUNT(*) as claim_count FROM claim GROUP BY account_id, status) AS counts GROUP BY status
   - Correlated: SELECT a.*, (SELECT COUNT(*) FROM claim c WHERE c.account_id = a.id) as total_claims FROM account a

3. CTEs (WITH clause) - Use for complex multi-step queries:
   - Basic: WITH active_accounts AS (SELECT * FROM account WHERE status = 'active') SELECT * FROM active_accounts WHERE created_at > CURDATE()
   - Multiple CTEs: WITH claims_count AS (SELECT account_id, COUNT(*) as cnt FROM claim GROUP BY account_id), high_volume AS (SELECT * FROM claims_count WHERE cnt > 10) SELECT a.*, h.cnt FROM account a JOIN high_volume h ON a.id = h.account_id

4. WINDOW FUNCTIONS (Analytical queries):
   - Ranking: SELECT *, ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at DESC) as rank_in_status FROM claim
   - Running totals: SELECT *, SUM(amount) OVER (ORDER BY created_at) as running_total FROM claim
   - LAG/LEAD: SELECT *, amount - LAG(amount) OVER (ORDER BY created_at) as change_from_previous FROM claim

5. ADVANCED AGGREGATIONS:
   - HAVING clause: SELECT status, COUNT(*) as cnt FROM claim GROUP BY status HAVING cnt > 100
   - COUNT DISTINCT: SELECT COUNT(DISTINCT account_id) as unique_accounts FROM claim
   - Multiple aggregates: SELECT status, COUNT(*) as total, AVG(amount) as avg_amount, MAX(amount) as max_amount FROM claim GROUP BY status

6. UNION/UNION ALL (Combine results):
   - UNION: SELECT id, name, 'account' as type FROM account UNION SELECT id, policy_number as name, 'policy' as type FROM policy
   - UNION ALL (keeps duplicates): SELECT account_id FROM claim WHERE status = 'pending' UNION ALL SELECT account_id FROM claim WHERE status = 'approved'

7. COMPLEX ANALYTICAL PATTERNS:
   - Top N per group: WITH ranked AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY amount DESC) as rn FROM claim) SELECT * FROM ranked WHERE rn <= 5
   - Period comparison: SELECT DATE(created_at) as date, COUNT(*) as today_count, LAG(COUNT(*)) OVER (ORDER BY DATE(created_at)) as yesterday_count FROM claim GROUP BY DATE(created_at)
   - Cohort analysis: SELECT DATE_FORMAT(created_at, '%Y-%m') as cohort, status, COUNT(*) FROM account GROUP BY cohort, status

QUERY BEST PRACTICES:
- For multi-table queries: ALWAYS check schema first to find correct join keys (id, account_id, policy_id, etc.)
- Use JOINs instead of multiple queries when relating data across tables
- Use CTEs for readability when query has multiple steps
- Use window functions for rankings, running totals, period-over-period comparisons
- Add LIMIT clause for exploratory queries to avoid huge result sets
- Use proper indexes awareness: Queries on indexed columns (id, created_at, status) are faster

IMPORTANT:
- Always use DATE(datetime_column) when comparing dates
- Use CURDATE() for today's date (not CURRENT_DATE or NOW())
- Column names are case-sensitive in MySQL
- Check schema first for multi-table queries to find join keys
- MySQL 8.0+ supports all advanced features (CTEs, window functions, etc.)""",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL SELECT query (MySQL syntax only). Must start with SELECT. No DROP/DELETE/UPDATE/INSERT allowed."
                    }
                },
                "required": ["sql"]
            }
        }
    },
    # N8N Workflow Tools
    {
        "type": "function",
        "function": {
            "name": "n8n_list_workflows",
            "description": "List all available n8n workflows. Use when user asks 'how many n8n wf do i have', 'list n8n workflows', 'my n8n workflows', 'n8n workflows', 'what workflows are available', or 'show me workflows'.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "n8n_create_workflow",
            "description": "Create/import a new n8n workflow from JSON. Use when user wants to add a new workflow, import a workflow, or create automation. The workflow will be imported, activated, and ready to use.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_json": {
                        "type": "object",
                        "description": "The n8n workflow JSON object (must be valid n8n workflow format with nodes, connections, etc.)"
                    },
                    "activate": {
                        "type": "boolean",
                        "description": "Automatically activate the workflow after import (default: true)"
                    },
                    "execute_after_create": {
                        "type": "boolean",
                        "description": "Execute the workflow immediately after creating it (default: false)"
                    },
                    "initial_payload": {
                        "type": "object",
                        "description": "Optional: Initial payload to send if execute_after_create is true"
                    }
                },
                "required": ["workflow_json"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "n8n_get_workflow",
            "description": "Get detailed information about a specific n8n workflow by workflow ID. Use when user asks for workflow details, workflow configuration, or to inspect a workflow.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "The n8n workflow ID"
                    }
                },
                "required": ["workflow_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "n8n_update_workflow",
            "description": "Update an existing n8n workflow. Use when user wants to modify a workflow, update workflow configuration, or change workflow nodes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "The n8n workflow ID to update"
                    },
                    "workflow_json": {
                        "type": "object",
                        "description": "The updated n8n workflow JSON object (must include id, name, nodes, connections, etc.)"
                    },
                    "activate": {
                        "type": "boolean",
                        "description": "Whether to activate the workflow after update (optional)"
                    }
                },
                "required": ["workflow_id", "workflow_json"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "n8n_delete_workflow",
            "description": "Delete an n8n workflow by workflow ID. Use when user wants to remove a workflow.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "The n8n workflow ID to delete"
                    }
                },
                "required": ["workflow_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "n8n_activate_workflow",
            "description": "Activate or deactivate an n8n workflow. Use when user wants to enable/disable a workflow.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "The n8n workflow ID"
                    },
                    "active": {
                        "type": "boolean",
                        "description": "True to activate, false to deactivate (default: true)"
                    }
                },
                "required": ["workflow_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "n8n_trigger_workflow",
            "description": "Trigger an n8n workflow by workflow ID. Use when user asks to run a workflow, execute automation, or trigger n8n process. First use n8n_list_workflows to find available workflow IDs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "The n8n workflow ID (e.g., 'demo-workflow', 'drive-file-notification', 'cypress-runner-workflow'). Use n8n_list_workflows to see available IDs."
                    },
                    "payload": {
                        "type": "object",
                        "description": "Optional: Data to send to the workflow (JSON object)"
                    }
                },
                "required": ["workflow_id"]
            }
        }
    },
    # ClaimHub Database Tools (PostgreSQL)
    {
        "type": "function",
        "function": {
            "name": "claimhub_list_tables",
            "description": "List all tables in the ClaimHub database (database name: assessment). ALWAYS use this tool when user asks about databases, assessment database, or claimdb. Use when user asks 'how many database do i have', 'the database assessment', 'how many tables', 'tables in assessment', 'how many tables in claimdb', 'tables in claimdb', 'claimdb tables', 'claimhub database tables', 'assessment database', or mentions 'assessment' or 'claimdb' database.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "claimhub_get_table_schema",
            "description": """Get detailed schema for ClaimHub table - returns columns, types, nullability, AND SAMPLE DATA for semantic understanding.

**CRITICAL: This tool is your DATABASE INTELLIGENCE - use it to understand what data actually means!**

**MANDATORY WORKFLOW (DO THIS EVERY TIME):**
1. Call claimhub_get_table_schema(table_name) for EVERY table involved in the query
2. **ANALYZE the schema response carefully:**
   - Look at column names and guess their purpose
   - Check data types (timestamp = dates, integer = IDs/counts, varchar = text)
   - Look for patterns: created_at, updated_at, *_date, *_time, *_at columns
   - Identify relationships: user_id, account_id, claim_id = foreign keys
3. **CRITICAL: If unsure about column meaning, run a SAMPLE query FIRST:**
   ```sql
   SELECT column1, column2, column3 FROM table_name LIMIT 5
   ```
   This shows you REAL DATA so you understand what each column contains!

4. **AFTER reviewing schema + sample data, TELL THE USER what you found** before running the real query

**EXAMPLE - How to handle "claims received yesterday":**

WRONG WAY (what you might do without this):
```sql
-- ❌ WRONG: Guessed policy_purchased_at without checking!
SELECT COUNT(*) FROM claim WHERE DATE(policy_purchased_at) = CURRENT_DATE - INTERVAL '1 day'
```

RIGHT WAY (intelligent approach):
```
Step 1: Call claimhub_get_table_schema('claim')
Step 2: Review columns - see: id, user_id, status, amount, policy_purchased_at, created_at, updated_at
Step 3: Realize: "claims received" = when claim was created, not when policy was purchased!
Step 4: To be 100% sure, run: SELECT created_at, policy_purchased_at, status FROM claim LIMIT 3
Step 5: Confirm created_at is claim submission date
Step 6: Tell user: "I found the 'claim' table has a created_at column for when claims were submitted. Let me count yesterday's claims."
Step 7: Run correct query:
SELECT COUNT(*) FROM claim WHERE DATE(created_at) = CURRENT_DATE - INTERVAL '1 day'
```

**SEMANTIC COLUMN ANALYSIS (Learn to read column names!):**
- *_at, *_date, *_time = Dates/timestamps
  - created_at = when record was created
  - updated_at = when record was last modified
  - submitted_at = when something was submitted
  - approved_at = when something was approved
  - purchased_at = when something was bought
- *_id = Foreign keys or identifiers
- *_status, *_state = Status/state columns
- *_amount, *_total, *_price = Monetary values
- *_count, *_number = Counts or quantities

**REMEMBER: Column names tell you WHAT the data is. Sample data shows you HOW it's used. Use both!**

This helps you generate correct SQL with proper column names and semantic understanding.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Table name from claimhub_list_tables (e.g., 'claim', 'assessment', 'user')"
                    }
                },
                "required": ["table_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "claimhub_query",
            "description": """Execute SELECT query on ClaimHub database (PostgreSQL, database: assessment). FULL SQL SUPPORT including JOINs, subqueries, CTEs, window functions, recursive queries, LATERAL joins, JSON aggregation.

DATABASE TYPE: PostgreSQL (Full Advanced SQL Support + PostgreSQL-Specific Features)

🚨 **CRITICAL COMMUNICATION RULE:** 🚨
AFTER calling claimhub_list_tables() or claimhub_get_table_schema(), you MUST:
1. **TELL THE USER** what you found in the schema
2. **EXPLAIN** your understanding of the data (which columns match their question)
3. **DESCRIBE** what SQL query you're going to run
4. **THEN** execute the query

❌ NEVER call tools and stay silent!
❌ NEVER say "Let me read..." without actually reading!
✅ ALWAYS communicate your findings and plan before executing!

**Example of correct behavior:**
User: "How many claims yesterday?"
You: "Let me check the claim table schema to find the right date column."
[Call claimhub_get_table_schema('claim')]
You: "I found the 'claim' table has these date columns: created_at (when claim was submitted), updated_at (last modified), and policy_purchased_at (when insurance was bought). For 'claims received yesterday', I'll use created_at since that's when the claim was submitted. Running the query now..."
[Call claimhub_query with correct SQL]
You: "I found X claims submitted yesterday!"

MANDATORY WORKFLOW FOR ANALYTICAL QUERIES:
1. Call claimhub_list_tables() to see available tables
2. **TELL USER what tables you found**
3. Call claimhub_get_table_schema(table_name) to see columns/types for ALL tables you need
4. **ANALYZE schema and EXPLAIN to user which columns match their question**
5. If unsure, run sample query (SELECT * FROM table LIMIT 3) to see real data
6. **DESCRIBE your SQL approach to the user**
7. Generate PostgreSQL-compatible SELECT query with proper syntax
8. **PRESENT results to user with context**

POSTGRESQL DATE/TIME FUNCTIONS:
- Today: WHERE DATE(created_at) = CURRENT_DATE
- This week: WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
- This month: WHERE DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE)
- Yesterday: WHERE DATE(created_at) = CURRENT_DATE - INTERVAL '1 day'
- Last 30 days: WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
- Specific date: WHERE DATE(created_at) = '2025-11-19'
- Date series: SELECT generate_series(CURRENT_DATE - INTERVAL '7 days', CURRENT_DATE, '1 day'::interval) as date

BASIC QUERY EXAMPLES:
- Count today: SELECT COUNT(*) FROM claim WHERE DATE(created_at) = CURRENT_DATE
- Count this week: SELECT COUNT(*) FROM claim WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
- Group by date: SELECT DATE(created_at) as date, COUNT(*) as count FROM claim WHERE created_at >= CURRENT_DATE - INTERVAL '7 days' GROUP BY DATE(created_at) ORDER BY date
- Group by status: SELECT status, COUNT(*) as count FROM claim GROUP BY status
- Recent records: SELECT * FROM claim ORDER BY created_at DESC LIMIT 10

⭐ ADVANCED SQL FEATURES (FULLY SUPPORTED):

1. CROSS-TABLE JOINS (Get schema first to find join keys):
   - INNER JOIN: SELECT c.*, a.* FROM claim c INNER JOIN assessment a ON c.id = a.claim_id
   - LEFT JOIN: SELECT c.id, c.status, COUNT(a.id) as assessment_count FROM claim c LEFT JOIN assessment a ON c.id = a.claim_id GROUP BY c.id, c.status
   - Multiple JOINs: SELECT c.*, a.*, u.* FROM claim c JOIN assessment a ON c.id = a.claim_id JOIN "user" u ON c.user_id = u.id

2. SUBQUERIES:
   - WHERE IN: SELECT * FROM claim WHERE id IN (SELECT claim_id FROM assessment WHERE status = 'completed')
   - FROM subquery: SELECT status, AVG(claim_count) FROM (SELECT user_id, status, COUNT(*) as claim_count FROM claim GROUP BY user_id, status) AS counts GROUP BY status
   - Correlated: SELECT c.*, (SELECT COUNT(*) FROM assessment a WHERE a.claim_id = c.id) as total_assessments FROM claim c

3. CTEs (WITH clause) - PostgreSQL has excellent CTE support:
   - Basic: WITH active_claims AS (SELECT * FROM claim WHERE status = 'active') SELECT * FROM active_claims WHERE created_at > CURRENT_DATE
   - Multiple CTEs: WITH claim_counts AS (SELECT user_id, COUNT(*) as cnt FROM claim GROUP BY user_id), high_volume AS (SELECT * FROM claim_counts WHERE cnt > 10) SELECT u.*, h.cnt FROM "user" u JOIN high_volume h ON u.id = h.user_id
   - Recursive CTE: WITH RECURSIVE hierarchy AS (SELECT id, parent_id, name FROM category WHERE parent_id IS NULL UNION ALL SELECT c.id, c.parent_id, c.name FROM category c JOIN hierarchy h ON c.parent_id = h.id) SELECT * FROM hierarchy

4. WINDOW FUNCTIONS (PostgreSQL excels at these):
   - Ranking: SELECT *, ROW_NUMBER() OVER (PARTITION BY status ORDER BY created_at DESC) as rank_in_status FROM claim
   - Running totals: SELECT *, SUM(amount) OVER (ORDER BY created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as running_total FROM claim
   - LAG/LEAD: SELECT *, amount - LAG(amount) OVER (ORDER BY created_at) as change_from_previous FROM claim
   - NTILE for percentiles: SELECT *, NTILE(4) OVER (ORDER BY amount) as quartile FROM claim
   - FIRST_VALUE/LAST_VALUE: SELECT *, FIRST_VALUE(amount) OVER (PARTITION BY status ORDER BY created_at) as first_amount FROM claim

5. ADVANCED AGGREGATIONS:
   - HAVING clause: SELECT status, COUNT(*) as cnt FROM claim GROUP BY status HAVING COUNT(*) > 100
   - COUNT DISTINCT: SELECT COUNT(DISTINCT user_id) as unique_users FROM claim
   - Multiple aggregates: SELECT status, COUNT(*) as total, AVG(amount) as avg_amount, MAX(amount) as max_amount, STDDEV(amount) as std_dev FROM claim GROUP BY status
   - FILTER clause: SELECT COUNT(*) FILTER (WHERE status = 'open') as open_count, COUNT(*) FILTER (WHERE status = 'closed') as closed_count FROM claim

6. UNION/INTERSECT/EXCEPT (Set operations):
   - UNION: SELECT id, description, 'claim' as type FROM claim UNION SELECT id, notes as description, 'assessment' as type FROM assessment
   - INTERSECT: SELECT user_id FROM claim WHERE status = 'open' INTERSECT SELECT user_id FROM claim WHERE created_at > CURRENT_DATE - INTERVAL '7 days'
   - EXCEPT: SELECT user_id FROM claim EXCEPT SELECT user_id FROM assessment

7. POSTGRESQL-SPECIFIC FEATURES:

   a) LATERAL Joins (for correlated subqueries):
      - SELECT c.*, recent.* FROM claim c, LATERAL (SELECT * FROM assessment a WHERE a.claim_id = c.id ORDER BY created_at DESC LIMIT 3) AS recent

   b) JSON Aggregation:
      - json_agg: SELECT status, json_agg(json_build_object('id', id, 'amount', amount)) as claims FROM claim GROUP BY status
      - jsonb_agg: SELECT user_id, jsonb_agg(DISTINCT status) as statuses FROM claim GROUP BY user_id

   c) Array Aggregation:
      - array_agg: SELECT user_id, array_agg(DISTINCT status) as all_statuses FROM claim GROUP BY user_id
      - string_agg: SELECT user_id, string_agg(DISTINCT status, ', ') as status_list FROM claim GROUP BY user_id

   d) Generate Series (for date ranges/sequences):
      - Date series: SELECT d.date, COUNT(c.id) as daily_count FROM generate_series(CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE, '1 day'::interval) AS d(date) LEFT JOIN claim c ON DATE(c.created_at) = d.date GROUP BY d.date ORDER BY d.date
      - Number series: SELECT generate_series(1, 100) as num

   e) DISTINCT ON (First row per group):
      - SELECT DISTINCT ON (user_id) user_id, status, created_at FROM claim ORDER BY user_id, created_at DESC

8. COMPLEX ANALYTICAL PATTERNS:
   - Top N per group: WITH ranked AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY amount DESC) as rn FROM claim) SELECT * FROM ranked WHERE rn <= 5
   - Period comparison: SELECT DATE(created_at) as date, COUNT(*) as today_count, LAG(COUNT(*)) OVER (ORDER BY DATE(created_at)) as yesterday_count, COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY DATE(created_at)) as change FROM claim GROUP BY DATE(created_at)
   - Cohort analysis: SELECT DATE_TRUNC('month', created_at) as cohort, status, COUNT(*) FROM claim GROUP BY cohort, status ORDER BY cohort, status
   - Moving averages: SELECT DATE(created_at) as date, AVG(amount) OVER (ORDER BY DATE(created_at) ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as moving_avg_7day FROM claim
   - Cumulative distributions: SELECT amount, PERCENT_RANK() OVER (ORDER BY amount) as percentile FROM claim

QUERY BEST PRACTICES:
- For multi-table queries: ALWAYS check schema first to find correct join keys (id, claim_id, user_id, etc.)
- Use JOINs instead of multiple queries when relating data across tables
- Use CTEs for readability when query has multiple steps
- Use window functions for rankings, running totals, period-over-period comparisons
- Use LATERAL for complex correlated subqueries
- Use json_agg/array_agg for grouping related data into structures
- Use generate_series for date/time series analysis with gaps filled
- Use DISTINCT ON for "first/last per group" queries (faster than window functions)
- Add LIMIT clause for exploratory queries to avoid huge result sets
- PostgreSQL is case-sensitive for quoted identifiers ("User" vs "user")

IMPORTANT:
- Use CURRENT_DATE for today's date (not CURDATE())
- Use INTERVAL '7 days' syntax (not MySQL's INTERVAL 7 DAY)
- Use DATE_TRUNC() for month/year grouping
- Column names may be case-sensitive (use quotes if needed: "User", "createdAt")
- PostgreSQL uses single quotes for strings and dates
- Check schema first for multi-table queries to find join keys
- PostgreSQL supports all advanced SQL features + unique features like LATERAL, json_agg, array_agg, generate_series, DISTINCT ON""",
            "parameters": {
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL SELECT query (PostgreSQL syntax only). Must start with SELECT. No DROP/DELETE/UPDATE/INSERT allowed."
                    }
                },
                "required": ["sql"]
            }
        }
    },
    # Google Drive MCP Tools
    {
        "type": "function",
        "function": {
            "name": "drive_list_files",
            "description": """List files and folders in Google Drive. CRITICAL: ALWAYS use this tool when user asks about Google Drive, files, documents, folders, or any question related to file storage or cloud storage. This tool connects to the user's Google Drive account and retrieves their files. Use this tool whenever user mentions Drive, Google Drive, files, documents, folders, or asks about their files or documents. NEVER say 'not connected' or 'I don't have access' - you MUST call this tool first to check the actual connection status. The tool will return real data if connected, or an error message if not connected - let the tool tell you, don't guess!

**CRITICAL DISPLAY REQUIREMENT:** When you present the file list to the user, you MUST ALWAYS include the file_id for EVERY file!

Required output format (MANDATORY):
1. **Filename** (ID: `1abc...xyz`)
   - Type: [file type]
   - Modified: [date]

Example:
"Here are your files:
1. **Meeting Notes** (ID: `1rOzZaoAPommHXQUTbElC54qE3T6XoGgAzYcdasMzB4k`)
   - Type: Google Docs
   - Modified: Nov 18, 2025"

The tool returns: (file_id: `1abc...xyz`)
You MUST display it as: (ID: `1abc...xyz`)

NEVER hide, omit, or truncate the file_id! The user needs to see it to read files.
When user asks to read a file, use the EXACT file_id from your previous response.""",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Optional: filter query (e.g., 'name contains \"report\"')"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "drive_search_files",
            "description": "Search files in Google Drive by name or content. Use when user wants to find specific documents.\n\nIMPORTANT: This tool returns file_id values in the response (shown in backticks like file_id: `1abc...xyz`). SAVE these file_id values - you MUST use the exact file_id when calling drive_read_file. NEVER make up or guess file_id values!",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (searches in file names)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "drive_read_file",
            "description": """Read file contents from Google Drive. ✅ FULLY SUPPORTS PDF, EXCEL, WORD, and all other file types!

🎯 **THIS TOOL CAN READ EVERYTHING - PDF, DOCX, XLSX, TXT, SHEETS, DOCS, ETC!**

**SUPPORTED FILE TYPES (WITH AUTOMATIC TEXT EXTRACTION):**

📄 **Microsoft Office Files** (✅ FULL TEXT EXTRACTION):
- ✅ **PDF files (.pdf)** → Automatic text extraction using PyPDF2
- ✅ **Word documents (.docx)** → Automatic text extraction using python-docx
- ✅ **Excel spreadsheets (.xlsx)** → Automatic text extraction using openpyxl
- ✅ PowerPoint (.pptx) → Binary content

📊 **Google Workspace Files** (auto-export to readable format):
- ✅ Google Docs → Plain text export
- ✅ Google Sheets → CSV format export
- ✅ Google Slides → Plain text export
- ✅ Google Forms → Plain text export
- ✅ Google Drawings → Plain text export

📝 **Text Files** (direct text content):
- ✅ TXT, CSV, JSON, HTML, XML → Direct text content
- ✅ Code files (.py, .js, .java, etc.) → Full source code

🖼️ **Other Files**:
- Images (PNG, JPG, GIF) → Binary only (no OCR capability)
- ZIP, TAR → Binary content

**Size Limits**:
- Maximum: 2MB per file
- Files >3MB → Error message returned
- Returns truncation flag if content exceeds 2MB

**IMPORTANT: This tool uses Python backend with PyPDF2, python-docx, and openpyxl libraries.**
**Same capability as ChatGPT 4.0 for reading PDF/Excel/Word files from Drive!**

Use this tool when user wants to:
- ✅ Read, view, or display file contents (INCLUDING PDF, EXCEL, WORD!)
- ✅ Analyze or summarize a document (PDF, DOCX, XLSX supported!)
- ✅ Extract information from a file
- ✅ Check what's inside a file
- ✅ "Read this PDF for me" → YES, you can do this!
- ✅ "What's in this Excel file?" → YES, you can do this!
- ✅ "Summarize this Word doc" → YES, you can do this!

📋 **How to Get file_id (REQUIRED PARAMETER):**

🚨 **MANDATORY WORKFLOW - ALWAYS SEARCH FIRST!**

⚠️ **CRITICAL: NEVER use file_id from conversation history - ALWAYS search first!**

**Why:** File IDs from previous messages may be stale, deleted, moved, or from different files → causes 404 errors.

**REQUIRED WORKFLOW (100% of the time):**

When user asks to read ANY file:
1. **ALWAYS call drive_search_files first** with the file name or keywords
2. Get file_id from fresh search results (first result is usually correct)
3. Call drive_read_file with that file_id
4. Done!

**Examples:**

**Example 1 - User provides file name:**
- User: "read Business Requirements.docx"
- Bot: ✅ Calls drive_search_files("Business Requirements.docx")
- Bot: Gets file_id from search → `1KeWe...Oq9Y`
- Bot: Calls drive_read_file(file_id="1KeWe...Oq9Y") → SUCCESS!

**Example 2 - User mentions file from list:**
- User previously listed files, file #7 was "ESMA_65-8-10392_OBOOK_BRD_v1.0.pdf"
- User: "summary this plz, file #7"
- Bot: ✅ Calls drive_search_files("ESMA_65-8-10392 OBOOK BRD v1.0") FIRST
- Bot: Gets FRESH file_id from search → `1Abc...xyz`
- Bot: Calls drive_read_file(file_id="1Abc...xyz") → SUCCESS!

**Example 3 - User references old conversation:**
- User: "read that Joffrey review document we talked about yesterday"
- Bot: ✅ Calls drive_search_files("Joffrey review") FIRST
- Bot: Gets FRESH file_id from search → `1Dq5...zhWg`
- Bot: Calls drive_read_file(file_id="1Dq5...zhWg") → SUCCESS!

**file_id Format:**
- Valid format: 30-60 alphanumeric characters (letters, numbers, hyphens, underscores)
- Example REAL file_id: `1KeWeBSxhoCEAS6S75KYobFHCPdsweOq9YKK2Bp9zhWg`
- Must be obtained from drive_search_files (NEVER from history!)

**IF YOU GET 404 ERROR:**
- This means you violated the rule and used file_id from history
- ALWAYS call drive_search_files first with file name
- If search returns no results → File was deleted/moved → Tell user file not found

Real Google Drive file_ids are 30-60 characters long and look random (e.g., `1KeWeBSxhoCEAS6S75KYobFHCPdsweOq9YKK2Bp9zhWg`).""",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "Google Drive file ID (obtained from drive_list_files or drive_search_files)"
                    }
                },
                "required": ["file_id"]
            }
        }
    },
    # Advanced Jira Analysis Tools
    {
        "type": "function",
        "function": {
            "name": "jira_get_project_details",
            "description": "Get detailed information about a Jira project including team members, roles, and composition. Use when user asks 'who works on project X', 'show me team members', or 'project team'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "Project key (e.g., TQB, AAP, CLEARQB)"
                    }
                },
                "required": ["project_key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "jira_get_project_analytics",
            "description": "Get comprehensive analytics for a Jira project - breakdown by status, priority, assignee, and type. Use for 'analyze project X', 'project statistics', 'how many issues', 'project health'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "Project key"
                    }
                },
                "required": ["project_key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "jira_get_issue_comments",
            "description": "Get all comments and discussion for a Jira issue. Use when user asks about discussion, feedback, or comments on a specific ticket.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "Issue key (e.g., AAP-123, TQB-456)"
                    }
                },
                "required": ["issue_key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "jira_get_all_projects_summary",
            "description": "Get bug count summary across ALL Jira projects in one efficient query. Use for 'which project has most bugs', 'bug summary', 'project comparison'. This is much faster than checking each project individually.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "jira_list_filters",
            "description": "List all Jira filters available to the user (my filters, favourites, shared filters). Use when user asks 'what filters do I have', 'show jira filters', 'list available filters'.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "jira_execute_filter",
            "description": "Execute a specific Jira filter by ID or name and return matching issues. Use when user wants to run a saved filter like 'run Code Review filter', 'show issues from AAP filter'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filter_id": {
                        "type": "string",
                        "description": "The filter ID (e.g., '10721') or search by name if user provides filter name"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Maximum number of issues to return (default 50)"
                    }
                },
                "required": ["filter_id"]
            }
        }
    },
    # Prompt Validation Tools
    {
        "type": "function",
        "function": {
            "name": "search_prompts_by_intent",
            "description": "Search for BUSINESS DOCUMENT prompt templates (HR, contracts, proposals, reports). Use ONLY when user asks to create formal business documents from template library (e.g., 'write an offer letter', 'create employment contract', 'generate performance review'). DO NOT use for simple content like jokes, stories, code, emails, or casual writing - handle those directly without templates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_query": {
                        "type": "string",
                        "description": "The user's request describing the BUSINESS DOCUMENT they want to generate (e.g., 'offer letter', 'employment contract', 'performance review', 'business proposal')"
                    }
                },
                "required": ["user_query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "validate_prompt_variables",
            "description": "Get required variables for a business document template. Use this AFTER finding a template with search_prompts_by_intent and BEFORE generating the document. Shows ALL required variables that MUST be collected from user. Only applicable for business documents using templates - not for simple content generation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt_code": {
                        "type": "string",
                        "description": "The code of the prompt template (e.g., 'hr_offer_letter', 'hr_contract')"
                    }
                },
                "required": ["prompt_code"]
            }
        }
    },
    # GitHub Phase 1 - Create & List Tools
    {
        "type": "function",
        "function": {
            "name": "github_create_issue",
            "description": "Create a new GitHub issue in a repository. Use when user wants to create a bug report, feature request, or task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository full name (format: owner/repo)"},
                    "title": {"type": "string", "description": "Issue title"},
                    "body": {"type": "string", "description": "Issue description/body"},
                    "labels": {"type": "array", "items": {"type": "string"}, "description": "Optional labels"},
                    "assignees": {"type": "array", "items": {"type": "string"}, "description": "Optional assignee usernames"}
                },
                "required": ["repo", "title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "github_list_issues",
            "description": "List issues in a GitHub repository with optional state filter (open/closed/all).",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository full name (format: owner/repo)"},
                    "state": {"type": "string", "description": "State filter: open, closed, all (default: open)"}
                },
                "required": ["repo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "github_get_issue",
            "description": "Get detailed information about a specific GitHub issue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository full name (format: owner/repo)"},
                    "issue_number": {"type": "integer", "description": "Issue number"}
                },
                "required": ["repo", "issue_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "github_list_prs",
            "description": "List pull requests in a GitHub repository with optional state filter.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository full name (format: owner/repo)"},
                    "state": {"type": "string", "description": "State filter: open, closed, all (default: open)"}
                },
                "required": ["repo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "github_get_pr",
            "description": "Get detailed information about a specific pull request.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository full name (format: owner/repo)"},
                    "pr_number": {"type": "integer", "description": "Pull request number"}
                },
                "required": ["repo", "pr_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "github_create_pr",
            "description": "Create a new pull request in a GitHub repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository full name (format: owner/repo)"},
                    "title": {"type": "string", "description": "PR title"},
                    "head": {"type": "string", "description": "Source branch name"},
                    "base": {"type": "string", "description": "Target branch name (e.g., main)"},
                    "body": {"type": "string", "description": "PR description"}
                },
                "required": ["repo", "title", "head", "base"]
            }
        }
    },
    # GitHub Phase 2 - Advanced Operations
    {
        "type": "function",
        "function": {
            "name": "github_create_file",
            "description": "Create a new file in a GitHub repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository full name (format: owner/repo)"},
                    "path": {"type": "string", "description": "File path in repository (e.g., 'src/main.py')"},
                    "content": {"type": "string", "description": "File content"},
                    "message": {"type": "string", "description": "Commit message"},
                    "branch": {"type": "string", "description": "Branch name (default: main)"}
                },
                "required": ["repo", "path", "content", "message"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "github_update_file",
            "description": "Update an existing file in a GitHub repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository full name (format: owner/repo)"},
                    "path": {"type": "string", "description": "File path in repository"},
                    "content": {"type": "string", "description": "New file content"},
                    "message": {"type": "string", "description": "Commit message"},
                    "sha": {"type": "string", "description": "Current file SHA (get from github_read_file)"},
                    "branch": {"type": "string", "description": "Branch name (default: main)"}
                },
                "required": ["repo", "path", "content", "message", "sha"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "github_merge_pr",
            "description": "Merge a pull request in a GitHub repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository full name (format: owner/repo)"},
                    "pr_number": {"type": "integer", "description": "Pull request number"},
                    "commit_title": {"type": "string", "description": "Optional merge commit title"},
                    "merge_method": {"type": "string", "description": "Merge method: merge, squash, rebase (default: merge)"}
                },
                "required": ["repo", "pr_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "github_create_branch",
            "description": "Create a new branch in a GitHub repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository full name (format: owner/repo)"},
                    "branch_name": {"type": "string", "description": "New branch name"},
                    "from_branch": {"type": "string", "description": "Source branch (default: main)"}
                },
                "required": ["repo", "branch_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "github_list_commits",
            "description": "List recent commits in a GitHub repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository full name (format: owner/repo)"},
                    "branch": {"type": "string", "description": "Branch name (default: main)"},
                    "max_results": {"type": "integer", "description": "Max commits to return (default: 30)"}
                },
                "required": ["repo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "github_get_repo",
            "description": "Get detailed information about a GitHub repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository full name (format: owner/repo)"}
                },
                "required": ["repo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "github_list_collaborators",
            "description": "List collaborators of a GitHub repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository full name (format: owner/repo)"}
                },
                "required": ["repo"]
            }
        }
    },
    # Jira Phase 1 - Create & Update Tools
    {
        "type": "function",
        "function": {
            "name": "jira_create_issue",
            "description": "Create a new Jira issue in a project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_key": {"type": "string", "description": "Project key (e.g., 'AAP', 'PROJ')"},
                    "summary": {"type": "string", "description": "Issue summary/title"},
                    "description": {"type": "string", "description": "Issue description"},
                    "issue_type": {"type": "string", "description": "Issue type: Task, Bug, Story, Epic (default: Task)"},
                    "priority": {"type": "string", "description": "Priority: Highest, High, Medium, Low, Lowest"},
                    "assignee_id": {"type": "string", "description": "Assignee account ID"}
                },
                "required": ["project_key", "summary"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "jira_update_issue",
            "description": "Update an existing Jira issue's fields.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key (e.g., 'AAP-123')"},
                    "summary": {"type": "string", "description": "New summary"},
                    "description": {"type": "string", "description": "New description"},
                    "status": {"type": "string", "description": "New status (e.g., 'In Progress', 'Done')"},
                    "priority": {"type": "string", "description": "New priority"},
                    "assignee_id": {"type": "string", "description": "New assignee account ID"}
                },
                "required": ["issue_key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "jira_add_comment",
            "description": "Add a comment to a Jira issue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key (e.g., 'AAP-123')"},
                    "comment": {"type": "string", "description": "Comment text"}
                },
                "required": ["issue_key", "comment"]
            }
        }
    },
    # Jira Phase 2 - Advanced Operations
    {
        "type": "function",
        "function": {
            "name": "jira_transition_issue",
            "description": "Transition a Jira issue to a new status workflow.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key (e.g., 'AAP-123')"},
                    "transition_name": {"type": "string", "description": "Transition name (e.g., 'In Progress', 'Done', 'To Do')"}
                },
                "required": ["issue_key", "transition_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "jira_list_boards",
            "description": "List Jira boards, optionally filtered by project.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_key": {"type": "string", "description": "Optional project key filter"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "jira_list_sprints",
            "description": "List sprints for a specific Jira board.",
            "parameters": {
                "type": "object",
                "properties": {
                    "board_id": {"type": "integer", "description": "Board ID"}
                },
                "required": ["board_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "jira_add_attachment",
            "description": "Add an attachment file to a Jira issue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key (e.g., 'AAP-123')"},
                    "file_content": {"type": "string", "description": "File content as bytes"},
                    "filename": {"type": "string", "description": "Filename"}
                },
                "required": ["issue_key", "file_content", "filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "jira_log_work",
            "description": "Log work time on a Jira issue (time tracking).",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "Issue key (e.g., 'AAP-123')"},
                    "time_spent": {"type": "string", "description": "Time spent (e.g., '2h 30m', '1d', '4h')"},
                    "comment": {"type": "string", "description": "Optional work log comment"}
                },
                "required": ["issue_key", "time_spent"]
            }
        }
    },
    # Jira - User-Specific Project Listing
    {
        "type": "function",
        "function": {
            "name": "jira_list_my_active_projects",
            "description": "List only Jira projects where you have actual issues assigned or created. RECOMMENDED: Use this instead of jira_list_projects to avoid seeing irrelevant workspace projects. Fast JQL-based approach that shows only your active projects.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    # Jira - Generic API Access
    {
        "type": "function",
        "function": {
            "name": "jira_api_call",
            "description": "⭐ RECOMMENDED: Universal Jira REST API v3 caller - call ANY Jira endpoint directly. USE THIS for all Jira operations including:\n• JQL Search: GET /search/jql with params={'jql': 'project=LEA AND status=Open', 'maxResults': 50} - Returns full issue details (summary, status, assignee, etc.)\n• Count ONLY: Use maxResults=1 and check 'total' field. For listing tickets, use maxResults=50-100 to get full details\n• Multiple tickets: Use JQL 'key IN (TICKET-1, TICKET-2, ...)' syntax to query multiple specific tickets at once\n• Reporter/Assignee query: Use 'reporter = \"Display Name\"' or 'assignee = \"Display Name\"' with exact display name in quotes\n• Filters: Combine JQL operators like 'project = LEA AND assignee = currentUser() ORDER BY created DESC'\n• Get single issue: GET /issue/{key}\n• Work logs: GET /issue/{key}/worklog\n• Custom fields: GET /field\n• Statuses: GET /status\n• Issue types: GET /issuetype\n• Priorities: GET /priority\n• Project details: GET /project/{key}\n• Transitions: POST /issue/{key}/transitions\nNOTE: maxResults must be 1-5000. Use higher values (50-100) when user wants to SEE ticket details, use 1 only for COUNT.\nDocs: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/",
            "parameters": {
                "type": "object",
                "properties": {
                    "endpoint": {
                        "type": "string",
                        "description": "API endpoint path without '/rest/api/3' prefix. Examples: '/search/jql' (for JQL queries), '/issue/LEA-123', '/project/LEA/statuses', '/field', '/issuetype', '/priority'. NOTE: Use '/search/jql' not '/search' (deprecated)"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                        "description": "HTTP method (default: GET)"
                    },
                    "params": {
                        "type": "object",
                        "description": "Query parameters object. For JQL search: {'jql': 'your query', 'maxResults': 50, 'startAt': 0}"
                    },
                    "body": {
                        "type": "object",
                        "description": "Request body for POST/PUT/PATCH requests"
                    }
                },
                "required": ["endpoint"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "jira_list_projects_with_role",
            "description": "List Jira projects where you have an assigned role (team member). More accurate than jira_list_projects but slower. Use when you need to see all projects you're a member of, even if you don't have issues yet.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    # Google Drive Phase 1 - Create & Update Tools
    {
        "type": "function",
        "function": {
            "name": "drive_create_file",
            "description": "Create a new file in Google Drive.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "File name"},
                    "content": {"type": "string", "description": "File content"},
                    "mime_type": {"type": "string", "description": "MIME type (default: text/plain)"},
                    "folder_id": {"type": "string", "description": "Optional parent folder ID"}
                },
                "required": ["name", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "drive_update_file",
            "description": "Update an existing Google Drive file's content or name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID"},
                    "content": {"type": "string", "description": "New file content"},
                    "name": {"type": "string", "description": "New file name"},
                    "mime_type": {"type": "string", "description": "MIME type (default: text/plain)"}
                },
                "required": ["file_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "drive_create_folder",
            "description": "Create a new folder in Google Drive.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Folder name"},
                    "parent_folder_id": {"type": "string", "description": "Optional parent folder ID"}
                },
                "required": ["name"]
            }
        }
    },
    # Google Drive Phase 2 - Advanced Operations
    {
        "type": "function",
        "function": {
            "name": "drive_share_file",
            "description": "Share a Google Drive file with another user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File ID"},
                    "email": {"type": "string", "description": "User email to share with"},
                    "role": {"type": "string", "description": "Permission role: reader, writer, commenter (default: reader)"},
                    "send_notification": {"type": "boolean", "description": "Send email notification (default: true)"}
                },
                "required": ["file_id", "email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "drive_delete_file",
            "description": "Delete a file or folder from Google Drive.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "File or folder ID to delete"}
                },
                "required": ["file_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "drive_export_file",
            "description": "Export Google Docs/Sheets/Slides to PDF, DOCX, XLSX, etc. and READ the content. Use this to scan/read PDF, DOC, or Sheet files. Returns full file content for analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "Google Drive file ID"},
                    "mime_type": {"type": "string", "description": "Export MIME type: application/pdf (for PDFs), application/vnd.openxmlformats-officedocument.wordprocessingml.document (for DOCX), application/vnd.openxmlformats-officedocument.spreadsheetml.sheet (for XLSX), text/plain (for TXT). Default: application/pdf"}
                },
                "required": ["file_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "drive_api_call",
            "description": "⭐ RECOMMENDED: Universal Google Drive REST API v3 caller - call ANY Drive endpoint directly. USE THIS for all Drive operations including:\n• Get detailed file metadata: GET /files/{fileId}?fields=*\n• List files with filters: GET /files?q=name contains 'report' AND mimeType='application/pdf'\n• Export files: GET /files/{fileId}/export?mimeType=application/pdf\n• Get permissions: GET /files/{fileId}/permissions\n• Copy file: POST /files/{fileId}/copy\n• Move file: PATCH /files/{fileId} with body {\"parents\": [\"newFolderId\"]}\nDocs: https://developers.google.com/drive/api/v3/reference",
            "parameters": {
                "type": "object",
                "properties": {
                    "endpoint": {
                        "type": "string",
                        "description": "API endpoint path without 'https://www.googleapis.com/drive/v3' prefix. Examples: '/files/{fileId}', '/files/{fileId}/export', '/files/{fileId}/permissions', '/files?q=...'"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                        "description": "HTTP method (default: GET)"
                    },
                    "params": {
                        "type": "object",
                        "description": "Query parameters object. Examples: {'fields': '*'}, {'q': \"name contains 'report'\"}, {'mimeType': 'application/pdf'}"
                    },
                    "body": {
                        "type": "object",
                        "description": "Request body for POST/PUT/PATCH requests"
                    }
                },
                "required": ["endpoint"]
            }
        }
    }
]
