#!/bin/sh
set -e

if [ -n "$DATABASE_URL" ]; then
  echo "Waiting for database connection..."
  python - <<'PY'
import os
import time
from urllib.parse import urlparse
import psycopg2

url = os.environ.get('DATABASE_URL')
parsed = urlparse(url)

while True:
    try:
        conn = psycopg2.connect(
            dbname=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port,
        )
        conn.close()
        print('Database is ready')
        break
    except Exception as exc:
        print('Database not ready, retrying...', exc)
        time.sleep(2)
PY
fi

exec "$@"
