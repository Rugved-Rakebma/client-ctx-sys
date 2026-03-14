from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from cli.db.schema import get_db


@click.command("add")
@click.argument("json_input")
@click.pass_context
def add(ctx: click.Context, json_input: str) -> None:
    """Insert or update entities and people in the database.

    Accepts a JSON string or a path to a JSON file.
    """
    kb_dir = Path(ctx.obj["kb_dir"])

    if not kb_dir.exists():
        click.echo(json.dumps({"error": ".knowledge-base/ directory not found"}, indent=2))
        sys.exit(1)

    db_path = str(kb_dir / "knowledge-base.db")

    # Parse input — either a file path or inline JSON
    json_path = Path(json_input)
    if json_path.exists() and json_path.is_file():
        try:
            data = json.loads(json_path.read_text())
        except json.JSONDecodeError as e:
            click.echo(json.dumps({"error": "Invalid JSON in file: {}".format(str(e))}, indent=2))
            sys.exit(1)
    else:
        try:
            data = json.loads(json_input)
        except json.JSONDecodeError as e:
            click.echo(json.dumps({"error": "Invalid JSON: {}".format(str(e))}, indent=2))
            sys.exit(1)

    now = datetime.datetime.utcnow().isoformat(timespec="seconds")
    today = datetime.date.today().isoformat()

    conn = get_db(db_path)

    try:
        source_id = None  # type: Optional[int]
        entity_results = []  # type: List[Dict[str, Any]]
        people_results = []  # type: List[Dict[str, Any]]
        relations_added = 0
        entity_people_added = 0

        # --- Source ---
        source_data = data.get("source")
        if source_data:
            cur = conn.execute(
                "INSERT INTO sources (type, title, path, original_source, ingested_at) VALUES (?, ?, ?, ?, ?)",
                (
                    source_data.get("type", ""),
                    source_data.get("title", ""),
                    source_data.get("path"),
                    source_data.get("original_source"),
                    now,
                ),
            )
            source_id = cur.lastrowid

        # --- Entities ---
        entities = data.get("entities", [])
        for entity in entities:
            etype = entity["type"]
            slug = entity["slug"]
            title = entity["title"]
            content = entity.get("content", "")

            # Try insert, on conflict update
            existing = conn.execute(
                "SELECT id FROM entities WHERE type = ? AND slug = ?",
                (etype, slug),
            ).fetchone()

            if existing:
                entity_id = existing["id"]
                conn.execute(
                    "UPDATE entities SET title = ?, content = ?, source_id = COALESCE(?, source_id), updated = ? WHERE id = ?",
                    (title, content, source_id, today, entity_id),
                )
                entity_results.append({"type": etype, "slug": slug, "action": "updated", "id": entity_id})
            else:
                cur = conn.execute(
                    "INSERT INTO entities (type, slug, title, content, source_id, created, updated) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (etype, slug, title, content, source_id, today, today),
                )
                entity_id = cur.lastrowid
                entity_results.append({"type": etype, "slug": slug, "action": "created", "id": entity_id})

        # --- People ---
        people = data.get("people", [])
        for person in people:
            slug = person["slug"]
            name = person["name"]
            role = person.get("role")
            org = person.get("org")

            existing = conn.execute(
                "SELECT id FROM people WHERE slug = ?",
                (slug,),
            ).fetchone()

            if existing:
                person_id = existing["id"]
                conn.execute(
                    "UPDATE people SET name = ?, role = COALESCE(?, role), org = COALESCE(?, org), updated = ? WHERE id = ?",
                    (name, role, org, today, person_id),
                )
                people_results.append({"slug": slug, "action": "updated", "id": person_id})
            else:
                cur = conn.execute(
                    "INSERT INTO people (slug, name, role, org, created, updated) VALUES (?, ?, ?, ?, ?, ?)",
                    (slug, name, role, org, today, today),
                )
                person_id = cur.lastrowid
                people_results.append({"slug": slug, "action": "created", "id": person_id})

        # --- Relations ---
        relations = data.get("relations", [])
        for rel in relations:
            from_ref = rel["from"]
            to_ref = rel["to"]
            relation = rel["relation"]

            from_type, from_slug = from_ref.split("/", 1)
            to_type, to_slug = to_ref.split("/", 1)

            from_row = conn.execute(
                "SELECT id FROM entities WHERE type = ? AND slug = ?",
                (from_type, from_slug),
            ).fetchone()
            to_row = conn.execute(
                "SELECT id FROM entities WHERE type = ? AND slug = ?",
                (to_type, to_slug),
            ).fetchone()

            if from_row and to_row:
                conn.execute(
                    "INSERT INTO relations (from_id, relation, to_id) VALUES (?, ?, ?)",
                    (from_row["id"], relation, to_row["id"]),
                )
                relations_added += 1
            else:
                click.echo(
                    "Warning: skipping relation {} -> {}, entity not found".format(from_ref, to_ref),
                    err=True,
                )

        # --- Entity-People links ---
        entity_people = data.get("entity_people", [])
        for ep in entity_people:
            entity_ref = ep["entity"]
            person_slug = ep["person"]
            role = ep.get("role")

            ep_type, ep_slug = entity_ref.split("/", 1)
            entity_row = conn.execute(
                "SELECT id FROM entities WHERE type = ? AND slug = ?",
                (ep_type, ep_slug),
            ).fetchone()
            person_row = conn.execute(
                "SELECT id FROM people WHERE slug = ?",
                (person_slug,),
            ).fetchone()

            if entity_row and person_row:
                conn.execute(
                    "INSERT OR IGNORE INTO entity_people (entity_id, person_id, role) VALUES (?, ?, ?)",
                    (entity_row["id"], person_row["id"], role),
                )
                entity_people_added += 1
            else:
                click.echo(
                    "Warning: skipping entity_people link {}/{}, not found".format(entity_ref, person_slug),
                    err=True,
                )

        conn.commit()

        result = {
            "entities": entity_results,
            "people": people_results,
            "relations_added": relations_added,
            "entity_people_added": entity_people_added,
        }  # type: Dict[str, Any]
        if source_id is not None:
            result["source_id"] = source_id

        click.echo(json.dumps(result, indent=2))

    except Exception as e:
        conn.rollback()
        click.echo(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)
    finally:
        conn.close()
