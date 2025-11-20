"""
Prompts service
Handles prompt template CRUD operations and validation
"""

import json
from typing import List, Dict, Optional
from fastapi import HTTPException
from database import get_db
from validation import (
    is_placeholder,
    humanize_var_name,
    extract_variables,
    validate_all_fields,
    fill_template
)


def get_prompts(user_email: Optional[str] = None) -> Dict:
    """List all prompts (filtered by user roles if user_email provided)"""
    try:
        conn = get_db()
        cur = conn.cursor()

        # Get user roles if email provided
        user_roles = None
        is_admin = False
        if user_email:
            cur.execute("SELECT roles, is_admin FROM users WHERE email = %s", (user_email,))
            user_data = cur.fetchone()
            if user_data:
                try:
                    user_roles = json.loads(user_data['roles']) if isinstance(user_data['roles'], str) else user_data['roles']
                    is_admin = user_data['is_admin']
                except:
                    user_roles = ["ALL"]

        # Get all prompts with backwards-compatible ordering
        # Try to order by created_at if column exists, otherwise no ordering
        try:
            cur.execute("SELECT * FROM prompts ORDER BY created_at DESC")
            prompts = cur.fetchall()
        except Exception as e:
            # Fallback: created_at column doesn't exist yet (pre-migration schema)
            # This handles UndefinedColumn error without explicit import
            if 'created_at' in str(e) or 'column' in str(e).lower():
                cur.execute("SELECT * FROM prompts")
                prompts = cur.fetchall()
            else:
                raise  # Re-raise if it's a different error
        conn.close()

        # Parse JSON fields
        for p in prompts:
            if p.get('categories'):
                try:
                    p['categories'] = json.loads(p['categories']) if isinstance(p['categories'], str) else p['categories']
                except:
                    p['categories'] = []
            if p.get('variables'):
                try:
                    p['variables'] = json.loads(p['variables']) if isinstance(p['variables'], str) else p['variables']
                except:
                    p['variables'] = {}

        # Filter prompts by user roles
        if user_roles and not is_admin:
            filtered_prompts = []
            for p in prompts:
                # Admin or ALL role sees everything
                if 'ADMIN' in user_roles or 'ALL' in user_roles:
                    filtered_prompts.append(p)
                # Check if any category matches user roles
                elif any(cat in user_roles for cat in p.get('categories', [])):
                    filtered_prompts.append(p)
            prompts = filtered_prompts

        return {"prompts": prompts, "count": len(prompts)}
    except Exception as e:
        print(f"ERROR: Error getting prompts: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def get_prompt(code: str) -> Dict:
    """Get single prompt by code"""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM prompts WHERE code = %s", (code,))
        prompt = cur.fetchone()
        conn.close()
        
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        # Parse JSON fields
        if prompt.get('categories'):
            try:
                prompt['categories'] = json.loads(prompt['categories']) if isinstance(prompt['categories'], str) else prompt['categories']
            except:
                prompt['categories'] = []
        
        return prompt
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Error getting prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def create_prompt(prompt_data: Dict) -> Dict:
    """Create new prompt"""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO prompts (code, name, categories, content, output_folder)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            prompt_data['code'],
            prompt_data['name'],
            json.dumps(prompt_data['categories']),
            prompt_data['content'],
            prompt_data.get('output_folder', '')
        ))
        conn.commit()
        conn.close()
        print(f"OK: Prompt created: {prompt_data['code']}")
        return {"success": True, "message": "Prompt created", "code": prompt_data['code']}
    except Exception as e:
        print(f"ERROR: Error creating prompt: {e}")
        raise HTTPException(status_code=400, detail=str(e))


def update_prompt(code: str, prompt_data: Dict) -> Dict:
    """Update existing prompt"""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE prompts
            SET name=%s, categories=%s, content=%s, output_folder=%s
            WHERE code=%s
        """, (
            prompt_data['name'],
            json.dumps(prompt_data['categories']),
            prompt_data['content'],
            prompt_data.get('output_folder', ''),
            code
        ))
        
        if cur.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        conn.commit()
        conn.close()
        print(f"OK: Prompt updated: {code}")
        return {"success": True, "message": "Prompt updated"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Error updating prompt: {e}")
        raise HTTPException(status_code=400, detail=str(e))


def delete_prompt(code: str) -> Dict:
    """Delete prompt"""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM prompts WHERE code=%s", (code,))

        if cur.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Prompt not found")

        conn.commit()
        conn.close()
        print(f"OK: Prompt deleted: {code}")
        return {"success": True, "message": "Prompt deleted"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Error deleting prompt: {e}")
        raise HTTPException(status_code=400, detail=str(e))


def search_prompts_by_intent(query: str) -> Dict:
    """Search prompts by user intent/query"""
    try:
        prompts_data = get_prompts()
        prompts = prompts_data.get('prompts', [])
        
        query_lower = query.lower()
        matches = []
        
        for prompt in prompts:
            name = prompt.get('name', '').lower()
            code = prompt.get('code', '').lower()
            categories = [c.lower() for c in prompt.get('categories', [])]
            
            # Check if query matches name, code, or categories
            if (query_lower in name or 
                query_lower in code or 
                any(query_lower in cat for cat in categories)):
                
                # Extract variables for this prompt
                content = prompt.get('content', '')
                variables = extract_variables(content)
                required_vars = [v['name'] for v in variables if v.get('required', False)]
                
                matches.append({
                    'code': prompt.get('code'),
                    'name': prompt.get('name'),
                    'categories': prompt.get('categories', []),
                    'required_variables': required_vars
                })
        
        return {
            'success': True,
            'matches': matches,
            'query': query
        }
    except Exception as e:
        print(f"ERROR: Error searching prompts: {e}")
        return {
            'success': False,
            'error': str(e),
            'matches': []
        }


def validate_prompt_variables(prompt_code: str) -> Dict:
    """Validate prompt variables and return user-friendly message"""
    try:
        prompt = get_prompt(prompt_code)
        content = prompt.get('content', '')
        
        # Extract variables
        variables = extract_variables(content)
        required_vars = [v for v in variables if v.get('required', False)]
        optional_vars = [v for v in variables if not v.get('required', False)]
        
        if not required_vars:
            return {
                'success': True,
                'prompt_name': prompt.get('name', 'Unknown'),
                'message': 'This template has no required variables. You can generate the document immediately.',
                'required_variables': [],
                'optional_variables': [v['name'] for v in optional_vars],
                'variables': variables
            }
        
        # Build user-friendly message
        var_list = ', '.join([v['name'] for v in required_vars])
        message = f"To generate {prompt.get('name', 'this document')}, I need the following information: {var_list}. Please provide all these values."
        
        return {
            'success': True,
            'prompt_name': prompt.get('name', 'Unknown'),
            'message': message,
            'required_variables': [v['name'] for v in required_vars],
            'optional_variables': [v['name'] for v in optional_vars],
            'variables': variables
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Error validating prompt: {e}")
        return {
            'success': False,
            'error': str(e)
        }

