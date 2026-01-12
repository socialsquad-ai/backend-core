"""
Broker configuration for TaskIQ.
This module is used to avoid circular imports.
"""

import os
from urllib.parse import quote

from taskiq_postgresql import PostgresqlBroker, PostgresqlResultBackend

from config.env import (
    SSQ_DB_HOST,
    SSQ_DB_NAME,
    SSQ_DB_PASSWORD,
    SSQ_DB_PORT,
    SSQ_DB_USER,
)

# URL-encode the password to handle special characters
encoded_pass = quote(SSQ_DB_PASSWORD)

# Heroku Postgres requires SSL and has limited connections (essential-0 = 20 max)
# API + Worker each need: broker pool + result backend pool + listen connection
# With min=1, max=2 for each pool, we use ~4-6 connections per dyno = ~12 total
is_heroku = os.environ.get("DYNO") is not None

# Build DSN - add sslmode=require for Heroku
if is_heroku:
    dsn = f"postgresql://{SSQ_DB_USER}:{encoded_pass}@{SSQ_DB_HOST}:{SSQ_DB_PORT}/{SSQ_DB_NAME}?sslmode=require"
else:
    dsn = f"postgresql://{SSQ_DB_USER}:{encoded_pass}@{SSQ_DB_HOST}:{SSQ_DB_PORT}/{SSQ_DB_NAME}"

# Pool settings passed via pool_kwargs (asyncpg pool parameters)
# These are NOT DSN parameters - they go to asyncpg.create_pool()
pool_kwargs = {"min_size": 1, "max_size": 2} if is_heroku else {"min_size": 2, "max_size": 4}

# Create the broker instance
broker = PostgresqlBroker(
    dsn=dsn,
    pool_kwargs=pool_kwargs,
    result_backend=PostgresqlResultBackend(
        dsn=dsn,
        pool_kwargs=pool_kwargs,
    ),
)
