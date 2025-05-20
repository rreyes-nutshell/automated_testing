#!/bin/bash
set -e

echo "🐞 Entrypoint started"
echo "📌 DB_HOST=$DB_HOST"
echo "📌 DB_PORT=$DB_PORT"
echo "📌 DB_USER=$DB_USER"
echo "📌 DB_NAME=$DB_NAME"

echo "⏳ Waiting for Postgres to be ready..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" --dbname="$DB_NAME" >/dev/null 2>&1; do
	echo "$(date '+%Y-%m-%d %H:%M:%S') ❌ Postgres is unavailable - retrying in 1s..."
	sleep 1
done

echo "✅ Postgres is available — running DB bootstrap"
python -c "from utils.bootstrap_db import bootstrap_schema; bootstrap_schema()"

echo "🚀 Starting app"
exec python app.py
