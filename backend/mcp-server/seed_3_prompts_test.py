#!/usr/bin/env python3
"""
Seed 3 test prompts quickly
"""
import psycopg2
import os
import json

# Database config from environment
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'aap_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres123')

# 3 test prompts
TEST_PROMPTS = [
    ('test_1', 'Test Prompt 1', '["test"]', 'Test content 1 with {{variable1}}'),
    ('test_2', 'Test Prompt 2', '["test"]', 'Test content 2 with {{variable2}}'),
    ('test_3', 'Test Prompt 3', '["test"]', 'Test content 3 with {{variable3}}')
]

def seed_test_prompts():
    """Seed 3 test prompts"""
    print(f"Connecting to {DB_HOST}:{DB_PORT}/{DB_NAME}...")
    
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    
    try:
        # Clear existing test prompts
        print("Clearing existing test prompts...")
        cur.execute("DELETE FROM prompts WHERE code LIKE 'test_%'")
        conn.commit()
        
        # Insert 3 test prompts
        print("Inserting 3 test prompts...")
        for code, name, categories, content in TEST_PROMPTS:
            cur.execute("""
                INSERT INTO prompts (code, name, categories, content)
                VALUES (%s, %s, %s, %s)
            """, (code, name, categories, content))
            print(f"✅ Created: {code}")
        
        conn.commit()
        
        # Verify
        cur.execute("SELECT COUNT(*) FROM prompts WHERE code LIKE 'test_%'")
        count = cur.fetchone()[0]
        print(f"\n✅ Successfully seeded {count} test prompts")
        
        # Show all prompts count
        cur.execute("SELECT COUNT(*) FROM prompts")
        total = cur.fetchone()[0]
        print(f"📊 Total prompts in DB: {total}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed_test_prompts()

