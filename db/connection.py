import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db.models import Base

current_directory = os.path.dirname(os.path.abspath(__file__))
load_dotenv(f"{current_directory}/.env")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
ENVIRONMENT = os.getenv("ENVIRONMENT")
CLOUD_SQL_CONNECTION_NAME = os.getenv("CLOUD_SQL_CONNECTION_NAME")

db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}?host=/cloudsql/{CLOUD_SQL_CONNECTION_NAME}"

engine = create_engine(db_url, echo=ENVIRONMENT == "development")
Base.metadata.create_all(bind=engine)

session = Session(engine)
