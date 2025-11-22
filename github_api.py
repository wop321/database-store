import base64
import os
import requests

USERNAME = os.getenv("GITHUB_USERNAME")
REPO = os.getenv("GITHUB_REPO")
FILE_PATH = os.getenv("GITHUB_FILE_PATH")
TOKEN = os.getenv("GITHUB_TOKEN")

API_URL = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{FILE_PATH}"


def github_add_entry(entry_text: str):
    """
    Appends a new entry to the GitHub-hosted database.txt file.
    The file is also served on GitHub Pages.
    """
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    # Get the current file state
    r = requests.get(API_URL, headers=headers)
    if r.status_code != 200:
        raise RuntimeError("Failed to fetch GitHub file:\n" + r.text)

    file_data = r.json()
    sha = file_data["sha"]
    current = base64.b64decode(file_data["content"]).decode("utf-8")

    # Append new entry
    new_content = current.rstrip() + "\n" + entry_text + "\n"

    encoded = base64.b64encode(new_content.encode()).decode()

    payload = {
        "message": "Add entry via Discord bot",
        "content": encoded,
        "sha": sha
    }

    update = requests.put(API_URL, json=payload, headers=headers)
    if update.status_code not in [200, 201]:
        raise RuntimeError("GitHub update failed:\n" + update.text)
