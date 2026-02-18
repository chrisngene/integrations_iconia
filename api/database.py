from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from urllib.parse import quote as urlquote
from sqlalchemy.orm import sessionmaker
from dotenv import dotenv_values

config = dotenv_values(".env")

# DB Connection for Matatu Sacco
dbhost = config.get("DBHOST")
dbuser = config.get("DBUSER")
dbpass = config.get("DBPASS")
dbname = config.get("DBNAME")

dburl = f"postgresql+psycopg2://{dbuser}:%s@{dbhost}:5432/{dbname}"
engine = create_engine(dburl % urlquote(f"{dbpass}"))

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
