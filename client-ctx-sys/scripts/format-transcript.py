#!/usr/bin/env python3
"""Format raw Fireflies JSON into speaker-attributed markdown. Outputs JSON to stdout."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def _format_time(seconds: float) -> str:
    total = int(seconds)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    if h > 0:
        return "{}:{:02d}:{:02d}".format(h, m, s)
    return "{}:{:02d}".format(m, s)


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: format-transcript.py <raw-json-path>"}))
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(json.dumps({"error": "File not found: {}".format(sys.argv[1])}))
        sys.exit(1)

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(json.dumps({"error": "Invalid JSON: {}".format(str(e))}))
        sys.exit(1)

    sentences = data.get("sentences", [])  # type: List[Dict[str, Any]]
    speakers = data.get("speakers", [])  # type: List[Dict[str, Any]]
    title = data.get("title", "")
    date_str = data.get("dateString", data.get("date", ""))

    if not sentences:
        print(json.dumps({"error": "No sentences found in transcript"}))
        sys.exit(1)

    # Build speaker list
    speaker_names = []  # type: List[str]
    for s in speakers:
        if isinstance(s, dict):
            name = s.get("name", "")
            if name and name not in speaker_names:
                speaker_names.append(name)

    # Build formatted transcript
    lines = []  # type: List[str]
    lines.append("## Speakers\n")
    for name in speaker_names:
        lines.append("- {}".format(name))
    lines.append("")
    lines.append("## Transcript\n")

    current_speaker = ""
    current_block = []  # type: List[str]
    block_start = 0.0

    for sentence in sentences:
        speaker = sentence.get("speaker_name", "Unknown")
        text = sentence.get("text", "").strip()
        start = sentence.get("start_time", 0.0)

        if not text:
            continue

        if speaker != current_speaker:
            if current_block:
                lines.append("**{}** ({})\n".format(current_speaker, _format_time(block_start)))
                lines.append(" ".join(current_block))
                lines.append("")
            current_speaker = speaker
            current_block = [text]
            block_start = start
        else:
            current_block.append(text)

    if current_block:
        lines.append("**{}** ({})\n".format(current_speaker, _format_time(block_start)))
        lines.append(" ".join(current_block))
        lines.append("")

    print(json.dumps({
        "title": title,
        "date": date_str,
        "speakers": speaker_names,
        "transcript_md": "\n".join(lines),
    }, indent=2))


if __name__ == "__main__":
    main()
