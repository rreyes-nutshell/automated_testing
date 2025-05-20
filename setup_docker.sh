#!/bin/bash

set -e

echo "📦 Creating Dockerized Flask+Ollama+Postgres environment..."

# Create .env
cat <<EOF > .env
FLASK_SECRET_KEY=supersecret
DEBUG_MODE=true

DB_HOST=db
DB_PORT=5432
DB_NAME=yourdb
DB_USER=youruser
DB_PASSWORD=yourpassword

OLLAMA_URL=http://ollama:11434
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
EOF
echo "✅ .env created"

# Create requirements.txt if not present
if [ ! -f requirements.txt ]; then
	cat <<EOF > requirements.txt
Flask==2.3.2
psycopg2-binary==2.9.9
requests
EOF
	echo "✅ requirements.txt created"
fi

# Create entrypoint.sh
cat <<'EOF' > entrypoint.sh
#!/bin/bash
set -e

echo "⏳ Waiting for Postgres at \$DB_HOST:\$DB_PORT..."
until pg_isready -h "\$DB_HOST" -p "\$DB_PORT" -U "\$DB_USER" >/dev/null 2>&1; do
	echo "❌ Postgres is unavailable - retrying in 1s..."
	sleep 1
done

echo "✅ Postgres is available - starting Flask app"
exec python app.py
EOF
chmod +x entrypoint.sh
echo "✅ entrypoint.sh created"

# Create Dockerfile
cat <<'EOF' > Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["./entrypoint.sh"]
EOF
echo "✅ Dockerfile created"

# Create docker-compose.yml
cat <<'EOF' > docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    container_name: flask_app
    ports:
      - "5000:5000"
    env_file:
      - .env
    volumes:
      - .:/app
    depends_on:
      - db
      - ollama

  db:
    image: postgres:15
    container_name: postgres_db
    environment:
      POSTGRES_USER: youruser
      POSTGRES_PASSWORD: yourpassword
      POSTGRES_DB: yourdb
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U youruser"]
      interval: 5s
      timeout: 3s
      retries: 5

  ollama:
    image: ollama/ollama
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    entrypoint: >
      sh -c "ollama serve & sleep 2 && ollama run mistral && tail -f /dev/null"

volumes:
  pgdata:
  ollama_data:
EOF
echo "✅ docker-compose.yml created"

# Create override file
cat <<'EOF' > docker-compose.override.yml
version: '3.8'

services:
  web:
    environment:
      - OLLAMA_HOST=localhost
      - OLLAMA_PORT=11434
      - FLASK_ENV=development
EOF
echo "✅ docker-compose.override.yml created"

echo "🎉 All Docker components generated successfully."
echo "▶️ Run: docker-compose up --build"

