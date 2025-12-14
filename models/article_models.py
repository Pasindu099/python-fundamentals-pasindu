from typing import Optional
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import DeclarativeBase, relationship
from mongoengine import Document, EmbeddedDocument, fields


class SQLBase(DeclarativeBase):
    pass


class Author(SQLBase):
    __tablename__ = "authors"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    full_name: str = Column(String(100), nullable=False, unique=True)
    title: Optional[str] = Column(String(50))

    articles = relationship("ScientificArticle", back_populates="author")

    def __repr__(self) -> str:
        return f"<Author {self.full_name}, {self.title}>"


class ScientificArticle(SQLBase):
    __tablename__ = "scientific_articles"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    title: str = Column(String(255), nullable=False)
    summary: str = Column(Text, nullable=False)
    file_path: str = Column(String(255), nullable=False)
    arxiv_id: Optional[str] = Column(String(50), unique=True)
    created_at = Column(DateTime, server_default=func.now())

    author_id: int = Column(Integer, ForeignKey("authors.id"), nullable=False)
    author = relationship("Author", back_populates="articles")

    def __repr__(self) -> str:
        return f"<ScientificArticle {self.title}>"


class MongoAuthor(EmbeddedDocument):
    full_name = fields.StringField(required=True)
    title = fields.StringField()


class MongoScientificArticle(Document):
    meta = {
        "collection": "scientific_articles",
        "indexes": [
            {
                "fields": ["$text"],
                "default_language": "english",
            }
        ],
    }

    sql_id = fields.IntField(required=True, unique=True)
    title = fields.StringField(required=True)
    summary = fields.StringField(required=True)
    arxiv_id = fields.StringField()
    text = fields.StringField(required=True)
    author = fields.EmbeddedDocumentField(MongoAuthor)