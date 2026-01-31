-- Add platform_username to integrations table
ALTER TABLE integrations ADD COLUMN platform_username VARCHAR(255);
