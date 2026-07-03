import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
logger = logging.getLogger(__name__)

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        _engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
        )
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


class _SessionProxy:
    """Lazy session factory that looks like SessionLocal but delays engine creation."""

    def __call__(self, **kwargs):
        return get_session_factory()(**kwargs)


SessionLocal = _SessionProxy()


def get_db():
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    from sqlalchemy import text
    try:
        with SessionLocal() as db:
            result = db.execute(text("SELECT current_database();")).scalar()
            print(f"Successfully connected to database: {result}")

            tables = ['areas', 'property_sales', 'amenities', 'area_demographics', 'crime_stats']
            print("\nRow counts per table:")
            for table in tables:
                try:
                    count = db.execute(text(f"SELECT COUNT(*) FROM {table};")).scalar()
                    print(f"  {table}: {count}")
                except Exception as e:
                    print(f"  {table}: error querying ({e})")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
