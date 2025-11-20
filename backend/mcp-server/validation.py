"""
Prompt validation logic for template variable extraction and validation
"""

import re
from typing import List, Dict, Tuple

def is_placeholder(val: str) -> bool:
    """
    Smart detection for placeholder/invalid values.
    
    Detects common placeholder patterns like [Name], <value>, {variable},
    TBD, TODO, N/A, etc.
    
    Args:
        val: Value to check
        
    Returns:
        bool: True if value appears to be a placeholder
    """
    if not val or not str(val).strip():
        return True
    
    s = str(val).strip().lower()
    
    if len(s) < 2:
        return True
    
    patterns = [
        r'^\[.*\]$',  # [Name], [Value]
        r'^<.*>$',    # <name>, <value>
        r'^\{.*\}$',  # {variable}
        r'^(tbd|todo|n/?a|none|null|pending|unknown)$',  # Common placeholders
        r'^(your|my|the|this|that)\s+\w+$',  # "your name", "the value"
        r'^\w+\s+(name|title|date|value|amount)$',  # "company name", "start date"
        r'^(please|enter|provide|specify)\s+',  # "please enter", "provide value"
        r'^(example|sample|test|demo|dummy)\s*',  # "example", "sample value"
    ]
    
    for pattern in patterns:
        if re.match(pattern, s):
            return True
    
    return False

def humanize_var_name(var_name: str) -> str:
    """
    Convert variable name to human-readable format.
    
    Example: "company_name" -> "Company Name"
    
    Args:
        var_name: Variable name with underscores
        
    Returns:
        str: Human-readable name
    """
    words = var_name.split("_")
    return " ".join(word.capitalize() for word in words)

def extract_variables(content: str) -> List[Dict]:
    """
    Extract variables from template content.
    
    Supports patterns:
    - {{variable}} - required variable
    - {{variable?}} - optional variable
    - {{variable=default}} - variable with default value
    
    Args:
        content: Template content with variable placeholders
        
    Returns:
        List[Dict]: List of variable definitions with name, description, required, default
    """
    if not content:
        return []
    
    pattern = r"\{\{(\w+)(\?)?(=([^}]*))?\}\}"
    seen = set()
    out = []
    
    for m in re.finditer(pattern, content):
        name = m.group(1)
        if name in seen:
            continue
        seen.add(name)
        
        is_optional = (m.group(2) == "?")
        default_val = m.group(4) if m.group(3) else None
        
        item = {
            "name": name,
            "description": humanize_var_name(name),
            "required": not is_optional and default_val is None
        }
        if default_val:
            item["default"] = default_val
        
        out.append(item)
    
    return out

def validate_all_fields(collected: Dict, required: List[str]) -> Tuple[bool, List[str]]:
    """
    Strict validation - all required fields must be valid (not placeholders).
    
    Args:
        collected: Dictionary of collected field values
        required: List of required field names
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, missing_fields)
    """
    missing = []
    
    for field in required:
        if field not in collected:
            missing.append(field)
        elif is_placeholder(collected[field]):
            missing.append(field)
    
    return (len(missing) == 0, missing)

def fill_template(content: str, values: Dict) -> str:
    """
    Fill template with provided values.
    
    Replaces all variable placeholders with actual values.
    Cleans up any remaining placeholders.
    
    Args:
        content: Template content
        values: Dictionary of variable names to values
        
    Returns:
        str: Filled template content
    """
    result = content
    for var, val in values.items():
        result = result.replace(f"{{{{{var}}}}}", str(val))
        result = result.replace(f"{{{{{var}?}}}}", str(val))
        result = re.sub(r"\{\{" + re.escape(var) + r"=[^}]*\}\}", str(val), result)
    
    # Clean remaining placeholders
    result = re.sub(r"\{\{\w+\??\}\}", "", result)
    result = re.sub(r"\{\{\w+=[^}]*\}\}", "", result)
    return result

