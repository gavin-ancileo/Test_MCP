#!/usr/bin/env python3
"""
Push 40 prompts directly to database
Can be run from ECS task or locally
"""
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Import prompts data
from prompts_data import PROMPTS_DATA

def get_db():
    """Get database connection"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'aap_db'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres123'),
        cursor_factory=RealDictCursor
    )

def push_prompts():
    """Push all 40 prompts to database"""
    print("Pushing 40 prompts to database...")
    print(f"Total prompts: {len(PROMPTS_DATA)}")
    print()
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Truncate table
        print("Truncating prompts table...")
        cur.execute("TRUNCATE TABLE prompts RESTART IDENTITY CASCADE;")
        conn.commit()
        print("Table truncated.")
        print()
        
        # Insert prompts
        success_count = 0
        error_count = 0
        
        for i, (code, name, categories, content) in enumerate(PROMPTS_DATA, 1):
            try:
                # Parse categories from JSON string
                if isinstance(categories, str):
                    categories_list = json.loads(categories)
                else:
                    categories_list = categories
                
                # Insert prompt
                cur.execute("""
                    INSERT INTO prompts (code, name, categories, content, output_folder)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    code,
                    name,
                    json.dumps(categories_list),
                    content,
                    ""  # output_folder
                ))
                
                print(f"[OK] [{i}/{len(PROMPTS_DATA)}] Created: {code}")
                success_count += 1
                
            except Exception as e:
                print(f"[ERROR] [{i}/{len(PROMPTS_DATA)}] Failed: {code} - {str(e)}")
                error_count += 1
        
        conn.commit()
        print()
        print("=" * 70)
        print(f"Summary:")
        print(f"   Success: {success_count}/{len(PROMPTS_DATA)}")
        print(f"   Errors: {error_count}/{len(PROMPTS_DATA)}")
        print("=" * 70)
        
        # Verify count
        cur.execute("SELECT COUNT(*) as total FROM prompts;")
        result = cur.fetchone()
        total = result['total'] if result else 0
        
        print()
        print(f"Database now has {total} prompts")
        
        return success_count, error_count
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0, len(PROMPTS_DATA)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    success, errors = push_prompts()
    sys.exit(0 if errors == 0 else 1)

