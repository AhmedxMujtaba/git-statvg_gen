from flask import Flask, Response
import requests
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/api')
def generate_terminal():
    user = "AhmedXMujtaba"
    headers = {}
    
    # 1. Use token to prevent 403 Rate Limit crashes
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Default fallbacks
    repos, followers, following, account_age = 0, 0, 0, 0
    
    try:
        user_response = requests.get(f"https://api.github.com/users/{user}", headers=headers)
        user_response.raise_for_status() 
        user_data = user_response.json()
        
        repos = user_data.get("public_repos", 0)
        followers = user_data.get("followers", 0)
        following = user_data.get("following", 0)
        
        created_at = datetime.strptime(user_data.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
        account_age = (datetime.now() - created_at).days
        
    except requests.exceptions.RequestException as e:
        print(f"API Connection Error: {e}")

    # 2. Alignment Logic
    def pad_line(text):
        return text.ljust(53)

    line1 = pad_line(f"  ARCHITECT: {user}")
    line2 = pad_line(f"  STATUS:    LEAD_ARCHITECT")
    line3 = pad_line(f"  > REPOSITORIES: {repos}")
    line4 = pad_line(f"  > FOLLOWERS:    {followers}")
    line5 = pad_line(f"  > FOLLOWING:    {following}")
    line6 = pad_line(f"  > UPTIME:       {account_age} DAYS")
    
    ascii_text = f"""
+-------------------------------------------------------+
| git-statvg_gen // SYSTEM_TELEMETRY                    |
+-------------------------------------------------------+
|                                                       |
|{line1}|
|{line2}|
|                                                       |
|  METRICS:                                             |
|{line3}|
|{line4}|
|{line5}|
|{line6}|
|                                                       |
|  CORE_STABILITY: [=========================] 100%     |
|  UPLINK: ACTIVE                                       |
|                                                       |
+-------------------------------------------------------+
    """

    # 3. Escape XML characters
    escaped_text = ascii_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('+', '&#43;')

    # 4. CRITICAL: The Multiline Loop for GitHub Camo
    tspan_lines = ""
    for i, line in enumerate(escaped_text.strip('\n').split('\n')):
        dy = "0" if i == 0 else "16"
        tspan_lines += f'            <tspan x="20" dy="{dy}">{line}</tspan>\n'

    # 5. SVG Wrapper with Transparent Background (fill="none")
    svg_content = f"""
    <svg width="520" height="340" viewBox="0 0 520 340" xmlns="http://www.w3.org/2000/svg">
        <rect x="5" y="5" width="510" height="330" fill="none" stroke="#30363d" stroke-width="2" rx="10"/>
        <text y="35" font-family="'Courier New', Courier, monospace" font-size="14" fill="#00d4ff">
{tspan_lines}
            <tspan x="20" dy="16" opacity="0.8">_</tspan>
        </text>
    </svg>
    """

    # 6. Public Headers for Camo
    headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
        'Content-Type': 'image/svg+xml',
        'Access-Control-Allow-Origin': '*'
    }
    return Response(svg_content.strip(), status=200, mimetype='image/svg+xml', headers=headers)
if __name__ == '__main__':
    app.run()