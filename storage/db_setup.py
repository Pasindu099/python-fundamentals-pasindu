from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from mongoengine import connect, get_connection
from typing import Iterator

MARIADB_USER = "root"
MARIADB_PASSWORD = "root123"
MARIADB_HOST = "localhost"
MARIADB_PORT = 3306
MARIADB_NAME = "pipeline_db"

MARIADB_URL = f"mysql+pymysql://{MARIADB_USER}:{MARIADB_PASSWORD}@{MARIADB_HOST}:{MARIADB_PORT}/{MARIADB_NAME}"

sql_engine = create_engine(
    MARIADB_URL,
    echo=False,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)
SQLSessionLocal = sessionmaker(bind=sql_engine)


def get_sql_session() -> Iterator[Session]:
    """Provides a transactional scope around a series of operations."""
    session = SQLSessionLocal()
    try:
        yield session
    finally:
        session.close()


MONGO_HOST = "localhost"
MONGO_PORT = 27017
MONGO_DB_NAME = "scientific_papers"
MONGO_USERNAME = ""
MONGO_PASSWORD = ""

def setup_mongodb_connection() -> None:
    """Connects to MongoDB using MongoEngine."""
    connect(
        db=MONGO_DB_NAME,
        host=MONGO_HOST,
        port=MONGO_PORT,
        alias="default",
    )

def close_mongodb_connection() -> None:
    """Closes the MongoDB connection."""
    conn = get_connection("default")
    if conn:
        conn.close()