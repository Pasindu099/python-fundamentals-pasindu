from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

DB_USER = "app_user"
DB_PASSWORD = "app_password"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "python_db"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    echo=True,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)
