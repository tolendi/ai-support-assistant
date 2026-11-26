BEGIN;

ALTER TABLE tickets
    ADD COLUMN IF NOT EXISTS knowledge_article_ids JSONB
        NOT NULL DEFAULT '[]'::JSONB,
    ADD COLUMN IF NOT EXISTS missing_information JSONB
        NOT NULL DEFAULT '[]'::JSONB;

COMMIT;