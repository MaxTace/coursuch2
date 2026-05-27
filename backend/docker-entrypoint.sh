#!/bin/sh
set -e

echo "Waiting for database..."
python - <<'PY'
import os, time
from urllib.parse import urlparse
import psycopg2

url = os.environ.get('DATABASE_URL', '')
if not url:
    print("No DATABASE_URL, skipping wait.")
    raise SystemExit(0)

parsed = urlparse(url)
for attempt in range(30):
    try:
        conn = psycopg2.connect(
            dbname=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port,
        )
        conn.close()
        print("Database is ready.")
        break
    except Exception as exc:
        print(f"Not ready ({attempt+1}/30): {exc}")
        time.sleep(2)
else:
    print("Database never became ready, aborting.")
    raise SystemExit(1)
PY

echo "Running seed..."
python seed.py

exec "$@"
