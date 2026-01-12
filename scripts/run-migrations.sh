#!/bin/bash
# Database Migration Script
# Runs all SQL files from data_adapter/sql-postgres/ in order
#
# Usage:
#   Local (with psql):  ./scripts/run-migrations.sh
#   Heroku:             ./scripts/run-migrations.sh --heroku <app-name>
#
# Examples:
#   ./scripts/run-migrations.sh --heroku ssq-api-staging
#   ./scripts/run-migrations.sh --heroku ssq-api-production

set -e

SQL_DIR="data_adapter/sql-postgres"

# Check if SQL directory exists
if [ ! -d "$SQL_DIR" ]; then
    echo "Error: SQL directory not found: $SQL_DIR"
    echo "Please run this script from the project root directory."
    exit 1
fi

# Count SQL files
SQL_FILES=$(ls -1 "$SQL_DIR"/*.sql 2>/dev/null | sort)
FILE_COUNT=$(echo "$SQL_FILES" | wc -l | tr -d ' ')

if [ -z "$SQL_FILES" ] || [ "$FILE_COUNT" -eq 0 ]; then
    echo "No SQL files found in $SQL_DIR"
    exit 0
fi

echo "Found $FILE_COUNT SQL files to execute"
echo "========================================"

if [ "$1" == "--heroku" ] && [ -n "$2" ]; then
    APP_NAME="$2"
    echo "Target: Heroku app '$APP_NAME'"
    echo ""

    for sql_file in $SQL_FILES; do
        filename=$(basename "$sql_file")
        echo "Executing: $filename"
        heroku pg:psql -a "$APP_NAME" --file "$sql_file"
        echo "  Done"
    done
else
    echo "Target: Local PostgreSQL"
    echo "Using: host=${SSQ_DB_HOST:-localhost}, db=${SSQ_DB_NAME:-ssq_db}, user=${SSQ_DB_USER:-postgres}"
    echo ""

    for sql_file in $SQL_FILES; do
        filename=$(basename "$sql_file")
        echo "Executing: $filename"
        PGPASSWORD="${SSQ_DB_PASSWORD:-postgres}" psql \
            -h "${SSQ_DB_HOST:-localhost}" \
            -p "${SSQ_DB_PORT:-5432}" \
            -U "${SSQ_DB_USER:-postgres}" \
            -d "${SSQ_DB_NAME:-ssq_db}" \
            -f "$sql_file" \
            --quiet
        echo "  Done"
    done
fi

echo ""
echo "========================================"
echo "All migrations completed successfully!"
