-- Run this in your Supabase SQL Editor

-- Table for tracking messages across the whole team
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    conversation_id TEXT DEFAULT 'default',
    sender TEXT NOT NULL, -- MORGAN, SCOUT, ALEX, etc.
    role TEXT NOT NULL, -- user or assistant
    content TEXT NOT NULL
);

-- Table for tracking campaigns
CREATE TABLE campaigns (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    name TEXT NOT NULL,
    status TEXT DEFAULT 'intake', -- intake, active, completed
    details JSONB DEFAULT '{}',
    seo_brief TEXT,
    post_calendar JSONB DEFAULT '[]'
);

-- Index for faster history retrieval
CREATE INDEX idx_conversation_history ON messages (conversation_id, created_at);
