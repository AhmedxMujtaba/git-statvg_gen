from flask import Flask, Response, request
import requests
import os
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

    svg = f"""
    <svg width="520" height="{height}" viewBox="0 0 520 {height}" xmlns="http://www.w3.org/2000/svg">
        <rect x="5" y="5" width="510" height="{height-10}" fill="none" stroke="#30363d" stroke-width="2" rx="10"/>
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

@app.route('/api')
def main_terminal():
    user = "AhmedXMujtaba"
    try:
        r = requests.get(f"https://api.github.com/users/{user}", headers=get_headers())
        data = r.json()
        repos = data.get("public_repos", 0)
        followers = data.get("followers", 0)
        age = (datetime.now() - datetime.strptime(data.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")).days
    except:
        repos, followers, age = 0, 0, 0

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pad = lambda t: t.ljust(53)
    
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

@app.route('/api/languages')
def language_terminal():
    user = "AhmedXMujtaba"
    try:
        r = requests.get(f"https://api.github.com/users/{user}/repos", headers=get_headers())
        repos = r.json()
        langs = {}
        for repo in repos:
            lang = repo.get("language")
            if lang: langs[lang] = langs.get(lang, 0) + 1
        sorted_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)[:4]
    except:
        sorted_langs = [("None", 0)]

    ascii_text = f"""
+-------------------------------------------------------+
| git-statvg_gen // TECH_STACK_DISTRIBUTION             |
+-------------------------------------------------------+
|                                                       |
|  ANALYZING REPOSITORY DATA...                         |
|                                                       |"""
    for lang, count in sorted_langs:
        bar = "=" * (count * 2)
        ascii_text += f"\n|  > {lang.ljust(12)} [{bar.ljust(20)}] {count} Repos |"
    
    ascii_text += """
|                                                       |
+-------------------------------------------------------+"""
    return generate_svg_response(ascii_text, height=280)