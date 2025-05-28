CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE locations(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE records(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    location_id UUID REFERENCES locations(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    cleaned BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (user_id, location_id, date)
)