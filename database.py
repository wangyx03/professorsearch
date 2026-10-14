
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME", "professorsearch"),
    query={"charset": "utf8mb4"},
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

def test_connection():
    with engine.connect() as conn:
        database = conn.execute(
            text("SELECT DATABASE()")
        ).scalar_one()

        tables = conn.execute(
            text("SHOW TABLES")
        ).scalars().all()

        return database, tables


if __name__ == "__main__":
    database, tables = test_connection()

    print("Connected database:", database)
    print("Tables:")
    for table in tables:
        print(" -", table)
