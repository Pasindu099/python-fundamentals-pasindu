# main.py

import os
from pathlib import Path
from storage.db_setup import sql_engine
from usecases.data_pipeline import (
    load_csv_to_mariadb,
    transfer_mariadb_to_mongodb,
    search_mongodb_articles,
)

# --- Configuration and Setup ---

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
PAPERS_DIR = PROJECT_ROOT / "papers"
CSV_FILE_PATH = DATA_DIR / "articles.csv"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
PAPERS_DIR.mkdir(exist_ok=True)


# Sample Data to fulfill the assignment requirements
# NOTE: You must replace the file paths and arxiv IDs with real data
SAMPLE_CSV_CONTENT = """title,summary,file_path,arxiv_id,author_full_name,author_title
Attention Is All You Need,The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...,papers/article_transformer.pdf,1706.03762,Ashish Vaswani,Researcher
Deep Residual Learning for Image Recognition,We present a residual learning framework to ease the training of networks that are substantially deeper than those previously used...,papers/article_resnet.pdf,1512.03385,Kaiming He,Staff Research Scientist
A Neural Probabilistic Language Model,We propose a neural network model for language, which attempts to overcome the limitations of the classic n-gram approach...,papers/article_nplm.pdf,cmp-lg/0007010,Yoshua Bengio,Professor
"""

# Create the CSV file
if not CSV_FILE_PATH.exists():
    with open(CSV_FILE_PATH, "w") as f:
        f.write(SAMPLE_CSV_CONTENT)
    print(f"Created sample CSV at: {CSV_FILE_PATH}")

# NOTE: For the PDF conversion to work, you must create the files
# papers/article_transformer.pdf, papers/article_resnet.pdf, and papers/article_nplm.pdf
# (even if they are empty or dummies for initial testing).
for filename in ["article_transformer.pdf", "article_resnet.pdf", "article_nplm.pdf"]:
    pdf_path = PAPERS_DIR / filename
    if not pdf_path.exists():
        with open(pdf_path, "w") as f:
            f.write("A dummy PDF file content.\n")
        print(f"Created dummy PDF at: {pdf_path}")


def run_pipeline() -> None:
    """Executes the complete data processing pipeline."""
    print("=" * 50)
    print("1. Loading CSV Data to MariaDB/SQLAlchemy...")
    load_csv_to_mariadb(str(CSV_FILE_PATH), sql_engine)
    print("-" * 50)

    print("2. Transferring Data from MariaDB to MongoDB (with PDF to Markdown conversion)...")
    transfer_mariadb_to_mongodb()
    print("-" * 50)

    # Example Search
    search_term = "recurrent neural networks"
    search_results = search_mongodb_articles(search_term)
    
    print(f"3. Search Results for '{search_term}': {len(search_results)} documents found.")
    
    if search_results:
        for i, doc in enumerate(search_results):
            # Print the text score and relevant fields
            score = doc.meta.get("score", "N/A")
            print(f"  Result {i+1} (Score: {score}):")
            print(f"    Title: {doc.title}")
            print(f"    Author: {doc.author.full_name}")
            print(f"    Summary: {doc.summary[:80]}...")
            print("-" * 20)
    
    print("=" * 50)
    print("Pipeline Complete.")


if __name__ == "__main__":
    run_pipeline()