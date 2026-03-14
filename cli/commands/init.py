from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path
from typing import List

import click
import yaml

from cli.db.schema import init_db


TEMPLATE_PATH = Path.home() / "Code" / "knowledge-base" / "templates" / "config.yaml"

DEFAULT_CONFIG = """\
project: "{project_name}"
created: "{created_date}"

schema:
  entity_types: []

fireflies:
  api_key_env: FIREFLIES_API_KEY

people: []
"""


@click.command("init")
@click.option(
    "--project-name",
    default=None,
    help="Project name (defaults to current directory basename).",
)
@click.pass_context
def init(ctx: click.Context, project_name: str) -> None:
    """Initialise a .knowledge-base/ knowledge base in the current directory."""
    kb_dir = Path(ctx.obj["kb_dir"])

    if project_name is None:
        project_name = Path.cwd().name

    created: List[str] = []
    skipped: List[str] = []

    # --- .knowledge-base/ root ---
    if not kb_dir.exists():
        kb_dir.mkdir(parents=True)
        created.append(str(kb_dir))
    else:
        skipped.append(str(kb_dir))

    # --- config.yaml ---
    config_path = kb_dir / "config.yaml"
    if not config_path.exists():
        if TEMPLATE_PATH.exists():
            raw = TEMPLATE_PATH.read_text()
            content = raw.replace(
                "{project_name}", project_name
            ).replace(
                "{created_date}", datetime.date.today().isoformat()
            )
        else:
            content = DEFAULT_CONFIG.format(
                project_name=project_name,
                created_date=datetime.date.today().isoformat(),
            )
        config_path.write_text(content)
        created.append(str(config_path))
    else:
        skipped.append(str(config_path))

    # --- .gitignore ---
    gitignore_path = kb_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text("knowledge-base.db\nknowledge-base.db-wal\nknowledge-base.db-shm\n.staging.json\nraw/\n*.pyc\n")
        created.append(str(gitignore_path))
    else:
        skipped.append(str(gitignore_path))

    # --- docs/ ---
    docs_dir = kb_dir / "docs"
    if not docs_dir.exists():
        docs_dir.mkdir(parents=True)
        created.append(str(docs_dir))
    else:
        skipped.append(str(docs_dir))

    # --- docs/meetings/ ---
    meetings_dir = kb_dir / "docs" / "meetings"
    if not meetings_dir.exists():
        meetings_dir.mkdir(parents=True)
        created.append(str(meetings_dir))
    else:
        skipped.append(str(meetings_dir))

    # --- file-manifest.yaml ---
    manifest_path = kb_dir / "file-manifest.yaml"
    if not manifest_path.exists():
        manifest_path.write_text("# File manifest — document catalog\nfiles: []\n")
        created.append(str(manifest_path))
    else:
        skipped.append(str(manifest_path))

    # --- Initialize SQLite database ---
    db_path = kb_dir / "knowledge-base.db"
    db_str = str(db_path)
    init_db(db_str)
    if str(db_path) not in [str(p) for p in created]:
        # Always report the db path
        pass

    click.echo(
        json.dumps(
            {
                "created": created,
                "skipped": skipped,
                "db": str(db_path),
            },
            indent=2,
        )
    )
