from __future__ import annotations

import os
from pathlib import Path

from psycopg import Connection, connect
from psycopg.rows import dict_row


DEFAULT_DATABASE_URL = "postgresql://cfhee:cfhee@localhost:5432/cfhee"


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def get_connection() -> Connection:
    return connect(get_database_url(), row_factory=dict_row)


def initialize_database() -> None:
    schema_path = Path(__file__).resolve().parents[3] / "sql" / "schema.sql"

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(schema_path.read_text(encoding="utf-8"))
