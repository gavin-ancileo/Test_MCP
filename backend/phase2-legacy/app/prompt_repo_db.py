# prompt_repo_db.py
# Build MCP /tools response from DB.
from typing import Any, Dict
from .db import list_all_tools

def mcp_tools_payload() -> Dict[str,Any]:
    tools = []
    for row in list_all_tools():
        args = []
        for a in (row["arguments_json"] or []):
            args.append({
                "name": a["name"],
                "description": a.get("description",""),
                "required": bool(a.get("required")),
                "schema": {"type": a.get("type","string"), **({"enum":a["enum"]} if a.get("enum") else {})}
            })
        tools.append({
            "name": row["code"],
            "description": row["name"],
            "arguments": args
        })
    return {"tools": tools}

