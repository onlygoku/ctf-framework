"""
Database - SQLite abstraction with connection pooling
"""

import sqlite3
import threading
from pathlib import Path
from typing import Any, List, Optional, Tuple


class Database:
    """
    Thread-safe SQLite wrapper with WAL mode for concurrent reads.
    """

    def __init__(self, db_path: str = "ctf.db"):
        self.db_path = str(Path(db_path))
        self._local = threading.local()
        self._setup()

    def _setup(self):
        conn = self._get_conn()
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.commit()

    def _get_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30,
            )
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        conn = self._get_conn()
        cursor = conn.execute(query, params)
        conn.commit()
        return cursor

    def executemany(self, query: str, params_list: List[Tuple]) -> sqlite3.Cursor:
        conn = self._get_conn()
        cursor = conn.executemany(query, params_list)
        conn.commit()
        return cursor

    def fetchone(self, query: str, params: Tuple = ()) -> Optional[tuple]:
        cursor = self._get_conn().execute(query, params)
        row = cursor.fetchone()
        return tuple(row) if row else None

    def fetchall(self, query: str, params: Tuple = ()) -> List[tuple]:
        cursor = self._get_conn().execute(query, params)
        return [tuple(row) for row in cursor.fetchall()]

    def close(self):
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None