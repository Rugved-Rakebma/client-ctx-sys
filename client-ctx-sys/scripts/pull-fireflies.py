#!/usr/bin/env python3
"""Pull transcripts from Fireflies.ai. Outputs JSON to stdout."""
from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional


FIREFLIES_API_URL = "https://api.fireflies.ai/graphql"
FIREFLIES_VIEW_PREFIX = "https://app.fireflies.ai/view/"


def _load_dotenv() -> None:
    """Load .env from current directory or parent directories (up to 3 levels)."""
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents)[:3]:
        env_file = parent / ".env"
        if env_file.exists():
            try:
                for line in env_file.read_text().splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip("'\"")
                    if key and key not in os.environ:
                        os.environ[key] = value
            except Exception:
                pass
            break

QUERY_LIST = """
query { transcripts { id title dateString date } }
"""

QUERY_GET = """
query GetTranscript($id: String!) {
  transcript(id: $id) {
    id title date dateString transcript_url duration
    sentences { speaker_name text start_time end_time }
    summary { action_items outline overview keywords short_summary }
    speakers { id name }
  }
}
"""


def _parse_url(url: str) -> str:
    if url.startswith(FIREFLIES_VIEW_PREFIX):
        path = url[len(FIREFLIES_VIEW_PREFIX):]
    else:
        path = url
    return path.split("::")[-1] if "::" in path else path


def _gql(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    api_key = os.environ.get("FIREFLIES_API_KEY", "")
    if not api_key:
        print(json.dumps({"error": "FIREFLIES_API_KEY not set"}), file=sys.stdout)
        sys.exit(1)

    payload = {"query": query}  # type: Dict[str, Any]
    if variables:
        payload["variables"] = variables

    req = urllib.request.Request(
        FIREFLIES_API_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": "Bearer {}".format(api_key),
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())

    if "errors" in data:
        print(json.dumps({"error": "API error", "details": data["errors"]}), file=sys.stdout)
        sys.exit(1)
    return data.get("data", {})


def cmd_list() -> None:
    data = _gql(QUERY_LIST)
    result = []  # type: List[Dict[str, Any]]
    for t in data.get("transcripts", []):
        result.append({"id": t.get("id"), "title": t.get("title", ""), "date": t.get("dateString", t.get("date", ""))})
    print(json.dumps(result, indent=2))


def cmd_pull(target_id: str, vault_dir: str) -> None:
    data = _gql(QUERY_GET, {"id": target_id})
    transcript = data.get("transcript", {})

    # Save raw JSON
    raw_dir = Path(vault_dir) / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    safe_title = (transcript.get("title", target_id) or target_id).replace("/", "_").replace(" ", "_")
    raw_file = raw_dir / "{}.json".format(safe_title)
    raw_file.write_text(json.dumps(transcript, indent=2))

    summary = transcript.get("summary", {}) or {}
    speakers = transcript.get("speakers", []) or []

    print(json.dumps({
        "transcript_id": target_id,
        "title": transcript.get("title", ""),
        "date": transcript.get("dateString", transcript.get("date", "")),
        "file": str(raw_file),
        "speakers": [s.get("name", "") for s in speakers if isinstance(s, dict)],
        "summary": {
            "action_items": summary.get("action_items", ""),
            "outline": summary.get("outline", ""),
            "overview": summary.get("overview", ""),
            "keywords": summary.get("keywords", []),
            "short_summary": summary.get("short_summary", ""),
        },
    }, indent=2))


def main() -> None:
    _load_dotenv()
    import argparse
    parser = argparse.ArgumentParser(description="Pull transcripts from Fireflies.ai")
    parser.add_argument("--latest", action="store_true", help="Pull most recent transcript")
    parser.add_argument("--id", dest="transcript_id", help="Pull by transcript ID")
    parser.add_argument("--url", help="Pull from Fireflies URL")
    parser.add_argument("--list", action="store_true", help="List recent transcripts")
    parser.add_argument("--vault-dir", default="context-vault", help="Path to context-vault/")
    args = parser.parse_args()

    if args.list:
        cmd_list()
        return

    target_id = args.transcript_id
    if args.url:
        target_id = _parse_url(args.url)
    if args.latest and not target_id:
        data = _gql(QUERY_LIST)
        transcripts = data.get("transcripts", [])
        if not transcripts:
            print(json.dumps({"error": "No transcripts found"}))
            sys.exit(1)
        target_id = transcripts[0].get("id")

    if not target_id:
        print(json.dumps({"error": "Specify --latest, --id, --url, or --list"}))
        sys.exit(1)

    cmd_pull(target_id, args.vault_dir)


if __name__ == "__main__":
    main()
