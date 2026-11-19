ALTER TABLE tickets
    ADD COLUMN IF NOT EXISTS chat_id BIGINT,
    ADD COLUMN IF NOT EXISTS review_status VARCHAR(20)
        NOT NULL DEFAULT 'pending_review',
    ADD COLUMN IF NOT EXISTS approved_reply TEXT,
    ADD COLUMN IF NOT EXISTS reviewed_by BIGINT,
    ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS approved_reply_status VARCHAR(20)
        NOT NULL DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS approved_reply_sent_at TIMESTAMPTZ;