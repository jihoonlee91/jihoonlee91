"""Refresh the "Latest writing" list in README.md from the homepage's Atom feed.

Runs in .github/workflows/latest-posts.yml. Standard library only, so the
workflow needs no third-party action or package.
"""
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

FEED = "https://jihoonlee91.github.io/feed.xml"
LIMIT = 3
ATOM = "{http://www.w3.org/2005/Atom}"
START, END = "<!-- BLOG-POST-LIST:START -->", "<!-- BLOG-POST-LIST:END -->"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def main():
    with urllib.request.urlopen(FEED, timeout=30) as resp:
        root = ET.fromstring(resp.read())
    lines = []
    for entry in root.findall(f"{ATOM}entry")[:LIMIT]:
        title = entry.findtext(f"{ATOM}title", "").strip()
        link = entry.find(f"{ATOM}link").get("href")
        y, m, d = (int(x) for x in entry.findtext(f"{ATOM}published", "")[:10].split("-"))
        lines.append(f"- [{title}]({link}) — {MONTHS[m - 1]} {d}, {y}")
    if not lines:
        print("feed has no entries; leaving README unchanged")
        return 0
    with open("README.md", encoding="utf-8") as f:
        readme = f.read()
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(readme):
        print("markers not found in README.md", file=sys.stderr)
        return 1
    updated = pattern.sub(START + "\n" + "\n".join(lines) + "\n" + END, readme)
    if updated != readme:
        with open("README.md", "w", encoding="utf-8", newline="\n") as f:
            f.write(updated)
        print("README updated")
    else:
        print("README already current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
