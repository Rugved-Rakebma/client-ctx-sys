#!/usr/bin/env python3
"""Statusline for client-ctx-sys. Two-line output:
Line 1: model, context window bar, cost, session duration (from stdin JSON)
Line 2: vault state — client name, projects, open items, last meeting (from filesystem)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


# --- ANSI colors ---
DIM = "\033[2m"
RESET = "\033[0m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
WHITE = "\033[37m"
BOLD = "\033[1m"


def read_stdin_json() -> dict:
    try:
        data = sys.stdin.read()
        if data.strip():
            return json.loads(data)
    except Exception:
        pass
    return {}


def format_context_bar(pct: float, width: int = 25) -> str:
    pct_int = int(pct)
    filled = int(pct * width / 100)
    empty = width - filled

    if pct_int < 50:
        color = GREEN
    elif pct_int < 75:
        color = YELLOW
    else:
        color = RED

    bar = color
    bar += "█" * filled
    bar += DIM + "░" * empty + RESET
    bar += " " + color + "{}%".format(pct_int) + RESET

    return bar


def format_duration(ms: float) -> str:
    secs = int(ms / 1000)
    if secs >= 3600:
        return "{}h{}m".format(secs // 3600, secs % 3600 // 60)
    elif secs >= 60:
        return "{}m".format(secs // 60)
    else:
        return "{}s".format(secs)


def format_cost(usd: float) -> str:
    return "${:.2f}".format(usd)


def format_session_line(data: dict) -> str:
    model = data.get("model", {}).get("display_name", "unknown")
    pct = float(data.get("context", {}).get("used_percent", 0))
    cost = float(data.get("cost", {}).get("total_cost_usd", 0))
    duration_ms = float(data.get("cost", {}).get("total_duration_ms", 0))

    parts = [
        CYAN + model + RESET,
        format_context_bar(pct),
        DIM + format_cost(cost) + RESET,
        DIM + format_duration(duration_ms) + RESET,
    ]

    return " │ ".join(parts)


# --- Vault reading (filesystem) ---

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


def format_vault_line(vault: Path) -> str:
    if not vault.exists():
        return ""

    name = get_project_name(vault)
    projects = count_projects(vault)
    open_items = count_open_items(vault)
    last_meeting = last_meeting_date(vault)

    parts = [BOLD + WHITE + name + RESET]
    if projects:
        parts.append("{} projects".format(projects))
    if open_items:
        color = YELLOW if open_items >= 5 else WHITE
        parts.append(color + "{} open tasks".format(open_items) + RESET)
    if last_meeting:
        parts.append(DIM + "last mtg " + last_meeting + RESET)

    return " │ ".join(parts)


def main() -> None:
    vault_path = sys.argv[1] if len(sys.argv) > 1 else "context-vault"
    vault = Path(vault_path)

    data = read_stdin_json()

    # Line 1: session info (always show if we have stdin data)
    if data:
        print(format_session_line(data))

    # Line 2: vault info (only if vault exists)
    vault_line = format_vault_line(vault)
    if vault_line:
        print(vault_line)
    elif not data:
        # No stdin data and no vault — empty output
        print("")


if __name__ == "__main__":
    main()
