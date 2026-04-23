#!/usr/bin/env python3
"""Local statusline for client-mgt-market dev repo. Logs raw JSON + displays session info."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).parent / "statusline-debug.log"

# --- ANSI colors ---
DIM = "\033[2m"
RESET = "\033[0m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
ORANGE = "\033[38;5;208m"
BOLD = "\033[1m"


def read_stdin_json() -> dict:
    try:
        data = sys.stdin.read()
        if data.strip():
            return json.loads(data), data
    except Exception:
        pass
    return {}, ""


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

    bar = color + "█" * filled + DIM + "░" * empty + RESET
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


def main() -> None:
    data, raw = read_stdin_json()

    # Log raw JSON
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"\n--- {timestamp} ---\n")
        if data:
            f.write(json.dumps(data, indent=2) + "\n")
        else:
            f.write(f"RAW: {raw}\n")

    if not data:
        print("")
        return

    model = data.get("model", {}).get("display_name", "unknown")
    pct = float(data.get("context_window", {}).get("used_percentage", 0))
    cost = float(data.get("cost", {}).get("total_cost_usd", 0))
    duration_ms = float(data.get("cost", {}).get("total_duration_ms", 0))

    parts = [
        ORANGE + BOLD + "📦 client-ctx-sys" + RESET,
        CYAN + model + RESET,
        format_context_bar(pct),
        DIM + "${:.2f}".format(cost) + RESET,
        DIM + format_duration(duration_ms) + RESET,
    ]
    print(" │ ".join(parts))


if __name__ == "__main__":
    main()
