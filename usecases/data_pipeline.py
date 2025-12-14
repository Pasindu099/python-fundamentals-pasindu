import os
from typing import List, Optional, Tuple, Any, Dict
import pandas as pd
import requests
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from mongoengine.queryset import QuerySet
from pathlib import Path
import xml.etree.ElementTree as ET
import html2text
import time

from models.article_models import (
    SQLBase,
    Author,
    ScientificArticle,
    MongoScientificArticle,
    MongoAuthor,
)
from storage.db_setup import get_sql_session, setup_mongodb_connection


def extract_text_from_html(html_content: str) -> str:
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    return h.handle(html_content).strip()


def save_article_to_mariadb(row: pd.Series, session: Session) -> pd.Series:
    try:
        author_full_name = row["author_full_name"]
        author_title = row["author_title"]
        
        author = session.query(Author).filter_by(full_name=author_full_name).first()
        if not author:
            author = Author(full_name=author_full_name, title=author_title)
            session.add(author)
            session.flush()

        article_data = {
            "title": row["title"],
            "summary": row["summary"],
            "file_path": row["file_path"],
            "arxiv_id": row["arxiv_id"],
            "author_id": author.id,
        }
        
        existing_article = session.query(ScientificArticle).filter_by(
            arxiv_id=article_data["arxiv_id"]
        ).first()

        if not existing_article:
            article = ScientificArticle(**article_data)
            session.add(article)
            session.flush()
            
            row["sql_article_id"] = article.id
            row["sql_author_id"] = author.id
        else:
            row["sql_article_id"] = existing_article.id
            row["sql_author_id"] = existing_article.author_id
            
    except SQLAlchemyError as e:
        session.rollback()
        row["sql_article_id"] = -1
        row["sql_author_id"] = -1
    
    return row


def save_article_to_mongodb(row: pd.Series) -> None:
    if row["sql_article_id"] == -1:
        return

    try:
        mongo_author = MongoAuthor(
            full_name=row["author_full_name"],
            title=row["author_title"],
        )

        mongo_article = MongoScientificArticle(
            sql_id=int(row["sql_article_id"]),
            title=row["title"],
            summary=row["summary"],
            arxiv_id=row["arxiv_id"],
            text=extract_text_from_html(row["html_content"]), 
            author=mongo_author,
        )
        
        if not MongoScientificArticle.objects(sql_id=mongo_article.sql_id).first():
            mongo_article.save()
        
    except Exception as e:
        pass


def load_csv_to_dataframe(csv_path: str) -> pd.DataFrame:
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"The file at {csv_path} does not exist.")

    df_temp = pd.read_csv(csv_path, nrows=1)
    string_dtypes = {col: 'string' for col in df_temp.columns}
    
    df = pd.read_csv(csv_path, dtype=string_dtypes)
    return df


def fetch_arxiv_data(query: str, max_results: int = 5) -> pd.DataFrame:
    ARXIV_URL = "http://export.arxiv.org/api/query?"
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    
    response = requests.get(ARXIV_URL, params=params)
    response.raise_for_status()
    
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(response.content)
    
    articles_data: List[Dict[str, Any]] = []

    for entry in root.findall("atom:entry", ns):
        
        author_element = entry.find("atom:author", ns)
        author_name = author_element.find("atom:name", ns).text if author_element and author_element.find("atom:name", ns) is not None else "Unknown Author"
        
        title = entry.find("atom:title", ns).text.strip() if entry.find("atom:title", ns) is not None else ""
        summary = entry.find("atom:summary", ns).text.strip() if entry.find("atom:summary", ns) is not None else ""
        
        arxiv_id_full = entry.find("atom:id", ns).text
        arxiv_id = arxiv_id_full.split('/')[-1] if arxiv_id_full else ""
        
        article_row = {
            "title": title,
            "summary": summary,
            "file_path": f"arxiv_pdf/{arxiv_id}.pdf",
            "arxiv_id": arxiv_id,
            "author_full_name": author_name,
            "author_title": "ArXiv Contributor",
            "html_content": "",
        }
        articles_data.append(article_row)

    df = pd.DataFrame(articles_data).astype('string')
    return df


def download_html_content(row: pd.Series) -> pd.Series:
    arxiv_id = row["arxiv_id"]
    if not arxiv_id:
        row["html_content"] = "<html><body>No ArXiv ID</body></html>"
        return row
    
    html_url = f"https://arxiv.org/abs/{arxiv_id}"
    
    try:
        time.sleep(0.5) 
        response = requests.get(html_url, timeout=10)
        response.raise_for_status() 
        
        row["html_content"] = response.text
    except Exception as e:
        row["html_content"] = f"<html><body>Error fetching content: {e}</body></html>"
        
    return row


def load_data_into_dbs(df: pd.DataFrame, sql_engine) -> pd.DataFrame:
    
    df["sql_article_id"] = pd.NA
    df["sql_author_id"] = pd.NA
    
    SQLBase.metadata.create_all(bind=sql_engine)

    with next(get_sql_session()) as session:
        df = df.apply(lambda row: save_article_to_mariadb(row, session), axis=1)
        session.commit()
        
    setup_mongodb_connection()
    df.apply(save_article_to_mongodb, axis=1)
    
    return df


def clear_mongo_collection(collection_class: type[MongoScientificArticle]) -> None:
    setup_mongodb_connection()
    collection_class.objects.delete()


def search_newly_ingested_data(query: str) -> QuerySet:
    setup_mongodb_connection()
    return search_mongodb_articles(query)

def search_mongodb_articles(search_term: str) -> QuerySet:
    setup_mongodb_connection()
    results = MongoScientificArticle.objects.search_text(search_term)
    return results