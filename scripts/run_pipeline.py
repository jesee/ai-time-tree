import logging
import sys
import os
import json

# Configure logging right at the start
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("--- Script execution started ---")

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
logging.info("Project root added to path.")

# Explicitly load .env file to ensure configuration is set before imports
from dotenv import load_dotenv
dotenv_path = os.path.join(project_root, '.env')
logging.info("Attempting to load .env file...")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    logging.info(f"Loaded .env file from: {dotenv_path}")
else:
    logging.warning(".env file not found, using environment variables.")
logging.info(".env loading process finished.")

# Import our modules
logging.info("Importing local modules (scraper, summarizer)...")
from scripts import scraper
from scripts import summarizer
from app.crud import article as crud_article
from app.core.database import SessionLocal
logging.info("Local modules imported successfully.")

def main_pipeline():
    """
    Executes the full data processing pipeline:
    1. Scrapes article URLs.
    2. Checks for new articles against the database.
    3. Fetches content for new articles.
    4. Summarizes content with AI.
    5. Saves the result to the database.
    """
    logging.info("🚀 Starting the AI Time Tree data pipeline...")
    
    db = None
    try:
        db = SessionLocal()
        
        # 1. Scrape article URLs from the main page
        logging.info("Step 1: Fetching article list from aivi.fyi...")
        articles_from_web = scraper.fetch_article_urls(scraper.TARGET_URL)
        
        if not articles_from_web:
            logging.warning("No articles found on the website. Pipeline finished.")
            return

        logging.info(f"Found {len(articles_from_web)} articles on the website. Processing...")
        
        new_articles_processed = 0
        # We process in reverse to handle the oldest articles first
        for article_info in reversed(articles_from_web):
            url = article_info['url']
            title = article_info['title']
            
            # 2. Check if the article already exists in the DB
            existing_article = crud_article.get_article_by_url(db, url=url)
            
            if existing_article:
                logging.info(f"Article '{title}' already exists in the database. Skipping.")
                continue
            
            logging.info(f"✨ New article found: '{title}'. Starting processing.")
            
            # 3. Fetch full content for the new article
            logging.info(f"Step 2: Fetching full content for '{url}'...")
            content_details = scraper.fetch_article_content(url)
            
            if not content_details or not content_details.get("content"):
                logging.error(f"Could not fetch content for '{title}'. Skipping.")
                continue
            
            # 4. Summarize with AI
            logging.info(f"Step 3: Summarizing article with AI...")
            ai_result = summarizer.summarize_article_with_ai(
                title=title,
                content=content_details["content"]
            )
            
            if not ai_result:
                logging.error(f"AI summarization failed for '{title}'. Skipping.")
                continue
            
            # 5. Save to database
            logging.info(f"Step 4: Saving article '{title}' to the database...")
            
            # The 'skills' list needs to be stored as a JSON string
            skills_json_string = json.dumps(ai_result['skills'], ensure_ascii=False)
            
            crud_article.create_article(
                db=db,
                title=title,
                url=url,
                published_date=content_details["published_date"],
                summary=ai_result["summary"],
                skills=skills_json_string
            )
            
            logging.info(f"✅ Successfully processed and saved '{title}'.")
            new_articles_processed += 1

        logging.info(f"Pipeline finished. Processed {new_articles_processed} new articles.")

    except Exception as e:
        logging.error(f"An unexpected error occurred during the pipeline: {e}", exc_info=True)
    finally:
        if db:
            db.close()
            logging.info("Database session closed.")

if __name__ == "__main__":
    main_pipeline()
