#!/usr/bin/env python3
"""
Validate generated prompts according to MCP Server rules
"""

import json
import re
from typing import List, Tuple, Dict

def validate_variable_syntax(content: str) -> Tuple[bool, List[str]]:
    """
    Validate {{variable}} syntax
    Supports:
    - {{variable}} - required
    - {{variable?}} - optional
    - {{variable=default}} - with default
    """
    errors = []

    # Find all variables
    pattern = r'\{\{([^}]+)\}\}'
    variables = re.findall(pattern, content)

    for var in variables:
        # Check valid format
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*(\?|=[^}]*)?$', var):
            errors.append(f"Invalid variable syntax: {{{{{var}}}}}")

    return len(errors) == 0, errors

def validate_required_fields(prompt: Dict) -> Tuple[bool, List[str]]:
    """Validate required fields exist"""
    errors = []

    required_fields = ['code', 'name', 'categories', 'content', 'variables']

    for field in required_fields:
        if field not in prompt or not prompt[field]:
            errors.append(f"Missing required field: {field}")

    # Check code format (lowercase, underscores only)
    if 'code' in prompt:
        if not re.match(r'^[a-z0-9_]+$', prompt['code']):
            errors.append(f"Invalid code format: {prompt['code']} (use lowercase and underscores only)")

    # Check categories is list
    if 'categories' in prompt and not isinstance(prompt['categories'], list):
        errors.append("Categories must be a list")

    # Check variables is list
    if 'variables' in prompt and not isinstance(prompt['variables'], list):
        errors.append("Variables must be a list")

    return len(errors) == 0, errors

def extract_variables_from_content(content: str) -> List[str]:
    """Extract all variables from content {{variable}}"""
    pattern = r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)(?:\?|=[^}]*)?\}\}'
    return list(set(re.findall(pattern, content)))

def validate_variables_match(prompt: Dict) -> Tuple[bool, List[str]]:
    """Validate that variables in content match variables list"""
    errors = []

    content_vars = set(extract_variables_from_content(prompt.get('content', '')))
    declared_vars = set(prompt.get('variables', []))

    # Check for undeclared variables in content
    undeclared = content_vars - declared_vars
    if undeclared:
        errors.append(f"Undeclared variables in content: {', '.join(undeclared)}")

    # Check for unused declared variables
    unused = declared_vars - content_vars
    if unused:
        errors.append(f"Declared but unused variables: {', '.join(unused)}")

    return len(errors) == 0, errors

def validate_placeholder_values(prompt: Dict) -> Tuple[bool, List[str]]:
    """
    Check for placeholder values that MCP Server would reject
    According to backend/mcp-server/app.py validation logic
    """
    errors = []

    invalid_patterns = [
        r'\[[\w\s]+\]',  # [name], [value]
        r'<[\w\s]+>',    # <value>, <text>
        r'\bTBD\b',      # TBD
        r'\bN/?A\b',     # N/A, NA
        r'\bTODO\b',     # TODO
        r'\bXXX\b',      # XXX
    ]

    content = prompt.get('content', '')

    for pattern in invalid_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            errors.append(f"Content contains placeholder pattern: {pattern}")

    return len(errors) == 0, errors

def validate_n8n_config(prompt: Dict) -> Tuple[bool, List[str]]:
    """Validate N8N-specific configuration"""
    errors = []

    if 'n8n_config' not in prompt:
        return True, []  # Not an N8N prompt, skip

    config = prompt['n8n_config']

    # Required N8N fields
    if 'workflow_id' not in config:
        errors.append("N8N prompt missing workflow_id")

    if 'trigger_type' not in config:
        errors.append("N8N prompt missing trigger_type")

    # Validate ECS config if present
    if 'ecs_task_config' in config:
        ecs = config['ecs_task_config']

        # Check valid CPU/memory combinations for Fargate
        valid_combinations = {
            256: [512, 1024, 2048],
            512: [1024, 2048, 3072, 4096],
            1024: [2048, 3072, 4096, 5120, 6144, 7168, 8192],
            2048: list(range(4096, 16385, 1024)),
            4096: list(range(8192, 30721, 1024))
        }

        cpu = ecs.get('cpu_default', 1024)
        memory = ecs.get('memory_default', 2048)

        if cpu not in valid_combinations:
            errors.append(f"Invalid CPU value: {cpu}")
        elif memory not in valid_combinations[cpu]:
            errors.append(f"Invalid CPU/Memory combination: {cpu}/{memory}")

    return len(errors) == 0, errors

def validate_prompt(prompt: Dict) -> Tuple[bool, List[str]]:
    """Run all validations on a prompt"""
    all_errors = []

    # 1. Required fields
    valid, errors = validate_required_fields(prompt)
    all_errors.extend(errors)

    # 2. Variable syntax
    valid, errors = validate_variable_syntax(prompt.get('content', ''))
    all_errors.extend(errors)

    # 3. Variables match
    valid, errors = validate_variables_match(prompt)
    all_errors.extend(errors)

    # 4. Placeholder values
    valid, errors = validate_placeholder_values(prompt)
    all_errors.extend(errors)

    # 5. N8N config
    valid, errors = validate_n8n_config(prompt)
    all_errors.extend(errors)

    return len(all_errors) == 0, all_errors

def main():
    """Validate all generated prompts"""
    print("\n[START] Validating Generated Prompts...")
    print("="*60)

    # Load generated prompts
    with open('generated_prompts.json', 'r', encoding='utf-8') as f:
        prompts = json.load(f)

    print(f"[LOADED] {len(prompts)} prompts from generated_prompts.json")

    total = len(prompts)
    valid_count = 0
    invalid_count = 0
    errors_by_prompt = {}

    for prompt in prompts:
        is_valid, errors = validate_prompt(prompt)

        if is_valid:
            valid_count += 1
            print(f"[OK] {prompt['code']}")
        else:
            invalid_count += 1
            errors_by_prompt[prompt['code']] = errors
            print(f"[FAIL] {prompt['code']}")
            for error in errors:
                print(f"  - {error}")

    print(f"\n{'='*60}")
    print(f"[SUMMARY]")
    print(f"  Total: {total}")
    print(f"  Valid: {valid_count}")
    print(f"  Invalid: {invalid_count}")

    if invalid_count > 0:
        print(f"\n[ERRORS] Detailed errors:")
        for code, errors in errors_by_prompt.items():
            print(f"\n  {code}:")
            for error in errors:
                print(f"    - {error}")

    print("="*60)

    # Save validation report
    report = {
        'total': total,
        'valid': valid_count,
        'invalid': invalid_count,
        'errors': errors_by_prompt
    }

    with open('validation_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\n[SAVED] Validation report: validation_report.json")

    return invalid_count == 0

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
