# validators.py
# Validate args against arguments_json.
from typing import Any, Dict, List
from fastapi import HTTPException, status

def ensure_valid_payload(arguments_json: List[Dict[str,Any]], args: Dict[str,Any]) -> None:
    missing = [a["name"] for a in (arguments_json or []) if a.get("required") and a["name"] not in args]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    for a in (arguments_json or []):
        if "enum" in a and a["name"] in args and args[a["name"]] not in a["enum"]:
            raise ValueError(f"Field '{a['name']}' must be one of {a['enum']}")
