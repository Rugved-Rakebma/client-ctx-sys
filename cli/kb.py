from __future__ import annotations

import os
import sys

# Ensure the cli package is importable when run as a script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click

from cli.commands.init import init
from cli.commands.status import status
from cli.commands.list_cmd import list_cmd
from cli.commands.get import get
from cli.commands.add import add
from cli.commands.search import search
from cli.commands.pull_fireflies import pull_fireflies


@click.group()
@click.option(
    "--kb-dir",
    default=".knowledge-base/",
    envvar="KB_DIR",
    help="Path to the .knowledge-base/ directory (default: .knowledge-base/).",
)
@click.version_option(version="0.2.0", prog_name="knowledge-base")
@click.pass_context
def cli(ctx: click.Context, kb_dir: str) -> None:
    """Knowledge base CLI — per-project knowledge management."""
    ctx.ensure_object(dict)
    ctx.obj["kb_dir"] = kb_dir


cli.add_command(init)
cli.add_command(status)
cli.add_command(list_cmd, "list")
cli.add_command(get)
cli.add_command(add)
cli.add_command(search)
cli.add_command(pull_fireflies, "pull-fireflies")


if __name__ == "__main__":
    cli()
