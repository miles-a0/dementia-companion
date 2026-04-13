CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP NULL,
    transcript JSONB NOT NULL DEFAULT '[]',
    summary TEXT NULL,
    trigger_type VARCHAR(50) NULL,
    CONSTRAINT chk_trigger_type CHECK (trigger_type IN ('manual', 'biometric', 'scheduled'))
);

CREATE TABLE intervention_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    triggered_at TIMESTAMP NOT NULL DEFAULT NOW(),
    trigger_type VARCHAR(50) NOT NULL,
    message_sent TEXT NOT NULL,
    conversation_id INTEGER REFERENCES conversations(id) NULL,
    duration_seconds INTEGER NULL
);

CREATE INDEX idx_conversations_user_ended ON conversations (user_id, ended_at);
CREATE INDEX idx_intervention_log_user_triggered ON intervention_log (user_id, triggered_at DESC);