import json
import pg8000
import os
from datetime import datetime
import boto3

# --- DB config ---
DB_HOST = os.environ.get("DB_HOST")
DB_NAME = os.environ.get("DB_NAME", "aapdb")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_SECRET_ARN = os.environ.get("DB_SECRET_ARN")

def get_db_credentials():
    """Get DB credentials from Secrets Manager or environment"""
    if DB_SECRET_ARN:
        try:
            client = boto3.client("secretsmanager", region_name="ap-southeast-1")
            resp = client.get_secret_value(SecretId=DB_SECRET_ARN)
            sec = json.loads(resp["SecretString"])
            return sec.get("username", "dbadmin"), sec.get("password", "AapDemo2025!")
        except Exception as e:
            print(f"Error getting secret: {e}")
            # Fallback
            return "dbadmin", "AapDemo2025!"
    else:
        return os.environ.get("DB_USER", "dbadmin"), os.environ.get("DB_PASS", "AapDemo2025!")

# --- CORS headers ---
CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
    "Access-Control-Allow-Headers": "*"
}

def _response(status: int, body: dict):
    return {
        "statusCode": status,
        "headers": CORS_HEADERS,
        "body": json.dumps(body, default=str)
    }

def lambda_handler(event, context):
    # Support both event formats
    if "requestContext" in event and "http" in event.get("requestContext", {}):
        method = event["requestContext"]["http"]["method"]
        path = event.get("rawPath", "/")
    else:
        method = event.get("httpMethod", "GET")
        path = event.get("path", "/")
    
    print(f"Method: {method}, Path: {path}")
    
    # Handle OPTIONS
    if method == "OPTIONS":
        return _response(200, {"message": "CORS OK"})
    
    # Health check without DB
    if path in ["/", "/health"]:
        return _response(200, {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "aap-api"
        })
    
    # Parse body
    body = {}
    if event.get("body"):
        try:
            body = json.loads(event["body"])
        except:
            body = {}
    
    # Routes that need DB
    try:
        user, pwd = get_db_credentials()
        print(f"Connecting to DB: {DB_HOST}:{DB_PORT}/{DB_NAME} as {user}")
        
        conn = pg8000.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=user,
            password=pwd,
            timeout=10
        )
        cur = conn.cursor()
        result = {}
        
        if path == "/api/prompts" and method == "GET":
            cur.execute("""
                SELECT p.id, p.code, p.name, p.description, p.category, p.is_active,
                       p.created_at, p.updated_at
                FROM prompts p
                WHERE p.is_active = TRUE
                ORDER BY p.created_at DESC
            """)
            
            cols = [d[0] for d in cur.description]
            prompts = []
            for row in cur.fetchall():
                p = dict(zip(cols, row))
                if p.get("created_at"):
                    p["created_at"] = p["created_at"].isoformat()
                if p.get("updated_at"):
                    p["updated_at"] = p["updated_at"].isoformat()
                prompts.append(p)
            
            result = {"prompts": prompts, "count": len(prompts)}
        
        elif path == "/api/prompts" and method == "POST":
            code = body.get("code")
            name = body.get("name")
            
            if not code or not name:
                return _response(400, {"error": "code and name required"})
            
            cur.execute("""
                INSERT INTO prompts (code, name, description, category)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (code) DO UPDATE
                SET name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    updated_at = NOW()
                RETURNING id
            """, (code, name, body.get("description", ""), body.get("category", "general")))
            
            pid = cur.fetchone()[0]
            
            # Try to insert version
            try:
                cur.execute("""
                    INSERT INTO prompt_versions (prompt_id, content, arguments_json, is_default)
                    VALUES (%s, %s, %s, TRUE)
                    ON CONFLICT DO NOTHING
                """, (pid, body.get("content", ""), json.dumps(body.get("arguments", []))))
            except:
                pass  # Version table might not exist
            
            conn.commit()
            result = {"success": True, "prompt_id": pid, "code": code}
        
        elif path.startswith("/api/prompts/") and method == "GET":
            code = path.split("/")[-1]
            cur.execute("""
                SELECT * FROM prompts WHERE code = %s AND is_active = TRUE
            """, (code,))
            row = cur.fetchone()
            
            if row:
                cols = [d[0] for d in cur.description]
                prompt = dict(zip(cols, row))
                if prompt.get("created_at"):
                    prompt["created_at"] = prompt["created_at"].isoformat()
                if prompt.get("updated_at"):
                    prompt["updated_at"] = prompt["updated_at"].isoformat()
                result = prompt
            else:
                result = {"error": "not found"}
        
        elif path.startswith("/api/prompts/") and method == "PUT":
            code = path.split("/")[-1]
            cur.execute("""
                UPDATE prompts
                SET name = COALESCE(%s, name),
                    description = COALESCE(%s, description),
                    category = COALESCE(%s, category),
                    updated_at = NOW()
                WHERE code = %s
                RETURNING id
            """, (body.get("name"), body.get("description"), body.get("category"), code))
            
            if cur.fetchone():
                conn.commit()
                result = {"success": True}
            else:
                result = {"error": "not found"}
        
        elif path.startswith("/api/prompts/") and method == "DELETE":
            code = path.split("/")[-1]
            cur.execute("""
                UPDATE prompts SET is_active = FALSE, updated_at = NOW()
                WHERE code = %s RETURNING id
            """, (code,))
            
            if cur.fetchone():
                conn.commit()
                result = {"success": True}
            else:
                result = {"error": "not found"}
        
        else:
            result = {"error": f"Route not found: {method} {path}"}
        
        cur.close()
        conn.close()
        return _response(200, result)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        return _response(500, {
            "error": str(e),
            "type": type(e).__name__
        })