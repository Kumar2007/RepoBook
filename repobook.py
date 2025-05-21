#!/usr/bin/env python3

import json
import argparse
import os
from datetime import datetime
import requests

DB_FILE = "repos.json"
README_FILE = "GENERATED_README.md"

def load_repos():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_repos(repos):
    with open(DB_FILE, "w") as f:
        json.dump(repos, f, indent=2)

def fetch_github_metadata(url):
    try:
        parts = url.rstrip("/").split("/")
        user, repo = parts[-2], parts[-1]
        api_url = f"https://api.github.com/repos/{user}/{repo}"
        response = requests.get(api_url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            return {
                "name": data.get("name"),
                "description": data.get("description"),
                "stars": data.get("stargazers_count"),
                "last_updated": data.get("updated_at")
            }
        else:
            print(f"⚠️ GitHub API failed: {response.status_code}")
            return {}
    except Exception as e:
        print(f"⚠️ Error fetching metadata: {e}")
        return {}

def add_repo(url, tags, use_api=False, section=None):
    repos = load_repos()

    if any(r["url"] == url for r in repos):
        print("⚠️ Repo already exists in your list.")
        return

    metadata = fetch_github_metadata(url) if use_api else {}

    repo = {
        "url": url,
        "tags": tags,
        "section": section or "Uncategorized",
        "added": datetime.now().isoformat(),
        "metadata": metadata
    }
    repos.append(repo)
    save_repos(repos)
    generate_readme(repos)
    print(f"✅ Repo added! {metadata.get('name', '') or url}")

def list_repos():
    repos = load_repos()
    if not repos:
        print("📭 No repos yet.")
        return

    # Group by section for display
    sections = {}
    for repo in repos:
        sec = repo.get("section", "Uncategorized")
        sections.setdefault(sec, []).append(repo)

    for section_name in sorted(sections.keys()):
        print(f"== {section_name} ==")
        for i, repo in enumerate(sections[section_name], 1):
            meta = repo.get("metadata", {})
            stars = f"⭐ {meta.get('stars')}" if meta.get("stars") else ""
            print(f"{i}. {meta.get('name', repo['url'])} - {repo['url']} {stars}")
            if meta.get("description"):
                print(f"   📝 {meta['description']}")
            if repo['tags']:
                print(f"   🔖 Tags: {', '.join(repo['tags'])}")
            print()

def search_repos(query):
    repos = load_repos()
    matches = [r for r in repos if query.lower() in r['url'].lower() or
               any(query.lower() in t.lower() for t in r['tags']) or
               query.lower() in (r.get("metadata", {}).get("name") or "").lower() or
               query.lower() in (r.get("section") or "").lower()]
    if not matches:
        print("🔍 No matches found.")
        return
    for i, repo in enumerate(matches, 1):
        meta = repo.get("metadata", {})
        print(f"{i}. {meta.get('name', repo['url'])} - {repo['url']} (Section: {repo.get('section', 'Uncategorized')})")

def delete_repo(index):
    repos = load_repos()
    if index < 1 or index > len(repos):
        print("❗ Invalid index.")
        return
    deleted = repos.pop(index - 1)
    save_repos(repos)
    generate_readme(repos)
    print(f"🗑️ Deleted: {deleted['url']}")

def generate_readme(repos):
    lines = [
        "# 📚 RepoBook Directory",
        "",
        "A curated list of GitHub repositories managed by RepoBook CLI tool.",
        "",
        "## Repositories",
        ""
    ]

    if not repos:
        lines.append("_No repositories added yet._\n")
    else:
        # Group by section
        sections = {}
        for repo in repos:
            sec = repo.get("section", "Uncategorized")
            sections.setdefault(sec, []).append(repo)

        for section_name in sorted(sections.keys()):
            lines.append(f"## {section_name}")
            lines.append("")
            for repo in sections[section_name]:
                meta = repo.get("metadata", {})
                name = meta.get("name") or repo["url"]
                description = meta.get("description") or ""
                stars = meta.get("stars")
                stars_str = f"⭐ {stars}" if stars is not None else ""
                tags_str = ", ".join(repo["tags"]) if repo["tags"] else ""
                lines.append(f"### [{name}]({repo['url']}) {stars_str}")
                if description:
                    lines.append(f"> {description}")
                if tags_str:
                    lines.append(f"**Tags:** {tags_str}")
                lines.append("")
            lines.append("---")
            lines.append("")

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def main():
    parser = argparse.ArgumentParser(description="📚 RepoBook: Manage GitHub repo links like a digital phonebook.")
    subparsers = parser.add_subparsers(dest="command")

    add_cmd = subparsers.add_parser("add", help="Add a GitHub repo")
    add_cmd.add_argument("url", help="GitHub repo URL")
    add_cmd.add_argument("--tags", nargs="+", default=[], help="Optional tags")
    add_cmd.add_argument("--fetch", action="store_true", help="Fetch metadata using GitHub API")
    add_cmd.add_argument("--section", type=str, default=None, help="Optional section/category name")

    subparsers.add_parser("list", help="List all saved repos")

    search_cmd = subparsers.add_parser("search", help="Search repos by keyword/tag/section")
    search_cmd.add_argument("query", help="Search term")

    del_cmd = subparsers.add_parser("delete", help="Delete repo by index")
    del_cmd.add_argument("index", type=int, help="Index from list")

    args = parser.parse_args()

    if args.command == "add":
        add_repo(args.url, args.tags, args.fetch, args.section)
    elif args.command == "list":
        list_repos()
    elif args.command == "search":
        search_repos(args.query)
    elif args.command == "delete":
        delete_repo(args.index)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
