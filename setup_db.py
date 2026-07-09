import os, sys
sys.path.insert(0, '/app')
from storage.scripts.db_connect import get_db, get_engine
from storage.models.db_models import Base

print("Creating all tables...")
Base.metadata.create_all(bind=get_engine())
print("Tables created successfully!")

from sqlalchemy import inspect
inspector = inspect(get_engine())
tables = inspector.get_table_names()
print(f"Tables: {tables}")
