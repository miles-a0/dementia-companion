CREATE TABLE medications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    dose VARCHAR(200) NOT NULL,
    times_of_day TEXT[] NOT NULL,
    instructions TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE medication_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    medication_id INTEGER REFERENCES medications(id),
    scheduled_at TIMESTAMP NOT NULL,
    confirmed_at TIMESTAMP NULL,
    reminder_sent_at TIMESTAMP NULL
);