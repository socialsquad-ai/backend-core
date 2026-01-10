"""
Broker configuration for TaskIQ.
This module is used to avoid circular imports.
"""

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

# Create the broker instance
broker = PostgresqlBroker(
    dsn=f"postgresql://{SSQ_DB_USER}:{encoded_pass}@{SSQ_DB_HOST}:{SSQ_DB_PORT}/{SSQ_DB_NAME}",
    result_backend=PostgresqlResultBackend(
        dsn=f"postgresql://{SSQ_DB_USER}:{encoded_pass}@{SSQ_DB_HOST}:{SSQ_DB_PORT}/{SSQ_DB_NAME}",
    ),
)
