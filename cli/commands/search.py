from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from cli.db.schema import get_db


@click.command("search")
@click.argument("query")
@click.option("--type", "entity_type", default=None, help="Filter by entity type.")
@click.option("--limit", default=10, type=int, help="Max results to return.")
@click.pass_context
def search(ctx: click.Context, query: str, entity_type: Optional[str], limit: int) -> None:
    """Search the knowledge base using full-text search."""
    kb_dir = Path(ctx.obj["kb_dir"])

    if not kb_dir.exists():
        click.echo(json.dumps({"error": ".knowledge-base/ directory not found"}, indent=2))
        sys.exit(1)

    db_path = str(kb_dir / "knowledge-base.db")
    conn = get_db(db_path)

    results = []  # type: List[Dict[str, Any]]

    try:
        # Try FTS5 search first — add prefix wildcards for partial matching
        fts_query = " ".join("{}*".format(w) for w in query.split() if w)
        fts_sql = """
            SELECT e.id, e.type, e.slug, e.title, e.content, entities_fts.rank
            FROM entities_fts
            JOIN entities e ON e.id = entities_fts.rowid
            WHERE entities_fts MATCH ?
            ORDER BY entities_fts.rank
            LIMIT ?
        """
        fts_rows = conn.execute(fts_sql, (fts_query, limit * 3)).fetchall()

        for row in fts_rows:
            if entity_type and row["type"] != entity_type:
                continue

            snippet = (row["content"] or "")[:300]
            results.append({
                "id": row["id"],
                "type": row["type"],
                "slug": row["slug"],
                "title": row["title"],
                "score": round(abs(row["rank"]), 4) if row["rank"] else 0.0,
                "snippet": snippet,
            })

            if len(results) >= limit:
                break

    except Exception:
        # FTS query syntax can fail on edge cases — fall back to LIKE
        pass

    # Fallback: LIKE search if FTS returned nothing
    if not results:
        seen_ids = []  # type: List[int]
        words = query.split()
        for word in words:
            like_sql = """
                SELECT id, type, slug, title, content
                FROM entities
                WHERE title LIKE ? OR content LIKE ?
                LIMIT ?
            """
            pattern = "%{}%".format(word)
            rows = conn.execute(like_sql, (pattern, pattern, limit * 2)).fetchall()

            for row in rows:
                if row["id"] in seen_ids:
                    continue
                if entity_type and row["type"] != entity_type:
                    continue

                seen_ids.append(row["id"])
                snippet = (row["content"] or "")[:300]
                results.append({
                    "id": row["id"],
                    "type": row["type"],
                    "slug": row["slug"],
                    "title": row["title"],
                    "score": 0.0,
                    "snippet": snippet,
                })

                if len(results) >= limit:
                    break

            if len(results) >= limit:
                break

    conn.close()

    click.echo(json.dumps({
        "query": query,
        "results": results,
        "total_results": len(results),
    }, indent=2))
