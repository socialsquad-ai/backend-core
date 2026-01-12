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

# Build base DSN
base_dsn = f"postgresql://{SSQ_DB_USER}:{encoded_pass}@{SSQ_DB_HOST}:{SSQ_DB_PORT}/{SSQ_DB_NAME}"

# Heroku Postgres requires SSL and has limited connections (essential-0 = 20 max)
# Add connection pool limits to avoid "too many connections" error
# API + Worker each need: broker pool + result backend pool + listen connection
# With min=1, max=3 for each pool, we use ~6-8 connections per dyno = ~16 total
is_heroku = os.environ.get("DYNO") is not None
if is_heroku:
    # asyncpg pool parameters via DSN
    dsn = f"{base_dsn}?min_size=1&max_size=3"
else:
    dsn = base_dsn

# Create the broker instance
broker = PostgresqlBroker(
    dsn=dsn,
    result_backend=PostgresqlResultBackend(
        dsn=dsn,
    ),
)
