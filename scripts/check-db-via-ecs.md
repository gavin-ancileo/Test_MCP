# Database Table Inspector - Instructions

Since the RDS database is in a private subnet, you need to run the check from inside the VPC (via ECS container).

## Method 1: Via ECS Exec (Recommended)

### Step 1: Find running MCP server task

```bash
aws ecs list-tasks \
  --cluster aap-cluster \
  --service-name aap-mcp-server-new \
  --region ap-southeast-2
```

### Step 2: Copy the task ARN and exec into container

```bash
# Replace TASK_ARN with actual ARN from step 1
aws ecs execute-command \
  --cluster aap-cluster \
  --task <TASK_ARN> \
  --container mcp-server \
  --command "/bin/bash" \
  --interactive \
  --region ap-southeast-2
```

### Step 3: Inside the container, install psycopg2 and run check

```bash
# Install psycopg2
pip install psycopg2-binary

# Run the database check script
cat > /tmp/check_db.py << 'EOF'
import psycopg2
import os

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cursor = conn.cursor()

# List all tables
print("\n=== ALL TABLES ===")
cursor.execute("""
    SELECT schemaname, tablename,
           pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
    FROM pg_tables
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
    ORDER BY tablename;
""")
for schema, table, size in cursor.fetchall():
    print(f"{schema}.{table} - {size}")

# Check each table
cursor.execute("""
    SELECT tablename FROM pg_tables
    WHERE schemaname = 'public'
    ORDER BY tablename;
""")
tables = cursor.fetchall()

for (table,) in tables:
    print(f"\n=== Table: {table} ===")

    # Row count
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"Rows: {count}")

    # Columns
    cursor.execute(f"""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = '{table}'
        ORDER BY ordinal_position;
    """)
    print("Columns:")
    for col, dtype, nullable in cursor.fetchall():
        print(f"  - {col}: {dtype} {'NULL' if nullable=='YES' else 'NOT NULL'}")

    # Sample data
    if count > 0:
        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        print("Sample rows:")
        for i, row in enumerate(rows, 1):
            print(f"  Row {i}:")
            for col, val in zip(cols, row):
                print(f"    {col}: {val}")

# Check users specifically
print("\n=== ALL USERS ===")
cursor.execute("SELECT email, role, is_admin, created_at FROM users ORDER BY created_at DESC")
for email, role, is_admin, created in cursor.fetchall():
    admin_str = "[ADMIN]" if is_admin else "[USER]"
    print(f"{admin_str} {email} - {role} - {created}")

cursor.close()
conn.close()
EOF

python /tmp/check_db.py
```

## Method 2: Via CloudShell (Alternative)

If ECS exec doesn't work, use AWS CloudShell:

### Step 1: Open AWS CloudShell
Go to: https://ap-southeast-2.console.aws.amazon.com/cloudshell

### Step 2: Install PostgreSQL client

```bash
sudo yum install -y postgresql15
```

### Step 3: Connect to database

```bash
export PGPASSWORD='AncileoAAP2025SecureDB#'

psql -h aap-rds-new.cv2usk6ye3hm.ap-southeast-2.rds.amazonaws.com \
     -p 5432 \
     -U AncileoMaster \
     -d prompts
```

### Step 4: Run queries

```sql
-- List all tables
\dt

-- Describe each table
\d users
\d prompts
\d oauth_states

-- Check all users
SELECT email, role, is_admin, created_at
FROM users
ORDER BY created_at DESC;

-- Check prompts
SELECT id, title, is_active, is_default, category, created_by
FROM prompts
ORDER BY created_at DESC
LIMIT 10;

-- Check oauth states
SELECT user_id, provider, state, created_at
FROM oauth_states
ORDER BY created_at DESC
LIMIT 10;
```

## Method 3: Via Application Logs

Check the MCP server logs to see database queries:

```bash
aws logs tail /ecs/aap-mcp-server-new \
  --follow \
  --region ap-southeast-2 \
  --filter-pattern "SELECT"
```

## Expected Tables

Based on the application code, you should see these tables:

1. **users** - User accounts and admin status
   - email, role, is_admin, created_at

2. **prompts** - AI prompts/templates
   - id, title, content, category, is_active, is_default, created_by, etc.

3. **oauth_states** - OAuth flow state tracking
   - user_id, provider, state, created_at

4. **conversations** - May exist if using RDS instead of DynamoDB

## Troubleshooting

If you can't connect:

1. **Check security group**: Database must allow traffic from ECS tasks
2. **Check VPC**: Database and ECS tasks must be in same VPC
3. **Check credentials**: Verify password in agentcore-updated.json
4. **Check logs**: `aws logs tail /ecs/aap-mcp-server-new --region ap-southeast-2`
