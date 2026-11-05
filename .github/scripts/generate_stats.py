
import os
import json
import urllib.request
import html
from pathlib import Path

USERNAME = "badhon220"
TOKEN = os.environ["GITHUB_TOKEN"]

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "Badhon-GitHub-Stats"
}

def api(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read())

user = api(f"https://api.github.com/users/{USERNAME}")
repos = api(f"https://api.github.com/users/{USERNAME}/repos?per_page=100")

public_repos = [r for r in repos if not r["fork"]]

stars = sum(r["stargazers_count"] for r in public_repos)
forks = sum(r["forks_count"] for r in public_repos)

languages = {}

for repo in public_repos:
    try:
        data = api(repo["languages_url"])
        for lang, size in data.items():
            languages[lang] = languages.get(lang, 0) + size
    except Exception:
        pass

total = sum(languages.values()) or 1
top_languages = sorted(
    languages.items(),
    key=lambda item: item[1],
    reverse=True
)[:5]

Path("profile").mkdir(exist_ok=True)

def stats_card():
    items = [
        ("Public Repositories", user["public_repos"]),
        ("Followers", user["followers"]),
        ("Total Stars", stars),
        ("Total Forks", forks)
    ]

    rows = ""
    for i, (label, value) in enumerate(items):
        y = 75 + i * 29
        rows += f"""
        <text x="30" y="{y}" fill="#c9d1d9" font-size="13">{label}</text>
        <text x="455" y="{y}" fill="#00ff66" font-size="14"
              text-anchor="end" font-weight="bold">{value}</text>
        """

    return f"""<svg xmlns="http://www.w3.org/2000/svg"
    width="495" height="190" viewBox="0 0 495 190">
    <rect width="495" height="190" rx="12" fill="#0d1117"
          stroke="#30363d"/>
    <text x="30" y="38" fill="#00ff66" font-size="18"
          font-weight="bold">GitHub Statistics</text>
    <line x1="30" y1="50" x2="465" y2="50"
          stroke="#30363d"/>
    {rows}
    </svg>"""

def language_card():
    bars = ""
    y = 80

    for lang, size in top_languages:
        percent = size / total * 100
        width = 270 * percent / 100
        safe_lang = html.escape(lang)

        bars += f"""
        <text x="30" y="{y}" fill="#c9d1d9"
              font-size="13">{safe_lang}</text>
        <rect x="150" y="{y-12}" width="270" height="10"
              rx="5" fill="#30363d"/>
        <rect x="150" y="{y-12}" width="{width:.2f}" height="10"
              rx="5" fill="#00ff66"/>
        <text x="460" y="{y}" fill="#00ff66"
              font-size="12" text-anchor="end">
              {percent:.1f}%
        </text>
        """
        y += 23

    if not bars:
        bars = '<text x="30" y="85" fill="#c9d1d9">No language data yet</text>'

    return f"""<svg xmlns="http://www.w3.org/2000/svg"
    width="495" height="190" viewBox="0 0 495 190">
    <rect width="495" height="190" rx="12" fill="#0d1117"
          stroke="#30363d"/>
    <text x="30" y="38" fill="#00ff66" font-size="18"
          font-weight="bold">Top Languages</text>
    <line x1="30" y1="50" x2="465" y2="50"
          stroke="#30363d"/>
    {bars}
    </svg>"""

Path("profile/user.svg").write_text(stats_card(), encoding="utf-8")
Path("profile/langs.svg").write_text(language_card(), encoding="utf-8")

print("GitHub stats cards generated successfully!")
