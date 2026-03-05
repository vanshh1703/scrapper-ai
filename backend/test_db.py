import sys
try:
    from core.config import settings
    from sqlalchemy import create_engine
    engine = create_engine(settings.DATABASE_URL)
    connection = engine.connect()
    connection.close()
    with open("err.txt", "w", encoding="utf-8") as f:
        f.write("SUCCESS")
except Exception as e:
    with open("err.txt", "w", encoding="utf-8") as f:
        f.write(f"DATABASE_ERROR: {e}")
