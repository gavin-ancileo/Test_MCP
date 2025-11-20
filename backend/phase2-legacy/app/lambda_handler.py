import json, pg8000, os
from datetime import datetime

DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_NAME = os.environ.get("DB_NAME", "aapdb")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Credentials": "true"
}

def _resp(status, body):
    return {
        "statusCode": status, 
        "headers": CORS_HEADERS, 
        "body": json.dumps(body, default=str)
    }

def lambda_handler(event, context):
    # Get method and path from different event formats
    if "requestContext" in event:
        # Lambda Function URL format
        method = event.get("requestContext", {}).get("http", {}).get("method", "GET")
        path = event.get("rawPath", "/")
    else:
        # API Gateway format
        method = event.get("httpMethod", "GET")
        path = event.get("path", "/")
    
    # Handle preflight OPTIONS for CORS
    if method == "OPTIONS":
        return _resp(200, {"message": "OK"})

    # Parse body
    body = {}
    if event.get("body"):
        try: 
            body = json.loads(event["body"])
        except: 
            pass

    try:
        conn = pg8000.connect(
            host=DB_HOST, port=DB_PORT, database=DB_NAME,
            user=DB_USER, password=DB_PASS, timeout=10
        )
        cur = conn.cursor()

        # /health
        if path == "/health" or path == "/":
            return _resp(200, {
                "status": "healthy",
                "service": "aap-api",
                "timestamp": datetime.utcnow().isoformat(),
                "database": "connected"
            })

        # GET /api/prompts
        if path == "/api/prompts" and method == "GET":
            cur.execute("""
                SELECT p.id, p.code, p.name, p.description, p.category, p.is_active,
                       p.created_at, p.updated_at, pv.version, pv.content, pv.arguments_json
                FROM prompts p
                LEFT JOIN prompt_versions pv ON p.id = pv.prompt_id AND pv.is_default = TRUE
                WHERE p.is_active = TRUE 
                ORDER BY p.created_at DESC
            """)
            
            cols = [d[0] for d in cur.description]
            rows = []
            for row in cur.fetchall():
                r = dict(zip(cols, row))
                # Convert datetime to string
                if r.get("created_at"):
                    r["created_at"] = r["created_at"].isoformat()
                if r.get("updated_at"):
                    r["updated_at"] = r["updated_at"].isoformat()
                rows.append(r)
            
            return _resp(200, {"prompts": rows, "count": len(rows)})

        # POST /api/prompts
        if path == "/api/prompts" and method == "POST":
            code = body.get("code")
            name = body.get("name")
            
            if not code or not name:
                return _resp(400, {"error": "code and name required"})
            
            # Insert prompt
            cur.execute("""
                INSERT INTO prompts(code, name, description, category)
                VALUES(%s, %s, %s, %s)
                ON CONFLICT(code) DO UPDATE
                SET name = EXCLUDED.name, 
                    description = EXCLUDED.description, 
                    updated_at = NOW()
                RETURNING id
            """, (code, name, body.get("description", ""), body.get("category", "general")))
            
            pid = cur.fetchone()[0]
            
            # Try to insert version if content provided
            if body.get("content"):
                try:
                    cur.execute("""
                        INSERT INTO prompt_versions(prompt_id, version, content, arguments_json, is_default)
                        VALUES(%s, 1, %s, %s, TRUE)
                        ON CONFLICT (prompt_id, version) DO UPDATE
                        SET content = EXCLUDED.content,
                            arguments_json = EXCLUDED.arguments_json
                        RETURNING id
                    """, (pid, body.get("content", ""), json.dumps(body.get("arguments", []))))
                except:
                    pass  # Prompt versions table might not exist
            
            conn.commit()
            return _resp(200, {"success": True, "prompt_id": pid, "message": "Prompt created successfully"})

        # GET /api/prompts/{code}
        if path.startswith("/api/prompts/") and method == "GET":
            code = path.split("/")[-1]
            cur.execute("""
                SELECT p.*, pv.version, pv.content, pv.arguments_json
                FROM prompts p
                LEFT JOIN prompt_versions pv ON p.id = pv.prompt_id AND pv.is_default = TRUE
                WHERE p.code = %s AND p.is_active = TRUE
            """, (code,))
            
            row = cur.fetchone()
            if not row:
                return _resp(404, {"error": "Prompt not found"})
            
            cols = [d[0] for d in cur.description]
            result = dict(zip(cols, row))
            
            # Convert datetime to string
            if result.get("created_at"):
                result["created_at"] = result["created_at"].isoformat()
            if result.get("updated_at"):
                result["updated_at"] = result["updated_at"].isoformat()
            
            return _resp(200, result)

        # PUT /api/prompts/{code}
        if path.startswith("/api/prompts/") and method == "PUT":
            code = path.split("/")[-1]
            
            # Update prompt
            updates = []
            params = []
            
            if body.get("name"):
                updates.append("name = %s")
                params.append(body["name"])
            
            if body.get("description"):
                updates.append("description = %s")
                params.append(body["description"])
            
            if body.get("category"):
                updates.append("category = %s")
                params.append(body["category"])
            
            if updates:
                updates.append("updated_at = NOW()")
                params.append(code)
                
                query = f"UPDATE prompts SET {', '.join(updates)} WHERE code = %s"
                cur.execute(query, params)
                conn.commit()
            
            return _resp(200, {"success": True, "message": "Prompt updated"})

        # DELETE /api/prompts/{code}
        if path.startswith("/api/prompts/") and method == "DELETE":
            code = path.split("/")[-1]
            
            cur.execute("""
                UPDATE prompts 
                SET is_active = FALSE, updated_at = NOW()
                WHERE code = %s
                RETURNING id
            """, (code,))
            
            result = cur.fetchone()
            if not result:
                return _resp(404, {"error": "Prompt not found"})
            
            conn.commit()
            return _resp(200, {"success": True, "message": f"Prompt {code} deleted"})

        return _resp(404, {"error": "Route not found", "path": path, "method": method})

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return _resp(500, {"error": str(e), "type": type(e).__name__})