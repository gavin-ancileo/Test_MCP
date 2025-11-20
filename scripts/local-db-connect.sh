#!/bin/bash
# Easy wrapper to connect to RDS database via port forwarding
# Usage: ./local-db-connect.sh [psql-command]

LOCAL_PORT="5432"
DB_NAME="${DB_NAME:-aap_db}"
DB_USER="${DB_USER:-postgres}"

echo "🔗 Connecting to database via port forwarding..."
echo "   Make sure port forwarding is running in another terminal:"
echo "   ./scripts/local-db-port-forward.sh"
echo ""

if [ -z "$1" ]; then
  # Interactive psql session
  psql -h localhost -p $LOCAL_PORT -U $DB_USER -d $DB_NAME
else
  # Execute command
  psql -h localhost -p $LOCAL_PORT -U $DB_USER -d $DB_NAME -c "$1"
fi









