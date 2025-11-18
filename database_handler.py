from __future__ import annotations
import os
import re
import sqlite3
from typing import Any, Dict, List, Optional

"""
/c:/Coding/briefkasten/database_handler.py

Simple SQLite database handler with:
- create_table(table_name)
- get_table_content(table_name) -> list[dict]

Creates the database file next to this module by default.
"""



_VALID_NAME = re.compile(r"^[A-Za-z0-9_]+$")


class DatabaseHandler:
    """
    Lightweight SQLite handler.

    Default schema created by create_table:
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      data TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "briefkasten.db")
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.row_factory = sqlite3.Row

        self.create_user_table()

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            self.conn = None  # type: ignore

    def __enter__(self) -> "DatabaseHandler":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _validate_table_name(self, name: str) -> None:
        if not name or not _VALID_NAME.match(name):
            raise ValueError("Invalid table name. Use letters, numbers, and underscores only.")

    def create_table(self, table_name: str) -> None:
        """
        Create a table with a simple schema if it does not exist.
        table_name: only letters, numbers and underscores are allowed.
        """
        self._validate_table_name(table_name)
        sql = f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    def _table_exists(self, table_name: str) -> bool:
        self._validate_table_name(table_name)
        cur = self.conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        return cur.fetchone() is not None

    def get_table_content(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Return all rows from the named table as a list of dicts.
        Raises ValueError if the table does not exist.
        """
        if not self._table_exists(table_name):
            raise ValueError(f"Table '{table_name}' does not exist")

        cur = self.conn.cursor()
        cur.execute(f'SELECT * FROM "{table_name}"')
        rows = cur.fetchall()
        return [dict(row) for row in rows]

    def create_user_table(self) -> None:
        """
        Create a 'users' table with id, username, email, created_at.
        """

        print("Creating users table")

        sql = """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            mac TEXT NOT NULL,
            ser TEXT NOT NULL
        )
        """
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    def create_letter_table(self, serial_number: str) -> None:
        """
        Create a table for letters with id, serial_number, content, created_at.
        """

        print("Creating letter table for serial number:", serial_number)

        sql = f"""
        CREATE TABLE IF NOT EXISTS {serial_number} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT
        )
        """
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

        # validate the serial number and insert a test row with the current timestamp
        self._validate_table_name(serial_number)
        cur.execute(f'INSERT INTO "{serial_number}" (time) VALUES (CURRENT_TIMESTAMP)')
        self.conn.commit()

    def getSerialNumberByMAC(self, mac_address: str) -> Optional[str]:
        """
        Retrieve the serial number associated with the given MAC address.
        Returns None if not found.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT ser FROM users WHERE mac = ?", (mac_address,))
        row = cur.fetchone()
        if row:
            return row["ser"]
        return None
    
    def getLetters(self, serial_number: str) -> List[Dict[str, Any]]:
        """
        Retrieve all letters associated with the given serial number.
        Returns a list of letters.
        """
        if not self._table_exists(serial_number):
            return []
        
        cur = self.conn.cursor()
        cur.execute(f'SELECT * FROM "{serial_number}"')
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    
    def addUser(self, mac: str, ser: str) -> None:
        """
        Add a user with the given MAC address and serial number.
        """
        cur = self.conn.cursor()
        cur.execute("INSERT INTO users (mac, ser) VALUES (?, ?)", (mac, ser))
        self.conn.commit()

    def addLetter(self, serial_number: str, time: str) -> None:
        """
        Add a letter entry to the table associated with the given serial number.
        """
        self._validate_table_name(serial_number)
        cur = self.conn.cursor()
        cur.execute(f'INSERT INTO "{serial_number}" (time) VALUES (?)', (time,))
        self.conn.commit()

# Example usage (for quick manual testing; remove when used as a module):
if __name__ == "__main__":
    db = DatabaseHandler()
    try:
        db.create_user_table("00:11:22:33:44:55", "SN123456")
        db.create_letter_table("SN123456")
    finally:
        db.close()