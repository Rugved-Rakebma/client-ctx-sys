from __future__ import annotations

import sqlite3
from typing import Optional

SCHEMA_VERSION = 1

SCHEMA_SQL = """
-- Ingestion tracking
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    path TEXT,
    original_source TEXT,
    ingested_at TEXT NOT NULL
);

-- Core entity storage
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL,
    slug TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_id INTEGER,
    created TEXT NOT NULL,
    updated TEXT NOT NULL,
    UNIQUE(type, slug),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

-- People
CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT,
    org TEXT,
    created TEXT NOT NULL,
    updated TEXT NOT NULL
);

-- Relationships between entities
CREATE TABLE IF NOT EXISTS relations (
    id INTEGER PRIMARY KEY,
    from_id INTEGER NOT NULL,
    relation TEXT NOT NULL,
    to_id INTEGER NOT NULL,
    FOREIGN KEY (from_id) REFERENCES entities(id) ON DELETE CASCADE,
    FOREIGN KEY (to_id) REFERENCES entities(id) ON DELETE CASCADE
);

-- Entity-to-person links
CREATE TABLE IF NOT EXISTS entity_people (
    entity_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    role TEXT,
    PRIMARY KEY (entity_id, person_id),
    FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE CASCADE
);

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY
);
"""

FTS_SQL = """
CREATE VIRTUAL TABLE IF NOT EXISTS entities_fts USING fts5(
    title, content,
    content=entities,
    content_rowid=id
);
"""

TRIGGERS_SQL = """
CREATE TRIGGER IF NOT EXISTS entities_ai AFTER INSERT ON entities BEGIN
    INSERT INTO entities_fts(rowid, title, content)
    VALUES (new.id, new.title, new.content);
END;

CREATE TRIGGER IF NOT EXISTS entities_au AFTER UPDATE ON entities BEGIN
    INSERT INTO entities_fts(entities_fts, rowid, title, content)
    VALUES('delete', old.id, old.title, old.content);
    INSERT INTO entities_fts(rowid, title, content)
    VALUES (new.id, new.title, new.content);
END;

CREATE TRIGGER IF NOT EXISTS entities_ad AFTER DELETE ON entities BEGIN
    INSERT INTO entities_fts(entities_fts, rowid, title, content)
    VALUES('delete', old.id, old.title, old.content);
END;
"""


def init_db(db_path: str) -> sqlite3.Connection:
    """Create tables if not exist, run migrations, return connection."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.row_factory = sqlite3.Row

    conn.executescript(SCHEMA_SQL)

    # FTS virtual table — separate because executescript can't mix DDL types
    try:
        conn.execute(FTS_SQL)
    except sqlite3.OperationalError:
        pass  # already exists

    conn.executescript(TRIGGERS_SQL)

    # Set schema version if not present
    row = conn.execute("SELECT MAX(version) FROM schema_version").fetchone()
    if row[0] is None:
        conn.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))

    conn.commit()
    return conn


def get_db(db_path: str) -> sqlite3.Connection:
    """Return a connection with foreign keys enabled and row_factory set."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.row_factory = sqlite3.Row
    return conn
