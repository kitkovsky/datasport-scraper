import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db.models import Base

current_directory = os.path.dirname(os.path.abspath(__file__))
load_dotenv(f"{current_directory}/.env")

DB_URL = os.getenv("DB_URL")
DB_AUTH_TOKEN = os.getenv("DB_AUTH_TOKEN")
ENVIRONMENT = os.getenv("ENVIRONMENT")

db_url = f"sqlite+{DB_URL}/?authToken={DB_AUTH_TOKEN}"

engine = create_engine(
    db_url, connect_args={"check_same_thread": False}, echo=ENVIRONMENT == "development"
)
Base.metadata.create_all(bind=engine)

session = Session(engine)
