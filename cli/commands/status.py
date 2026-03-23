from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import yaml

from cli.db.schema import get_db


@click.command("status")
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show the status of the current knowledge base."""
    kb_dir = Path(ctx.obj["kb_dir"])

    if not kb_dir.exists():
        click.echo(json.dumps({"error": ".knowledge-base/ directory not found"}, indent=2))
        sys.exit(1)

    # Read config for project name
    config_path = kb_dir / "config.yaml"
    project = ""
    if config_path.exists():
        with open(config_path) as f:
            cfg = yaml.safe_load(f) or {}
        project = cfg.get("project", "")

    db_path = kb_dir / "knowledge-base.db"
    if not db_path.exists():
        click.echo(json.dumps({"error": "Database not found. Run 'kb init' first."}, indent=2))
        sys.exit(1)

    conn = get_db(str(db_path))

    try:
        # Entity counts by type
        rows = conn.execute(
            "SELECT type, COUNT(*) as cnt FROM entities GROUP BY type ORDER BY type"
        ).fetchall()
        by_type = {}  # type: Dict[str, int]
        total_entities = 0
        for row in rows:
            by_type[row["type"]] = row["cnt"]
            total_entities += row["cnt"]

        # People count
        people_count = conn.execute("SELECT COUNT(*) FROM people").fetchone()[0]

        # Sources count
        sources_count = conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0]

        # Relations count
        relations_count = conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0]

        # Open action items with owners
        open_rows = conn.execute(
            """SELECT e.slug, e.title, e.created,
                      p.name AS owner
               FROM entities e
               LEFT JOIN entity_people ep ON ep.entity_id = e.id AND ep.role = 'owner'
               LEFT JOIN people p ON p.id = ep.person_id
               WHERE e.type = 'action-items' AND e.status = 'open'
               ORDER BY e.created ASC"""
        ).fetchall()
        open_items = [
            {"slug": r["slug"], "title": r["title"], "created": r["created"], "owner": r["owner"]}
            for r in open_rows
        ]  # type: List[Dict[str, Any]]

        # Untriaged action items (NULL status — pre-migration)
        untriaged_rows = conn.execute(
            """SELECT slug, title, created
               FROM entities
               WHERE type = 'action-items' AND status IS NULL
               ORDER BY created ASC"""
        ).fetchall()
        untriaged_items = [
            {"slug": r["slug"], "title": r["title"], "created": r["created"]}
            for r in untriaged_rows
        ]  # type: List[Dict[str, Any]]

        # Last source ingested
        last_source_row = conn.execute(
            "SELECT type, title, ingested_at FROM sources ORDER BY ingested_at DESC LIMIT 1"
        ).fetchone()
        last_source = None  # type: Optional[Dict[str, Any]]
        if last_source_row:
            last_source = {
                "type": last_source_row["type"],
                "title": last_source_row["title"],
                "ingested_at": last_source_row["ingested_at"],
            }

        # Recent activity
        recent_rows = conn.execute(
            "SELECT type, slug, title, updated FROM entities ORDER BY updated DESC LIMIT 5"
        ).fetchall()
        recent_activity = [
            {"type": r["type"], "slug": r["slug"], "title": r["title"], "updated": r["updated"]}
            for r in recent_rows
        ]  # type: List[Dict[str, Any]]

        # DB size
        db_size_kb = round(os.path.getsize(str(db_path)) / 1024, 1)

        click.echo(json.dumps({
            "project": project,
            "action_items": {
                "open": open_items,
                "open_count": len(open_items),
                "untriaged": untriaged_items,
                "untriaged_count": len(untriaged_items),
            },
            "last_source": last_source,
            "recent_activity": recent_activity,
            "entities": {
                "total": total_entities,
                "by_type": by_type,
            },
            "people": people_count,
            "sources": sources_count,
            "relations": relations_count,
            "db_size_kb": db_size_kb,
        }, indent=2))

    finally:
        conn.close()
