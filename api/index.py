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
    escaped_text = ascii_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('+', '&#43;')
    tspan_lines = ""
    for i, line in enumerate(escaped_text.strip('\n').split('\n')):
        dy = "0" if i == 0 else "16"
        tspan_lines += f'            <tspan x="20" dy="{dy}">{line}</tspan>\n'

    # BORDERLESS FIX: The <rect> is removed here
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

@app.route('/api', defaults={'path': ''})
@app.route('/api/<path:path>')
def router(path):
    if path == 'languages': return language_terminal()
    if path == 'contributions': return contribution_terminal()
    if path == 'traffic': return traffic_terminal()
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
    except:
        weekly_counts = [0] * 26
        max_val = 1

    layers = ["", "", "", "", ""]
    for count in weekly_counts:
        ratio = count / max_val
        height = 0
        if ratio > 0.8: height = 5
        elif ratio > 0.6: height = 4
        elif ratio > 0.4: height = 3
        elif ratio > 0.2: height = 2
        elif ratio > 0: height = 1
        
        for i in range(5):
            layers[i] += " # " if (5 - i) <= height else "   "

    ascii_text = f"""
+-------------------------------------------------------+
| git-statvg_gen // CONTRIBUTION_VOLATILITY             |
+-------------------------------------------------------+
|                                                       |
|  6-MONTH_ACTIVITY_LOG (T-26 WEEKS):                   |
|                                                       |
|  Peak | {layers[0]} |
|       | {layers[1]} |
|  Med  | {layers[2]} |
|       | {layers[3]} |
|  Base | {layers[4]} |
|       +---------------------------------------------  |
|          -6M      -4M      -2M      NOW               |
|                                                       |
|  STATUS: ARCHIVAL_SYNC_COMPLETE                       |
|  PEAK_WEEKLY_COMMITS: {str(max_val).ljust(31)} |
+-------------------------------------------------------+"""
    return generate_svg_response(ascii_text, height=360)

def traffic_terminal():
    user = "AhmedXMujtaba"
    count = "---"
    try:
        r = requests.get(f"https://visitcount.itsvg.in/api?id={user}", timeout=5)
        if r.status_code == 200:
            # Regex extracts ONLY digits from the itsvg SVG response
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
|  THREAT:   NONE                                       |
|                                                       |
|  [||||||||||||||||||||||||||||||||||||||||||||] 100%  |
|                                                       |
|  MONITORING INCOMING PACKETS...                       |
+-------------------------------------------------------+"""
    return generate_svg_response(ascii_text, height=280)