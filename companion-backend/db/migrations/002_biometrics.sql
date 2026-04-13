CREATE TABLE biometrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    heart_rate INTEGER NOT NULL,
    steps_last_hour INTEGER NOT NULL DEFAULT 0,
    recorded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    intervention_triggered BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT chk_heart_rate CHECK (heart_rate BETWEEN 30 AND 250),
    CONSTRAINT chk_steps CHECK (steps_last_hour >= 0)
);

CREATE INDEX idx_biometrics_user_recorded ON biometrics (user_id, recorded_at DESC);