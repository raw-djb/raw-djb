import os
import sys
import urllib.request
import json

USERNAME = os.environ.get("GH_USERNAME", "raw-djb")
README_PATH = os.environ.get("README_PATH", "../README.md")
MAX_REPOS = 5

START_MARKER = "<!--START_PROJECTS-->"
END_MARKER = "<!--END_PROJECTS-->"

API_URL = f"https://api.github.com/users/{USERNAME}/repos?sort=pushed&direction=desc&per_page=100"


def fetch_repos():
    req = urllib.request.Request(
        API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": USERNAME,
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())

    repos = [r for r in data if not r.get("private") and not r.get("fork") and not r.get("archived")]
    return repos[:MAX_REPOS]


def format_repos(repos):
    if not repos:
        return "_No public repositories yet._"

    lines = []
    for r in repos:
        name = r["name"]
        url = r["html_url"]
        desc = (r.get("description") or "").strip()
        lang = r.get("language")
        stars = r.get("stargazers_count", 0)

        meta_bits = []
        if lang:
            meta_bits.append(lang)
        if stars:
            meta_bits.append(f"★ {stars}")
        meta = f" — _{', '.join(meta_bits)}_" if meta_bits else ""

        desc_line = f"  {desc}" if desc else ""
        lines.append(f"- **[{name}]({url})**{meta}\n{desc_line}".rstrip())

    return "\n".join(lines)


def update_readme(new_block):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if START_MARKER not in content or END_MARKER not in content:
        print(f"Markers not found in {README_PATH}; nothing to update.", file=sys.stderr)
        sys.exit(1)

    before, rest = content.split(START_MARKER, 1)
    _, after = rest.split(END_MARKER, 1)

    updated = f"{before}{START_MARKER}\n{new_block}\n{END_MARKER}{after}"

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated)


def main():
    repos = fetch_repos()
    block = format_repos(repos)
    update_readme(block)
    print(f"Updated {README_PATH} with {len(repos)} repositories.")


if __name__ == "__main__":
    main()
