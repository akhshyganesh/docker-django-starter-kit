-- Database initialization script
-- This script will be run when the PostgreSQL container starts

-- Create additional databases if needed
-- CREATE DATABASE saas_app_test;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Set timezone
SET timezone = 'UTC';
