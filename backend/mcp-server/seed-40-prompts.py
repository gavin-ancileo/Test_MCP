#!/usr/bin/env python3
"""
Seed 40 prompts into the database
This file is used by app.py on startup to populate prompts
"""
from prompts_data import PROMPTS_DATA

def get_seed_sql():
    """Generate SQL to seed 40 prompts"""
    values = []
    for code, name, categories, content in PROMPTS_DATA:
        # Escape single quotes in content
        content_escaped = content.replace("'", "''")
        values.append(f"('{code}', '{name}', '{categories}', '{content_escaped}')")

    sql = f"""
-- Seed 40 prompts
TRUNCATE TABLE prompts RESTART IDENTITY CASCADE;

INSERT INTO prompts (code, name, categories, content) VALUES
{',\n'.join(values)};
"""
    return sql

if __name__ == "__main__":
    print(get_seed_sql())