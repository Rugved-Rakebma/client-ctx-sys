from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from cli.db.schema import get_db


@click.command("list")
@click.option("--type", "entity_type", default=None, help="Filter by entity type.")
@click.option("--source-id", default=None, type=int, help="Filter by source ID.")
@click.option("--limit", default=50, type=int, help="Max results to return.")
@click.option("--offset", default=0, type=int, help="Offset for pagination.")
@click.pass_context
def list_cmd(
    ctx: click.Context,
    entity_type: Optional[str],
    source_id: Optional[int],
    limit: int,
    offset: int,
) -> None:
    """List entities in the knowledge base."""
    kb_dir = Path(ctx.obj["kb_dir"])

    if not kb_dir.exists():
        click.echo(json.dumps({"error": ".knowledge-base/ directory not found"}, indent=2))
        sys.exit(1)

    db_path = str(kb_dir / "knowledge-base.db")
    conn = get_db(db_path)

    try:
        # Build query
        where_clauses = []  # type: List[str]
        params = []  # type: List[Any]

        if entity_type:
            where_clauses.append("type = ?")
            params.append(entity_type)
        if source_id is not None:
            where_clauses.append("source_id = ?")
            params.append(source_id)

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        # Get total count
        count_sql = "SELECT COUNT(*) FROM entities {}".format(where_sql)
        total = conn.execute(count_sql, params).fetchone()[0]

        # Get paginated results
        query_sql = "SELECT id, type, slug, title, updated FROM entities {} ORDER BY updated DESC LIMIT ? OFFSET ?".format(where_sql)
        rows = conn.execute(query_sql, params + [limit, offset]).fetchall()

        entities = [
            {
                "id": row["id"],
                "type": row["type"],
                "slug": row["slug"],
                "title": row["title"],
                "updated": row["updated"],
            }
            for row in rows
        ]

        click.echo(json.dumps({
            "entities": entities,
            "total": total,
            "limit": limit,
            "offset": offset,
        }, indent=2))

    finally:
        conn.close()
