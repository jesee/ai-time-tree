import logging
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.core.database import engine, Base
# We need to import the models so that Base knows about them
from app.models import article

logging.basicConfig(level=logging.INFO)

def initialize_database():
    """
    Connects to the database and creates all tables
    based on the defined SQLAlchemy models.
    """
    logging.info("Initializing database...")
    try:
        # The create_all function checks for the existence of tables
        # before creating them, so it's safe to run multiple times.
        Base.metadata.create_all(bind=engine)
        logging.info("Database tables created successfully (if they didn't exist).")
    except Exception as e:
        logging.error(f"An error occurred during database initialization: {e}")

if __name__ == "__main__":
    initialize_database()
