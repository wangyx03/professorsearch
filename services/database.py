
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from config import Config


DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=Config.DB_USER,
    password=Config.DB_PASSWORD,
    host=Config.DB_HOST,
    port=Config.DB_PORT,
    database=Config.DB_NAME,
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
