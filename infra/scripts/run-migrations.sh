#!/bin/bash
# ============================================
# Database Migration Runner
# ============================================
# Usage:
#   ./run-migrations.sh           # Run all pending migrations
#   ./run-migrations.sh --status  # Show migration status
# ============================================

set -e

DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-aap_db}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres123}"

MIGRATIONS_DIR="/migrations"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "========================================"
echo "  Database Migration Runner"
echo "========================================"
echo ""

# Wait for database to be ready
echo "Waiting for database to be ready..."
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  echo "  Postgres is unavailable - sleeping"
  sleep 2
done

echo -e "${GREEN}Database is ready!${NC}"
echo ""

# Check if showing status only
if [ "$1" = "--status" ]; then
    echo "Migration Status:"
    echo "----------------"
    PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "
        SELECT version, description, applied_at
        FROM schema_migrations
        ORDER BY applied_at;
    "
    exit 0
fi

# Run migrations
echo "Running migrations..."
echo ""

PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$MIGRATIONS_DIR/run-migrations.sql"

echo ""
echo -e "${GREEN}Migrations completed successfully!${NC}"
