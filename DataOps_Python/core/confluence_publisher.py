# ============================================================
# File       : confluence_publisher.py
# Folder     : DataOps_Python/core/
# Purpose    : Read a Markdown file and publish/update it as a Confluence page
# Layer      : core (reusable)
# Created    : 2026-07-04
# Author     : Sandy DataOps
# Notes      : Credentials come from env vars (CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN)
#              Non-sensitive config (url, space_key) read from config JSON
# ============================================================

import json
import os
from pathlib import Path

from atlassian import Confluence


CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "jiira_confluence_credentials.json"


def _load_config() -> dict:
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def _get_confluence_client(config: dict) -> Confluence:
    username = os.environ.get("CONFLUENCE_USERNAME")
    api_token = os.environ.get("CONFLUENCE_API_TOKEN")

    if not username or not api_token:
        raise EnvironmentError(
            "CONFLUENCE_USERNAME and CONFLUENCE_API_TOKEN must be set as environment variables."
        )

    return Confluence(
        url=config["confluence"]["url"],
        username=username,
        password=api_token,
        cloud=True,
    )


def publish_md_to_confluence(md_file_path: str) -> dict:
    """
    Takes a Markdown file path, reads its content, and creates or updates
    the corresponding Confluence page under the configured parent page.

    Args:
        md_file_path (str): Absolute or relative path to the .md file.

    Returns:
        dict: Confluence API response with page id and url.
    """
    md_path = Path(md_file_path).resolve()

    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    content = md_path.read_text(encoding="utf-8")
    page_title = md_path.stem.replace("_", " ")  # e.g. Sandy_Consultancy_Overview → Sandy Consultancy Overview

    config = _load_config()
    confluence = _get_confluence_client(config)

    space_key = config["confluence"]["space_key"]
    parent_title = config["confluence"]["parent_page_title"]

    # Resolve parent page id
    parent_page = confluence.get_page_by_title(space=space_key, title=parent_title)
    parent_id = parent_page["id"] if parent_page else None

    existing_page = confluence.get_page_by_title(space=space_key, title=page_title)

    if existing_page:
        result = confluence.update_page(
            page_id=existing_page["id"],
            title=page_title,
            body=content,
            representation="wiki",
        )
        print(f"[UPDATED] '{page_title}' — {existing_page['id']}")
    else:
        result = confluence.create_page(
            space=space_key,
            title=page_title,
            body=content,
            parent_id=parent_id,
            representation="wiki",
        )
        print(f"[CREATED] '{page_title}' — {result['id']}")

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python confluence_publisher.py <path_to_md_file>")
        sys.exit(1)

    publish_md_to_confluence(sys.argv[1])
