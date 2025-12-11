from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, func

metadata = MetaData()

users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(50), nullable=False),
    Column("email", String(100), nullable=False, unique=True),
    Column("age", Integer),
    Column("created_at", DateTime, server_default=func.now()),
)
