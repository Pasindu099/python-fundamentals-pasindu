import os
from typing import List
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from mongoengine import QuerySet
from pathlib import Path
from pdfminer.high_level import extract_text_to_fp
from io import StringIO
from markdownify import markdownify as md

from models.article_models import (
    SQLBase,
    Author,
    ScientificArticle,
    MongoScientificArticle,
    MongoAuthor,
)
from storage.db_setup import get_sql_session, setup_mongodb_connection


def convert_pdf_to_markdown(pdf_path: str) -> str:
    """Extracts text from PDF and converts it to basic Markdown."""
    path = Path(pdf_path)
    if not path.exists():
        return "PDF content not available."

    output_string = StringIO()
    try:
        with open(path, "rb") as f:
            extract_text_to_fp(f, output_string)
        
        plain_text = output_string.getvalue()
        markdown_text = md(plain_text, heading_style="ATX", strong_em_symbol='*')

        return markdown_text.strip()
    except Exception:
        return "Error processing PDF."


def load_csv_to_mariadb(csv_path: str, sql_engine) -> None:
    """Loads data from articles.csv into MariaDB/SQLAlchemy."""
    if not Path(csv_path).exists():
        print(f"Error: CSV file not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)

    SQLBase.metadata.create_all(bind=sql_engine)

    with next(get_sql_session()) as session:
        try:
            for _, row in df.iterrows():
                author = session.query(Author).filter_by(full_name=str(row["author_full_name"])).first()
                if not author:
                    author = Author(
                        full_name=str(row["author_full_name"]), 
                        title=str(row["author_title"]) if pd.notna(row["author_title"]) else None
                    )
                    session.add(author)
                    session.flush()

                article_data = {
                    "title": str(row["title"]),
                    "summary": str(row["summary"]),
                    "file_path": str(row["file_path"]),
                    "arxiv_id": str(row["arxiv_id"]) if pd.notna(row["arxiv_id"]) else None,
                    "author_id": author.id,
                }
                
                existing_article = session.query(ScientificArticle).filter_by(
                    title=article_data["title"], author_id=author.id
                ).first()
                
                if not existing_article:
                    article = ScientificArticle(**article_data)
                    session.add(article)
            
            session.commit()
            print(f"MariaDB load complete. {len(df)} records processed.")
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error loading data to MariaDB: {e}")


def transfer_mariadb_to_mongodb() -> None:
    """
    Transfers data from MariaDB to MongoDB, converting PDF content to Markdown.
    """
    setup_mongodb_connection()
    project_root = Path(__file__).parent.parent
    
    with next(get_sql_session()) as session:
        sql_articles: List[ScientificArticle] = session.query(ScientificArticle).all()

        if not sql_articles:
            print("No articles found in MariaDB to transfer.")
            return

        for sql_article in sql_articles:
            
            if MongoScientificArticle.objects(sql_id=sql_article.id).first():
                continue

            pdf_full_path = project_root / sql_article.file_path.lstrip(os.sep).replace("/", os.sep)
            markdown_text = convert_pdf_to_markdown(str(pdf_full_path))

            mongo_author = MongoAuthor(
                full_name=sql_article.author.full_name,
                title=sql_article.author.title,
            )

            mongo_article = MongoScientificArticle(
                sql_id=sql_article.id,
                title=sql_article.title,
                summary=sql_article.summary,
                arxiv_id=sql_article.arxiv_id,
                text=markdown_text,
                author=mongo_author,
            )
            
            mongo_article.save()
            print(f"Transferred article ID {sql_article.id} to MongoDB.")

        print("Data transfer to MongoDB complete.")


def search_mongodb_articles(search_term: str) -> QuerySet:
    """
    Performs a full-text search on the MongoDB ScientificArticle collection.
    """
    setup_mongodb_connection()
    print(f"\n--- MongoDB Text Search for: '{search_term}' ---")
    
    results = MongoScientificArticle.objects.search_text(search_term)
    return results