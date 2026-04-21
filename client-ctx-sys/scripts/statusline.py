#!/usr/bin/env python3
"""Statusline script for client-ctx-sys. Reads context-vault and outputs a one-line status."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path


def count_open_items(vault: Path) -> int:
    ai_dir = vault / "action-items"
    if not ai_dir.exists():
        return 0
    count = 0
    for f in ai_dir.glob("*.md"):
        try:
            text = f.read_text(errors="ignore")
            if re.search(r'status:\s*["\']?open["\']?', text):
                count += 1
        except Exception:
            pass
    return count


def count_projects(vault: Path) -> int:
    proj_dir = vault / "projects"
    if not proj_dir.exists():
        return 0
    return len([d for d in proj_dir.iterdir() if d.is_dir()])


def get_project_name(vault: Path) -> str:
    config = vault / "config.yaml"
    if config.exists():
        try:
            text = config.read_text()
            m = re.search(r'project:\s*["\']?([^"\']+)', text)
            if m:
                return m.group(1).strip()
        except Exception:
            pass
    return vault.parent.name


def last_meeting_date(vault: Path) -> str:
    meetings = vault / "docs" / "meetings"
    if not meetings.exists():
        return ""
    files = sorted(meetings.glob("*.md"), reverse=True)
    if files:
        name = files[0].stem
        parts = name.split("-")
        if len(parts) >= 3:
            return "-".join(parts[:3])
    return ""


def main() -> None:
    vault_path = sys.argv[1] if len(sys.argv) > 1 else "context-vault"
    vault = Path(vault_path)

    if not vault.exists():
        print("")
        return

    name = get_project_name(vault)
    projects = count_projects(vault)
    open_items = count_open_items(vault)
    last_meeting = last_meeting_date(vault)

    parts = [name]
    if projects:
        parts.append("{} projects".format(projects))
    if open_items:
        parts.append("{} open items".format(open_items))
    if last_meeting:
        parts.append("last meeting: {}".format(last_meeting))

    print(" | ".join(parts))


if __name__ == "__main__":
    main()
