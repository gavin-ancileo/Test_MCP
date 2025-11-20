#!/usr/bin/env python3
"""
Set gavin.pham@ancileo.com as admin user in production RDS
"""
import psycopg2
import json

# RDS connection details
DB_CONFIG = {
    'host': 'aap-rds-new.cv2usk6ye3hm.ap-southeast-2.rds.amazonaws.com',
    'port': 5432,
    'database': 'prompts',
    'user': 'AncileoMaster',
    'password': 'AncileoAAP2025SecureDB#'
}

def set_admin_user():
    """Set gavin.pham@ancileo.com as admin"""
    try:
        print("Connecting to RDS...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        print("Setting gavin.pham@ancileo.com as admin...")
        cur.execute("""
            INSERT INTO users (email, name, roles, is_admin)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE
            SET is_admin = TRUE, roles = '["ALL"]', name = 'Gavin Pham'
        """, ('gavin.pham@ancileo.com', 'Gavin Pham', json.dumps(["ALL"]), True))

        conn.commit()

        # Verify
        cur.execute("""
            SELECT email, name, is_admin, roles, created_at
            FROM users
            WHERE email = %s
        """, ('gavin.pham@ancileo.com',))

        user = cur.fetchone()
        if user:
            print("\n✅ SUCCESS! User updated:")
            print(f"   Email: {user[0]}")
            print(f"   Name: {user[1]}")
            print(f"   Is Admin: {user[2]}")
            print(f"   Roles: {user[3]}")
            print(f"   Created: {user[4]}")
        else:
            print("❌ User not found after update")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    set_admin_user()
