-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Log the initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialized at %', NOW();
END $$;