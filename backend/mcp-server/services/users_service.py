"""
Users service
Handles user management and authentication
"""

import json
from typing import Dict, Optional, List
from fastapi import HTTPException
from database import get_db


def user_login(email: str, name: Optional[str] = None) -> Dict:
    """
    Get or create user on SSO login
    IMPORTANT: Admin status (is_admin) comes from DATABASE, NOT from Cognito groups
    - New users are created with is_admin = FALSE by default
    - Admin status must be set manually via admin panel or /admin/set-admin endpoint
    - Cognito groups are only for reference, not used to determine admin status
    """
    try:
        conn = get_db()
        cur = conn.cursor()

        # Check if user exists
        cur.execute("SELECT email, name, roles, is_admin FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if user:
            # Parse roles
            try:
                roles = json.loads(user['roles']) if isinstance(user['roles'], str) else user['roles']
            except:
                roles = ["ALL"]
            
            # Admin status comes from database - NOT from Cognito groups
            is_admin = user['is_admin']
            
            conn.close()
            print(f"OK: User logged in: {email}, is_admin: {is_admin}")
            return {
                "email": user['email'],
                "name": user['name'],
                "roles": roles,
                "is_admin": is_admin
            }
        else:
            # Create new user with default roles
            default_roles = ["ALL"]
            cur.execute("""
                INSERT INTO users (email, name, roles, is_admin)
                VALUES (%s, %s, %s, %s)
            """, (email, name or email.split('@')[0], json.dumps(default_roles), False))
            conn.commit()
            conn.close()
            
            print(f"OK: New user created: {email}, is_admin: False")
            return {
                "email": email,
                "name": name or email.split('@')[0],
                "roles": default_roles,
                "is_admin": False
            }
    except Exception as e:
        print(f"ERROR: Error in user login: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def list_users(authorization: Optional[str] = None, user_email: Optional[str] = None) -> Dict:
    """List all users (admin only)"""
    try:
        # Verify admin access
        if not user_email:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT is_admin FROM users WHERE email = %s", (user_email,))
        user_data = cur.fetchone()
        
        if not user_data or not user_data['is_admin']:
            conn.close()
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Get all users
        cur.execute("SELECT email, name, roles, is_admin FROM users ORDER BY email")
        users = cur.fetchall()
        conn.close()
        
        # Parse roles
        for user in users:
            try:
                user['roles'] = json.loads(user['roles']) if isinstance(user['roles'], str) else user['roles']
            except:
                user['roles'] = ["ALL"]
        
        return {"users": users, "count": len(users)}
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Error listing users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def update_user_roles(email: str, roles: List[str], is_admin: bool, user_email: Optional[str] = None) -> Dict:
    """Update user roles (admin only)"""
    try:
        # Verify admin access
        if not user_email:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT is_admin FROM users WHERE email = %s", (user_email,))
        admin_data = cur.fetchone()
        
        if not admin_data or not admin_data['is_admin']:
            conn.close()
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Update user
        cur.execute("""
            UPDATE users
            SET roles = %s, is_admin = %s
            WHERE email = %s
        """, (json.dumps(roles), is_admin, email))
        
        if cur.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        conn.close()
        print(f"OK: User roles updated: {email}, is_admin: {is_admin}")
        return {"success": True, "message": "User roles updated"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Error updating user roles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def delete_user(email: str, user_email: Optional[str] = None) -> Dict:
    """Delete user (admin only)"""
    try:
        # Verify admin access
        if not user_email:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT is_admin FROM users WHERE email = %s", (user_email,))
        admin_data = cur.fetchone()
        
        if not admin_data or not admin_data['is_admin']:
            conn.close()
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Prevent self-deletion
        if email == user_email:
            conn.close()
            raise HTTPException(status_code=400, detail="Cannot delete yourself")
        
        # Delete user
        cur.execute("DELETE FROM users WHERE email = %s", (email,))
        
        if cur.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        conn.close()
        print(f"OK: User deleted: {email}")
        return {"success": True, "message": "User deleted"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def set_admin_user(email: str, admin_key: Optional[str] = None) -> Dict:
    """Set user as admin (requires admin key)"""
    try:
        # Verify admin key
        expected_key = "MIGRATE_2025_SECRET"  # Should be in config
        if admin_key != expected_key:
            raise HTTPException(status_code=403, detail="Invalid admin key")
        
        conn = get_db()
        cur = conn.cursor()
        
        # Update user to admin
        cur.execute("""
            UPDATE users
            SET is_admin = TRUE
            WHERE email = %s
        """, (email,))
        
        if cur.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        conn.close()
        print(f"OK: User set as admin: {email}")
        return {"success": True, "message": f"User {email} is now an admin"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: Error setting admin user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

