from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict

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

        # DB size
        db_size_kb = round(os.path.getsize(str(db_path)) / 1024, 1)

        click.echo(json.dumps({
            "project": project,
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
