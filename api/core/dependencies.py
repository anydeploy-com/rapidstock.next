from typing import Generator
import importlib


def get_db() -> Generator:
    # Lazy import to avoid import path issues during tooling/analysis
    SessionLocal = importlib.import_module("db.session").SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

