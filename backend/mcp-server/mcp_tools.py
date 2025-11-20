"""
MCP Tools - DEPRECATED
This module is no longer used. Integration tools (GitHub/Jira/Drive) are now handled
via native MCP servers in the Agent API, not through this local MCP server.

Local MCP Server now only handles:
- Prompts management (via routers/prompts.py)
- Database access (via routers/insurance.py, routers/claimhub.py)
- OAuth token storage (via routers/oauth.py)
"""

# This file is kept for backward compatibility but contains no tools
__all__ = []
