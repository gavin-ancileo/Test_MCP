"""
ClaimHub router
API endpoints for ClaimHub database queries
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_db
import psycopg2

router = APIRouter(tags=["claimhub"])


@router.get("/claimhub/test")
@router.get("/mcp-server/claimhub/test")
async def test_claimhub_connection():
    """Test ClaimHub database connection"""
    try:
        from config import CONFIG
        # ClaimHub uses PostgreSQL with database name 'assessment'
        conn = psycopg2.connect(
            host=CONFIG.get('CLAIMHUB_DB_HOST', CONFIG['DB_HOST']),
            port=CONFIG.get('CLAIMHUB_DB_PORT', '5432'),
            database='assessment',
            user=CONFIG.get('CLAIMHUB_DB_USER', CONFIG['DB_USER']),
            password=CONFIG.get('CLAIMHUB_DB_PASSWORD', CONFIG['DB_PASSWORD'])
        )
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return {"status": "connected", "database": "assessment"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/claimhub/tables")
@router.get("/mcp-server/claimhub/tables")
async def list_claimhub_tables():
    """List all tables in ClaimHub database"""
    try:
        from config import CONFIG
        conn = psycopg2.connect(
            host=CONFIG.get('CLAIMHUB_DB_HOST', CONFIG['DB_HOST']),
            port=CONFIG.get('CLAIMHUB_DB_PORT', '5432'),
            database='assessment',
            user=CONFIG.get('CLAIMHUB_DB_USER', CONFIG['DB_USER']),
            password=CONFIG.get('CLAIMHUB_DB_PASSWORD', CONFIG['DB_PASSWORD'])
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return {"tables": tables, "count": len(tables)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/claimhub/table/{table_name}")
@router.get("/mcp-server/claimhub/table/{table_name}")
async def describe_claimhub_table(table_name: str):
    """Describe ClaimHub table structure"""
    try:
        from config import CONFIG
        conn = psycopg2.connect(
            host=CONFIG.get('CLAIMHUB_DB_HOST', CONFIG['DB_HOST']),
            port=CONFIG.get('CLAIMHUB_DB_PORT', '5432'),
            database='assessment',
            user=CONFIG.get('CLAIMHUB_DB_USER', CONFIG['DB_USER']),
            password=CONFIG.get('CLAIMHUB_DB_PASSWORD', CONFIG['DB_PASSWORD'])
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s AND table_schema = 'public'
            ORDER BY ordinal_position
        """, (table_name,))
        columns = [{"name": row[0], "type": row[1], "nullable": row[2]} for row in cur.fetchall()]
        cur.close()
        conn.close()
        return {"table": table_name, "columns": columns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/claimhub/query")
@router.post("/mcp-server/claimhub/query")
async def query_claimhub(query: dict):
    """Execute SQL query on ClaimHub database"""
    try:
        from config import CONFIG
        sql = query.get('query') or query.get('sql')
        if not sql:
            raise HTTPException(status_code=400, detail="SQL query is required")
        
        conn = psycopg2.connect(
            host=CONFIG.get('CLAIMHUB_DB_HOST', CONFIG['DB_HOST']),
            port=CONFIG.get('CLAIMHUB_DB_PORT', '5432'),
            database='assessment',
            user=CONFIG.get('CLAIMHUB_DB_USER', CONFIG['DB_USER']),
            password=CONFIG.get('CLAIMHUB_DB_PASSWORD', CONFIG['DB_PASSWORD'])
        )
        cur = conn.cursor()
        cur.execute(sql)
        
        # Get column names
        columns = [desc[0] for desc in cur.description] if cur.description else []
        
        # Fetch results
        rows = cur.fetchall()
        data = [dict(zip(columns, row)) for row in rows]
        
        cur.close()
        conn.close()
        return {"row_count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

