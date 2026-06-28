import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Generator function to get a database session.
    Yields a session and ensures it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    # Sanity check query
    from sqlalchemy import text
    try:
        with SessionLocal() as db:
            result = db.execute(text("SELECT current_database();")).scalar()
            print(f"Successfully connected to database: {result}")
            
            # Check table counts
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
