import os

from app.models import Ticket, TicketStatusHistory
from app.services.status_manager import is_status_transition_allowed
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

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


def get_ticket_by_id(ticket_id: int):
    with SessionLocal() as session:
        return session.get(Ticket, ticket_id)


def update_ticket_status(ticket_id: int, status: str):
    with SessionLocal() as session:
        ticket = session.get(Ticket, ticket_id)

        if ticket is None:
            return None

        old_status = ticket.status

        if not is_status_transition_allowed(old_status, status):
            raise ValueError(
                f"Status transition from '{old_status}' to '{status}' is not allowed"
            )

        ticket.status = status

        history_entry = TicketStatusHistory(
            ticket_id=ticket.id,
            old_status=old_status,
            new_status=status,
        )

        session.add(history_entry)

        session.commit()
        session.refresh(ticket)

        return ticket

def update_reply_status(ticket_id: int, reply_status: str):
    with SessionLocal() as session:
        ticket = session.get(Ticket, ticket_id)

        if ticket is None:
            return None

        ticket.reply_status = reply_status

        session.commit()
        session.refresh(ticket)

        return ticket


def get_tickets(
    category=None,
    priority=None,
    status=None,
    limit=50,
    offset=0,
):
    with SessionLocal() as session:
        query = session.query(Ticket)

        if category:
            query = query.filter(Ticket.category == category)

        if priority:
            query = query.filter(Ticket.priority == priority)

        if status:
            query = query.filter(Ticket.status == status)

        return (
            query
            .order_by(Ticket.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )


def get_ticket_status_history(ticket_id: int):
    with SessionLocal() as session:
        ticket = session.get(Ticket, ticket_id)

        if ticket is None:
            return None

        return (
            session.query(TicketStatusHistory)
            .filter(TicketStatusHistory.ticket_id == ticket_id)
            .order_by(TicketStatusHistory.changed_at.asc())
            .all()
        )