-- Database Initialization Schema for Stephen Hawking Digital Twin
-- Target Database Engine: PostgreSQL

-- Drop table if it exists to allow clean environment resets
DROP TABLE IF EXISTS user_memories;

-- Foundational table to store long-term context extracted by the LLM
CREATE TABLE user_memories (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    memory_text TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);