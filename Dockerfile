FROM python:3.11-slim

WORKDIR /app

# Install PostgreSQL client for pg_isready
RUN apt update && apt install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN playwright install --with-deps



ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["./entrypoint.sh"]
