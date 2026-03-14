from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import click
import httpx


FIREFLIES_API_URL = "https://api.fireflies.ai/graphql"
FIREFLIES_VIEW_PREFIX = "https://app.fireflies.ai/view/"


def _parse_fireflies_url(url: str) -> str:
    """Extract transcript ID from a Fireflies URL.

    Format: https://app.fireflies.ai/view/<title>::<id>
    """
    if url.startswith(FIREFLIES_VIEW_PREFIX):
        path = url[len(FIREFLIES_VIEW_PREFIX):]
    else:
        path = url

    if "::" in path:
        return path.split("::")[-1]
    return path

QUERY_LIST_TRANSCRIPTS = """
query {
  transcripts {
    id
    title
    dateString
    date
  }
}
"""

QUERY_GET_TRANSCRIPT = """
query GetTranscript($id: String!) {
  transcript(id: $id) {
    id
    title
    date
    dateString
    transcript_url
    duration
    sentences {
      speaker_name
      text
      start_time
      end_time
    }
    summary {
      action_items
      outline
      overview
      keywords
      short_summary
    }
    speakers {
      id
      name
    }
  }
}
"""


def _get_api_key() -> str:
    key = os.environ.get("FIREFLIES_API_KEY", "")
    if not key:
        raise click.ClickException(
            "FIREFLIES_API_KEY environment variable is not set."
        )
    return key


def _gql(query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    api_key = _get_api_key()
    headers = {
        "Authorization": "Bearer {}".format(api_key),
        "Content-Type": "application/json",
    }
    payload: Dict[str, Any] = {"query": query}
    if variables:
        payload["variables"] = variables

    resp = httpx.post(FIREFLIES_API_URL, json=payload, headers=headers, timeout=30.0)
    resp.raise_for_status()
    data = resp.json()

    if "errors" in data:
        raise click.ClickException(
            "Fireflies API error: {}".format(json.dumps(data["errors"]))
        )
    return data.get("data", {})


@click.command("pull-fireflies")
@click.option("--latest", is_flag=True, default=False, help="Pull the most recent transcript.")
@click.option("--id", "transcript_id", default=None, help="Pull a specific transcript by ID.")
@click.option("--url", default=None, help="Pull transcript from a Fireflies URL.")
@click.option("--list", "list_mode", is_flag=True, default=False, help="List recent transcripts.")
@click.pass_context
def pull_fireflies(
    ctx: click.Context,
    latest: bool,
    transcript_id: Optional[str],
    url: Optional[str],
    list_mode: bool,
) -> None:
    """Pull transcripts from Fireflies.ai."""
    kb_dir = Path(ctx.obj["kb_dir"])

    if not kb_dir.exists() and not list_mode:
        click.echo(json.dumps({"error": ".knowledge-base/ directory not found"}, indent=2))
        sys.exit(1)

    if list_mode:
        data = _gql(QUERY_LIST_TRANSCRIPTS)
        transcripts = data.get("transcripts", [])
        result = []
        for t in transcripts:
            result.append(
                {
                    "id": t.get("id"),
                    "title": t.get("title", ""),
                    "date": t.get("dateString", t.get("date", "")),
                }
            )
        click.echo(json.dumps(result, indent=2))
        return

    # Determine which transcript to fetch
    if url:
        transcript_id = _parse_fireflies_url(url)
    target_id = transcript_id
    if latest and not target_id:
        data = _gql(QUERY_LIST_TRANSCRIPTS)
        transcripts = data.get("transcripts", [])
        if not transcripts:
            click.echo(json.dumps({"error": "No transcripts found."}, indent=2))
            sys.exit(1)
        target_id = transcripts[0].get("id")

    if not target_id:
        click.echo(
            json.dumps(
                {"error": "Specify --latest, --id, or --list."},
                indent=2,
            )
        )
        sys.exit(1)

    # Fetch the full transcript
    data = _gql(QUERY_GET_TRANSCRIPT, {"id": target_id})
    transcript = data.get("transcript", {})

    # Save raw JSON
    raw_dir = kb_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    safe_title = (transcript.get("title", target_id) or target_id).replace("/", "_").replace(" ", "_")
    raw_file = raw_dir / "{}.json".format(safe_title)
    raw_file.write_text(json.dumps(transcript, indent=2))

    # Extract summary data
    summary = transcript.get("summary", {}) or {}
    speakers = transcript.get("speakers", []) or []

    click.echo(
        json.dumps(
            {
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
            },
            indent=2,
        )
    )
