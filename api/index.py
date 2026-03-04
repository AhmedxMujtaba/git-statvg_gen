from flask import Flask, Response, request
import requests
import os
import re
from datetime import datetime

app = Flask(__name__)

def get_headers():
    token = os.environ.get("GITHUB_TOKEN")
    return {"Authorization": f"Bearer {token}"} if token else {}

def generate_svg_response(ascii_text, height=340):
    escaped_text = (ascii_text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('+', '&#43;')
        .replace(' ', '\u00A0'))  # non-breaking spaces — fixes HTML collapsing whitespace

    tspan_lines = ""
    for i, line in enumerate(escaped_text.strip('\n').split('\n')):
        dy = "0" if i == 0 else "16"
        tspan_lines += f'            <tspan x="20" dy="{dy}">{line}</tspan>\n'

    svg = f"""
    <svg width="520" height="{height}" viewBox="0 0 520 {height}" xmlns="http://www.w3.org/2000/svg">
        <text y="35" font-family="'Courier New', Courier, monospace" font-size="14" fill="#00d4ff">
{tspan_lines}
            <tspan x="20" dy="16" opacity="0.8">_</tspan>
        </text>
    </svg>
    """
    return Response(svg.strip(), status=200, mimetype='image/svg+xml', headers={
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Content-Type': 'image/svg+xml',
        'Access-Control-Allow-Origin': '*'
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def router(path):
    if path == 'languages': return language_terminal()
    if path == 'contributions': return contribution_terminal()
    if path == 'traffic': return traffic_terminal()
    if path == 'telemetry': return main_terminal()
    return main_terminal()

def main_terminal():
    user = "AhmedXMujtaba"
    try:
        r = requests.get(f"https://api.github.com/users/{user}", headers=get_headers())
        data = r.json()
        repos = data.get("public_repos", 0)
        followers = data.get("followers", 0)
        age = (datetime.now() - datetime.strptime(data.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")).days
    except: repos, followers, age = 0, 0, 0

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ascii_text = f"""
+-------------------------------------------------------+
| git-statvg_gen // SYSTEM_TELEMETRY                    |
+-------------------------------------------------------+
|                                                       |
|  ARCHITECT: {user.ljust(41)} |
|  STATUS:    LEAD_ARCHITECT                            |
|                                                       |
|  METRICS:                                             |
|  > REPOSITORIES: {str(repos).ljust(36)} |
|  > FOLLOWERS:    {str(followers).ljust(36)} |
|  > UPTIME:       {str(age).ljust(30)} DAYS |
|  > LAST_UPDATED: {now.ljust(36)} |
|                                                       |
|  CORE_STABILITY: [=========================] 100%     |
|  UPLINK: ACTIVE                                       |
+-------------------------------------------------------+"""
    return generate_svg_response(ascii_text)

def language_terminal():
    user = "AhmedXMujtaba"
    try:
        r = requests.get(f"https://api.github.com/users/{user}/repos?per_page=100", headers=get_headers())
        repos = r.json()
        langs = {}
        for repo in repos:
            lang = repo.get("language")
            if lang: langs[lang] = langs.get(lang, 0) + 1
        sorted_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)[:4]
    except: sorted_langs = [("None", 0)]

    ascii_text = """
+-------------------------------------------------------+
| git-statvg_gen // TECH_STACK_DISTRIBUTION             |
+-------------------------------------------------------+
|                                                       |
|  ANALYZING REPOSITORY DATA...                         |
|                                                       |"""
    for lang, count in sorted_langs:
        bar = "=" * min(count * 2, 20)
        ascii_text += f"\n|  > {lang.ljust(12)} [{bar.ljust(20)}] {count} Repos |"

    ascii_text += "\n|                                                       |\n+-------------------------------------------------------+"
    return generate_svg_response(ascii_text, height=280)

def contribution_terminal():
    user = "AhmedXMujtaba"
    token = os.environ.get("GITHUB_TOKEN")
    query = """
    query($userName:String!) {
      user(login: $userName) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                contributionCount
              }
            }
          }
        }
      }
    }
    """
    try:
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"userName": user}},
            headers={"Authorization": f"Bearer {token}"}
        )
        data = response.json()
        all_weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
        weekly_counts = [sum(day['contributionCount'] for day in week['contributionDays']) for week in all_weeks[-26:]]
        max_val = max(weekly_counts) if max(weekly_counts) > 0 else 1
        total_commits = sum(weekly_counts)
    except:
        weekly_counts = [0] * 26
        max_val = 1
        total_commits = 0

    ROWS = 8

    heights = [0 if c == 0 else max(1, round((c / max_val) * ROWS)) for c in weekly_counts]

    def get_char(col, row):
        h = heights[col]
        row_from_bottom = ROWS - 1 - row
        if row_from_bottom < h:
            ratio = h / ROWS
            if ratio > 0.85: return '\u2588'  # █
            if ratio > 0.6:  return '\u2593'  # ▓
            if ratio > 0.35: return '\u2592'  # ▒
            return '\u2591'                    # ░
        return ' '

    chart_rows = []
    for r in range(ROWS):
        row_from_bottom = ROWS - 1 - r
        if row_from_bottom == ROWS - 1:
            label = str(max_val).rjust(3)
        elif row_from_bottom == ROWS // 2:
            label = str(max_val // 2).rjust(3)
        elif row_from_bottom == 0:
            label = "  0"
        else:
            label = "   "
        row_str = label + " |" + "".join(get_char(c, r) for c in range(len(weekly_counts))) + "|"
        chart_rows.append(row_str)

    x_axis   = "     +" + "-" * len(weekly_counts) + "+"
    x_labels = "     -26W" + " " * 7 + "-13W" + " " * 6 + "NOW"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "+-------------------------------------------------------+",
        "| git-statvg_gen // CONTRIBUTION_VOLATILITY             |",
        "+-------------------------------------------------------+",
        "|                                                       |",
        "|  6-MONTH ACTIVITY (T-26 WEEKS):                       |",
        "|                                                       |",
        *["|  " + row.ljust(53) + "|" for row in chart_rows],
        "|  " + x_axis.ljust(53) + "|",
        "|  " + x_labels.ljust(53) + "|",
        "|                                                       |",
        f"|  PEAK_WEEKLY: {str(max_val).ljust(10)} TOTAL_6M: {str(total_commits).ljust(16)}|",
        "|  STATUS: ARCHIVAL_SYNC_COMPLETE                       |",
        f"|  LAST_UPDATED: {now.ljust(38)}|",
        "+-------------------------------------------------------+",
    ]

    ascii_text = "\n" + "\n".join(lines)
    height = len(lines) * 16 + 60
    return generate_svg_response(ascii_text, height=height)

def traffic_terminal():
    user = "AhmedXMujtaba"
    count = "---"
    try:
        r = requests.get(f"https://visitcount.itsvg.in/api?id={user}", timeout=5)
        if r.status_code == 200:
            numbers = re.findall(r'\d+', r.text)
            if numbers:
                count = "".join(numbers)
    except:
        count = "OFFLINE"

    ascii_text = f"""
+-------------------------------------------------------+
| git-statvg_gen // TRAFFIC_ANALYSIS                    |
+-------------------------------------------------------+
|                                                       |
|  UPLINK:   GITHUB_PROXY                               |
|  SESSION:  ACTIVE                                     |
|                                                       |
|  VISITS:   {count.ljust(41)} |
|                                                       |
|  MONITORING INCOMING PACKETS...                       |
+-------------------------------------------------------+"""
    return generate_svg_response(ascii_text, height=280)