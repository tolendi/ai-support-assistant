import os

from app.models import Ticket
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured in .env")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def check_database_connection() -> bool:
    """Check whether the application can connect to PostgreSQL."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True


def save_ticket(ticket: Ticket) -> Ticket:
    """Save a ticket to PostgreSQL and return the saved record."""
    with SessionLocal() as session:
        session.add(ticket)
        session.commit()
        session.refresh(ticket)
        return ticket