import os
from pathlib import Path
import pandas as pd
from storage.db_setup import sql_engine
from usecases.data_pipeline import (
    fetch_arxiv_data,
    download_html_content,
    load_data_into_dbs,
    search_mongodb_articles,
    clear_mongo_collection, 
)
from models.article_models import MongoScientificArticle 

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"

DATA_DIR.mkdir(exist_ok=True)


def run_api_pipeline() -> None:
    print("=" * 50)
    
    ARXIV_QUERY = "quantum circuit learning"
    MAX_RESULTS = 3
    
    clear_mongo_collection(MongoScientificArticle) 

    print(f"1. Fetching {MAX_RESULTS} articles from ArXiv for query: '{ARXIV_QUERY}'...")
    df_arxiv = fetch_arxiv_data(ARXIV_QUERY, MAX_RESULTS)
    
    df_arxiv = df_arxiv.apply(download_html_content, axis=1)

    print("2. Loading DataFrame into MariaDB and MongoDB...")
    df_final = load_data_into_dbs(df_arxiv, sql_engine)
    
    print("-" * 50)
    
    SEARCH_TERM = "Open-vocabulary"
    search_results = search_mongodb_articles(SEARCH_TERM)
    
    print(f"3. Search Results for '{SEARCH_TERM}': {len(search_results)} documents found.")
    
    if search_results:
        for i, doc in enumerate(search_results):
            score = getattr(doc, 'score', 'N/A')

            print(f"Result {i+1} (Score: {score}):")
            print(f"Title: {doc.title}")
            print(f"Author: {doc.author.full_name}")
            print(f"Text snippet: {doc.text[:80]}...")
            
    print("=" * 50)


if __name__ == "__main__":
    run_api_pipeline()