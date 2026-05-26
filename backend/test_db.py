from sqlalchemy import create_engine
from config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute("SELECT 1")
    print(result.scalar())
