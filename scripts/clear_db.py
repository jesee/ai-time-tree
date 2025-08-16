import logging
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.core.database import SessionLocal, engine
from app.models.article import Article

logging.basicConfig(level=logging.INFO)

def clear_articles_table():
    """Deletes all records from the articles table."""
    db = SessionLocal()
    try:
        num_rows_deleted = db.query(Article).delete()
        db.commit()
        logging.info(f"Successfully deleted {num_rows_deleted} rows from the articles table.")
    except Exception as e:
        logging.error(f"An error occurred while clearing the table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_articles_table()
