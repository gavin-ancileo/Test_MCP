# db.py
# Lightweight DB helpers + transaction decorator. Postgres via psycopg2.
import os, json, psycopg2, psycopg2.extras
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

DATABASE_URL = os.getenv("DATABASE_URL")

def _conn():
    if not DATABASE_URL:
        raise RuntimeError("Missing DATABASE_URL")
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)

@contextmanager
def tx():
    conn = _conn()
    try:
        with conn:
            with conn.cursor() as cur:
                yield cur
    finally:
        conn.close()

# --------- CRUD helpers ----------
def create_prompt(cur, code: str, name: str) -> int:
    cur.execute("""INSERT INTO prompts(code, name) VALUES (%s,%s)
                   ON CONFLICT (code) DO UPDATE SET name=EXCLUDED.name
                   RETURNING id""", (code, name))
    return cur.fetchone()["id"]

def create_prompt_version(cur, prompt_id: int, version: int,
                          arguments: List[Dict[str,Any]], rules: Dict[str,Any],
                          is_default: bool=True) -> int:
    cur.execute("""INSERT INTO prompt_versions(prompt_id, version, arguments_json, rules_json, is_default)
                   VALUES (%s,%s,%s::jsonb,%s::jsonb,%s)
                   ON CONFLICT (prompt_id,version) DO UPDATE
                   SET arguments_json=EXCLUDED.arguments_json, rules_json=EXCLUDED.rules_json,
                       is_default=EXCLUDED.is_default
                   RETURNING id""",
                   (prompt_id, version, json.dumps(arguments), json.dumps(rules), is_default))
    return cur.fetchone()["id"]

def add_asset(cur, prompt_version_id: int, asset_key: str, provider: str, uri: str, mime: str):
    cur.execute("""INSERT INTO prompt_assets(prompt_version_id, asset_key, provider, uri, mime_type)
                   VALUES (%s,%s,%s,%s,%s)
                   ON CONFLICT (prompt_version_id, asset_key) DO UPDATE
                   SET provider=EXCLUDED.provider, uri=EXCLUDED.uri, mime_type=EXCLUDED.mime_type""",
                (prompt_version_id, asset_key, provider, uri, mime))

def get_default_version_by_code(code: str) -> Optional[Dict[str,Any]]:
    with tx() as cur:
        cur.execute("""SELECT pv.id as prompt_version_id, p.id as prompt_id, p.code, p.name,
                              pv.version, pv.arguments_json, pv.rules_json
                       FROM prompts p
                       JOIN prompt_versions pv ON pv.prompt_id=p.id
                       WHERE p.code=%s AND pv.is_default=true
                       LIMIT 1""", (code,))
        row = cur.fetchone()
        return row

def get_assets_by_prompt_version(pvid: int) -> Dict[str,Any]:
    with tx() as cur:
        cur.execute("""SELECT asset_key, provider, uri, mime_type
                       FROM prompt_assets WHERE prompt_version_id=%s""", (pvid,))
        rows = cur.fetchall()
        return {r["asset_key"]: {"provider": r["provider"], "uri": r["uri"], "mime_type": r["mime_type"]} for r in rows}

def list_all_tools() -> List[Dict[str,Any]]:
    with tx() as cur:
        cur.execute("""SELECT p.code, p.name, pv.arguments_json
                       FROM prompts p JOIN prompt_versions pv ON pv.prompt_id=p.id
                       WHERE pv.is_default = true""")
        return cur.fetchall()

def record_execution_start(cur, pvid: int, user_id: str) -> int:
    cur.execute("""INSERT INTO executions(prompt_version_id,user_id,status)
                   VALUES (%s,%s,'running') RETURNING id""", (pvid, user_id))
    return cur.fetchone()["id"]

def record_execution_io(cur, ex_id: int, role: str, data: Dict[str,Any]):
    cur.execute("""INSERT INTO execution_io(execution_id,role,data_json)
                   VALUES (%s,%s,%s::jsonb)""", (ex_id, role, json.dumps(data)))

def record_execution_finish(cur, ex_id: int, status: str, artifacts: Dict[str,Any]):
    cur.execute("""UPDATE executions SET status=%s, finished_at=now(), artifacts_json=%s::jsonb WHERE id=%s""",
                (status, json.dumps(artifacts), ex_id))

def update_rules_json(code: str, version: int, patch: Dict[str,Any]) -> bool:
    """Shallow+deep merge patch into rules_json."""
    with tx() as cur:
        cur.execute("""SELECT pv.id, pv.rules_json FROM prompt_versions pv
                       JOIN prompts p ON p.id=pv.prompt_id
                       WHERE p.code=%s AND pv.version=%s""", (code, version))
        row = cur.fetchone()
        if not row: return False
        pvid, rules = row["id"], row["rules_json"] or {}
        def merge(a,b):
            if isinstance(a, dict) and isinstance(b, dict):
                out = dict(a)
                for k,v in b.items(): out[k] = merge(out.get(k), v)
                return out
            return b if b is not None else a
        new_rules = merge(rules, patch)
        cur.execute("UPDATE prompt_versions SET rules_json=%s::jsonb WHERE id=%s",
                    (json.dumps(new_rules), pvid))
        return True
