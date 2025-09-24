from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from core.config import DATABASE_URL

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


# Enable WAL mode and related performance/consistency PRAGMAs for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL;")  # Improves concurrency
        cursor.execute("PRAGMA synchronous=NORMAL;")  # Safe with WAL, faster than FULL
        cursor.execute("PRAGMA foreign_keys=ON;")  # Enforce FK constraints
    finally:
        cursor.close()


# Session factory and Base
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=True)
Base = declarative_base()

