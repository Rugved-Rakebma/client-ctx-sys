from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from cli.db.schema import get_db


@click.command("get")
@click.argument("path", required=False, default=None)
@click.option("--id", "entity_id", default=None, type=int, help="Get entity by database ID.")
@click.pass_context
def get(ctx: click.Context, path: Optional[str], entity_id: Optional[int]) -> None:
    """Get a specific entity by type/slug or --id."""
    kb_dir = Path(ctx.obj["kb_dir"])

    if not kb_dir.exists():
        click.echo(json.dumps({"error": ".knowledge-base/ directory not found"}, indent=2))
        sys.exit(1)

    if not path and entity_id is None:
        click.echo(json.dumps({"error": "Provide type/slug or --id"}, indent=2))
        sys.exit(1)

    db_path = str(kb_dir / "knowledge-base.db")
    conn = get_db(db_path)

    try:
        # Fetch entity
        if entity_id is not None:
            row = conn.execute(
                "SELECT id, type, slug, title, content, source_id, created, updated FROM entities WHERE id = ?",
                (entity_id,),
            ).fetchone()
        else:
            # path is type/slug
            parts = path.split("/", 1)
            if len(parts) != 2:
                click.echo(json.dumps({"error": "Invalid format. Use type/slug or --id"}, indent=2))
                sys.exit(1)
            etype, slug = parts
            row = conn.execute(
                "SELECT id, type, slug, title, content, source_id, created, updated FROM entities WHERE type = ? AND slug = ?",
                (etype, slug),
            ).fetchone()

        if not row:
            click.echo(json.dumps({"error": "Entity not found"}, indent=2))
            sys.exit(1)

        result = {
            "id": row["id"],
            "type": row["type"],
            "slug": row["slug"],
            "title": row["title"],
            "content": row["content"],
            "created": row["created"],
            "updated": row["updated"],
        }  # type: Dict[str, Any]

        # Join source
        if row["source_id"]:
            source = conn.execute(
                "SELECT id, type, title, path FROM sources WHERE id = ?",
                (row["source_id"],),
            ).fetchone()
            if source:
                result["source"] = {
                    "id": source["id"],
                    "type": source["type"],
                    "title": source["title"],
                    "path": source["path"],
                }

        # Join people via entity_people
        people_rows = conn.execute(
            """SELECT p.slug, p.name, ep.role
               FROM entity_people ep
               JOIN people p ON p.id = ep.person_id
               WHERE ep.entity_id = ?""",
            (row["id"],),
        ).fetchall()
        if people_rows:
            result["people"] = [
                {"slug": p["slug"], "name": p["name"], "role": p["role"]}
                for p in people_rows
            ]

        # Join relations (outgoing)
        rel_rows = conn.execute(
            """SELECT r.relation, e.type, e.slug, e.title
               FROM relations r
               JOIN entities e ON e.id = r.to_id
               WHERE r.from_id = ?""",
            (row["id"],),
        ).fetchall()
        if rel_rows:
            result["related"] = [
                {
                    "relation": r["relation"],
                    "entity": "{}/{}".format(r["type"], r["slug"]),
                    "title": r["title"],
                }
                for r in rel_rows
            ]

        click.echo(json.dumps(result, indent=2))

    finally:
        conn.close()
