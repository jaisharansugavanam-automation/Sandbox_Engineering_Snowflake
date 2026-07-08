# ============================================================
# File       : test_atlassian_connection.py
# Folder     : DataOps_Python/
# Purpose    : Smoke test — create a Jira ticket and Confluence page
#              to verify Atlassian connectivity
# Created    : 2026-07-04
# Author     : Sandy DataOps
# Run        : python DataOps_Python/test_atlassian_connection.py
# ============================================================

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from atlassian import Confluence, Jira

# Load credentials from .env at repo root (git-ignored)
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

CONFIG_PATH = Path(__file__).resolve().parent / "config" / "jiira_confluence_credentials.json"


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get_credentials():
    username = os.environ.get("CONFLUENCE_USERNAME")
    api_token = os.environ.get("CONFLUENCE_API_TOKEN")
    if not username or not api_token:
        raise EnvironmentError(
            "\n  Missing credentials. Set these env vars before running:\n"
            "    export CONFLUENCE_USERNAME='your@email.com'\n"
            "    export CONFLUENCE_API_TOKEN='your_token'\n"
        )
    return username, api_token


def test_jira(config, username, api_token):
    print("\n── Jira Connection Test ──────────────────")
    jira = Jira(
        url=config["jira"]["url"],
        username=username,
        password=api_token,
        cloud=True,
    )
    issue = jira.issue_create(
        fields={
            "project": {"key": config["jira"]["project_key"]},
            "summary": "Gratitude to Ganesha 🙏 Om Gan Ganapate Namah",
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Om Gan Ganapate Namah 🙏 — Sandy DataOps connection test. Blessings for the project!",
                            }
                        ],
                    }
                ],
            },
            "issuetype": {"name": "Task"},
        }
    )
    print(f"  ✅ Jira ticket created: {issue['key']} — {config['jira']['url']}/browse/{issue['key']}")
    return issue["key"]


def test_confluence(config, username, api_token):
    print("\n── Confluence Connection Test ────────────")
    confluence = Confluence(
        url=config["confluence"]["url"],
        username=username,
        password=api_token,
        cloud=True,
    )
    title = "Om Gan Ganapate Namah — Sandy DataOps Connection Test"
    body = (
        "<h1>🙏 Om Gan Ganapate Namah</h1>"
        "<p>Sandy Enterprise DataOps Accelerator — Atlassian connection verified successfully.</p>"
        "<p><em>Metadata drives everything. AI reasons. Python executes.</em></p>"
    )
    space_key = config["confluence"]["space_key"]

    existing = confluence.get_page_by_title(space=space_key, title=title)
    if existing:
        result = confluence.update_page(
            page_id=existing["id"],
            title=title,
            body=body,
        )
        page_id = existing["id"]
        print(f"  ✅ Confluence page updated: ID {page_id}")
    else:
        result = confluence.create_page(
            space=space_key,
            title=title,
            body=body,
        )
        page_id = result["id"]
        print(f"  ✅ Confluence page created: ID {page_id}")

    print(f"     URL: {config['confluence']['url']}/wiki/spaces/{space_key}/pages/{page_id}")


if __name__ == "__main__":
    config = load_config()
    username, api_token = get_credentials()

    print("═══════════════════════════════════════════")
    print("  Sandy DataOps — Atlassian Connection Test")
    print("═══════════════════════════════════════════")

    try:
        test_jira(config, username, api_token)
    except Exception as e:
        print(f"  ⚠️  Jira skipped: {e}")
        print("     Create a Jira project first at:", config["jira"]["url"])

    test_confluence(config, username, api_token)

    print("\n  🙏 Om Gan Ganapate Namah. Connection test complete.\n")
