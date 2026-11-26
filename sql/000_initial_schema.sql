BEGIN;

-- Main support tickets
CREATE TABLE IF NOT EXISTS tickets (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    message_id BIGINT NOT NULL,
    telegram_update_id BIGINT UNIQUE,
    user_id BIGINT NOT NULL,
    chat_id BIGINT,
    message_text TEXT NOT NULL,

    category VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    confidence NUMERIC(3, 2) NOT NULL,
    reason TEXT NOT NULL,

    draft_reply TEXT NOT NULL,
    reply_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    requires_human_review BOOLEAN NOT NULL DEFAULT TRUE,

    review_status VARCHAR(20) NOT NULL DEFAULT 'pending_review',
    approved_reply TEXT,
    reviewed_by BIGINT,
    reviewed_at TIMESTAMPTZ,

    approved_reply_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    approved_reply_sent_at TIMESTAMPTZ,

    status VARCHAR(20) NOT NULL DEFAULT 'new',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Ticket status change history
CREATE TABLE IF NOT EXISTS ticket_status_history (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ticket_id BIGINT NOT NULL REFERENCES tickets(id),
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_ticket_status_history_ticket_id
    ON ticket_status_history(ticket_id);

-- Notifications sent through n8n
CREATE TABLE IF NOT EXISTS ticket_notifications (
    id BIGSERIAL PRIMARY KEY,
    ticket_id BIGINT NOT NULL UNIQUE REFERENCES tickets(id),
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMIT;
