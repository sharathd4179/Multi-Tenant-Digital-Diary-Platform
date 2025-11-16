-- Sample SQL script that could be used to initialise the PostgreSQL database.
-- In this project, SQLAlchemy’s metadata creates tables automatically on
-- application startup, so this script is provided for reference only.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Example table definitions (not used when SQLAlchemy is configured to autogenerate):
-- CREATE TABLE tenants (
--   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
--   name TEXT NOT NULL UNIQUE,
--   created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
-- );