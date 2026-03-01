"""
Database - SQLite for local, PostgreSQL for production
"""

import os
import threading
from typing import List, Optional, Tuple


def get_db():
    db_url = os.getenv("DATABASE_URL", "")
    if db_url and db_url.startswith("postgresql"):
        return PostgresDatabase(db_url)
    return SQLiteDatabase(os.getenv("CTF_DB_PATH", "ctf.db"))


class SQLiteDatabase:
    def __init__(self, db_path: str = "ctf.db"):
        import sqlite3
        self.db_path = db_path
        self._local = threading.local()
        self._setup()

    def _setup(self):
        conn = self._get_conn()
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.commit()

    def _get_conn(self):
        import sqlite3
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = __import__('sqlite3').connect(
                self.db_path, check_same_thread=False, timeout=30
            )
            self._local.conn.row_factory = __import__('sqlite3').Row
        return self._local.conn

    def execute(self, query: str, params: Tuple = ()):
        query = self._fix_query(query)
        conn = self._get_conn()
        cursor = conn.execute(query, params)
        conn.commit()
        return cursor

    def fetchone(self, query: str, params: Tuple = ()) -> Optional[tuple]:
        query = self._fix_query(query)
        row = self._get_conn().execute(query, params).fetchone()
        return tuple(row) if row else None

    def fetchall(self, query: str, params: Tuple = ()) -> List[tuple]:
        query = self._fix_query(query)
        return [tuple(r) for r in self._get_conn().execute(query, params).fetchall()]

    def executemany(self, query: str, params_list):
        query = self._fix_query(query)
        conn = self._get_conn()
        cursor = conn.executemany(query, params_list)
        conn.commit()
        return cursor

    def _fix_query(self, query: str) -> str:
        return query

    def close(self):
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None


class PostgresDatabase:
    def __init__(self, db_url: str):
        import psycopg2
        import psycopg2.extras
        # Render uses postgres:// but psycopg2 needs postgresql://
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        self.db_url = db_url
        self._local = threading.local()

    def _get_conn(self):
        import psycopg2
        import psycopg2.extras
        if not hasattr(self._local, "conn") or self._local.conn is None or self._local.conn.closed:
            self._local.conn = psycopg2.connect(self.db_url)
            self._local.conn.autocommit = False
        return self._local.conn

    def execute(self, query: str, params: Tuple = ()):
        query = self._fix_query(query)
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            return cur
        except Exception as e:
            conn.rollback()
            raise e

    def fetchone(self, query: str, params: Tuple = ()) -> Optional[tuple]:
        query = self._fix_query(query)
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            row = cur.fetchone()
            return tuple(row) if row else None
        except Exception as e:
            conn.rollback()
            raise e

    def fetchall(self, query: str, params: Tuple = ()) -> List[tuple]:
        query = self._fix_query(query)
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.execute(query, params)
            conn.commit()
            return [tuple(r) for r in cur.fetchall()]
        except Exception as e:
            conn.rollback()
            raise e

    def executemany(self, query: str, params_list):
        query = self._fix_query(query)
        conn = self._get_conn()
        try:
            cur = conn.cursor()
            cur.executemany(query, params_list)
            conn.commit()
            return cur
        except Exception as e:
            conn.rollback()
            raise e

    def _fix_query(self, query: str) -> str:
        # Convert SQLite syntax to PostgreSQL
        query = query.replace("?", "%s")
        query = query.replace("INTEGER PRIMARY KEY AUTOINCREMENT",
                              "SERIAL PRIMARY KEY")
        query = query.replace("strftime('%s', 'now')", 
                              "EXTRACT(EPOCH FROM NOW())")
        query = query.replace("INSERT OR REPLACE",
                              "INSERT")
        query = query.replace("INSERT OR IGNORE",
                              "INSERT")
        return query

    def close(self):
        if hasattr(self._local, "conn") and self._local.conn:
            self._local.conn.close()
            self._local.conn = None


# Default database class for backward compatibility
class Database(SQLiteDatabase):
    def __new__(cls, db_path: str = "ctf.db"):
        db_url = os.getenv("DATABASE_URL", "")
        if db_url and (db_url.startswith("postgresql://") or db_url.startswith("postgres://")):
            instance = object.__new__(PostgresDatabase)
            instance.__init__(db_url)
            return instance
        instance = object.__new__(SQLiteDatabase)
        instance.__init__(db_path)
        return instance
        