import sqlite3
import json
import re
from pathlib import Path

class Database:
    def __init__(self, db_path="../data/prompts.db"):
        self.db_path = Path(__file__).parent.parent / "data" / "prompts.db"
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY,
                code TEXT UNIQUE,
                name TEXT,
                categories TEXT,
                content TEXT,
                variables TEXT,
                output_folder TEXT,
                is_active INTEGER DEFAULT 1
            )
        """)
        
        if conn.execute("SELECT COUNT(*) FROM prompts").fetchone()[0] == 0:
            defaults = [
                ('email_reply', 'Email Reply', ['general'], 
                 'Reply to {{sender}} about {{subject}}:\n{{content}}', ''),
                ('hr_contract', 'HR Contract', ['hr'],
                 'Contract for {{name}}, Position: {{position}}, Salary: {{salary}}',
                 'drive://folder/hr_contracts'),
                ('code_review', 'Code Review', ['dev'],
                 'Review PR #{{pr_number}} in {{repo}}',
                 'github://org/reviews')
            ]
            
            for code, name, cats, content, output in defaults:
                vars = re.findall(r'\{\{(\w+)\}\}', content)
                conn.execute(
                    "INSERT INTO prompts VALUES (NULL,?,?,?,?,?,?,1)",
                    (code, name, json.dumps(cats), content, json.dumps(vars), output)
                )
        
        conn.commit()
        conn.close()
    
    def get_all(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM prompts WHERE is_active=1").fetchall()
        conn.close()
        
        prompts = []
        for row in rows:
            p = dict(row)
            p['categories'] = json.loads(p['categories'])
            p['variables'] = json.loads(p['variables'])
            prompts.append(p)
        return prompts
    
    def get_one(self, code):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM prompts WHERE code=? AND is_active=1", (code,)).fetchone()
        conn.close()
        
        if row:
            p = dict(row)
            p['categories'] = json.loads(p['categories'])
            p['variables'] = json.loads(p['variables'])
            return p
        return None
    
    def create(self, code, name, categories, content, output_folder=''):
        vars = re.findall(r'\{\{(\w+)\}\}', content)
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                "INSERT INTO prompts VALUES (NULL,?,?,?,?,?,?,1)",
                (code, name, json.dumps(categories), content, json.dumps(vars), output_folder)
            )
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()
    
    def delete(self, code):
        conn = sqlite3.connect(self.db_path)
        conn.execute("UPDATE prompts SET is_active=0 WHERE code=?", (code,))
        conn.commit()
        conn.close()