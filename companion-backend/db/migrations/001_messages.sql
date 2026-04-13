CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    message_type VARCHAR(50) NOT NULL DEFAULT 'general',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    read_at TIMESTAMP NULL,
    spoken_at TIMESTAMP NULL,
    CONSTRAINT chk_message_type CHECK (message_type IN ('greeting', 'reminder', 'intervention', 'check_in', 'medication', 'general'))
);

CREATE INDEX idx_messages_user_read ON messages (user_id, read_at);