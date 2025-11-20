"""
Insurance router
API endpoints for Insurance database queries
"""

from fastapi import APIRouter, HTTPException
from database import get_db
import pymysql
import pymysql.cursors

router = APIRouter(tags=["insurance"])


@router.get("/insurance/test")
@router.get("/mcp-server/insurance/test")
async def test_insurance_connection():
    """Test Insurance database connection"""
    try:
        from config import CONFIG
        conn = pymysql.connect(
            host=CONFIG.get('INSURANCE_DB_HOST', CONFIG['DB_HOST']),
            port=int(CONFIG.get('INSURANCE_DB_PORT', '3306')),
            user=CONFIG.get('INSURANCE_DB_USER', CONFIG['DB_USER']),
            password=CONFIG.get('INSURANCE_DB_PASSWORD', CONFIG['DB_PASSWORD']),
            database=CONFIG.get('INSURANCE_DB_NAME', 'insurance'),
            cursorclass=pymysql.cursors.DictCursor
        )
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return {"status": "connected", "database": CONFIG.get('INSURANCE_DB_NAME', 'insurance')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insurance/tables")
@router.get("/mcp-server/insurance/tables")
async def list_insurance_tables():
    """List all tables in Insurance database"""
    try:
        from config import CONFIG
        conn = pymysql.connect(
            host=CONFIG.get('INSURANCE_DB_HOST', CONFIG['DB_HOST']),
            port=int(CONFIG.get('INSURANCE_DB_PORT', '3306')),
            user=CONFIG.get('INSURANCE_DB_USER', CONFIG['DB_USER']),
            password=CONFIG.get('INSURANCE_DB_PASSWORD', CONFIG['DB_PASSWORD']),
            database=CONFIG.get('INSURANCE_DB_NAME', 'insurance'),
            cursorclass=pymysql.cursors.DictCursor
        )
        cur = conn.cursor()
        cur.execute("SHOW TABLES")
        tables = [list(row.values())[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return {"tables": tables, "count": len(tables)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insurance/table/{table_name}")
@router.get("/mcp-server/insurance/table/{table_name}")
async def describe_insurance_table(table_name: str):
    """Describe Insurance table structure (columns, types, nullable)"""
    try:
        from config import CONFIG
        conn = pymysql.connect(
            host=CONFIG.get('INSURANCE_DB_HOST', CONFIG['DB_HOST']),
            port=int(CONFIG.get('INSURANCE_DB_PORT', '3306')),
            user=CONFIG.get('INSURANCE_DB_USER', CONFIG['DB_USER']),
            password=CONFIG.get('INSURANCE_DB_PASSWORD', CONFIG['DB_PASSWORD']),
            database=CONFIG.get('INSURANCE_DB_NAME', 'insurance'),
            cursorclass=pymysql.cursors.DictCursor
        )
        cur = conn.cursor()
        # Use INFORMATION_SCHEMA to get column details (similar to PostgreSQL approach)
        cur.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY, EXTRA
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
        """, (CONFIG.get('INSURANCE_DB_NAME', 'insurance'), table_name))
        columns = [{
            "name": row['COLUMN_NAME'],
            "type": row['DATA_TYPE'],
            "nullable": row['IS_NULLABLE'],
            "key": row['COLUMN_KEY'],
            "extra": row['EXTRA']
        } for row in cur.fetchall()]
        cur.close()
        conn.close()
        return {"table": table_name, "columns": columns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insurance/query")
@router.post("/mcp-server/insurance/query")
async def query_insurance(query: dict):
    """Execute SQL query on Insurance database"""
    try:
        from config import CONFIG
        sql = query.get('sql') or query.get('query')
        if not sql:
            raise HTTPException(status_code=400, detail="SQL query is required")

        conn = pymysql.connect(
            host=CONFIG.get('INSURANCE_DB_HOST', CONFIG['DB_HOST']),
            port=int(CONFIG.get('INSURANCE_DB_PORT', '3306')),
            user=CONFIG.get('INSURANCE_DB_USER', CONFIG['DB_USER']),
            password=CONFIG.get('INSURANCE_DB_PASSWORD', CONFIG['DB_PASSWORD']),
            database=CONFIG.get('INSURANCE_DB_NAME', 'insurance'),
            cursorclass=pymysql.cursors.DictCursor
        )
        cur = conn.cursor()
        cur.execute(sql)

        # Fetch results
        rows = cur.fetchall()
        data = [dict(row) for row in rows]

        cur.close()
        conn.close()
        return {"row_count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

