
from sqlalchemy import (
    BigInteger,
    Boolean,
    Identity,
    Numeric,
    String,
    Text,
    TIMESTAMP,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(
        BigInteger, Identity(always=True), primary_key=True
    )
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    telegram_update_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    draft_reply: Mapped[str] = mapped_column(Text, nullable=False)
    reply_status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'pending'"))
    requires_human_review: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("TRUE")
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'new'")
    )
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("NOW()")
    )

    updated_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
        onupdate=text("NOW()"),
    )


class TicketStatusHistory(Base):
    __tablename__ = "ticket_status_history"

    id: Mapped[int] = mapped_column(
        BigInteger, Identity(always=True), primary_key=True
    )
    ticket_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True
    )
    old_status: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )
    new_status: Mapped[str] = mapped_column(
        String(20), nullable=False
    )
    changed_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )