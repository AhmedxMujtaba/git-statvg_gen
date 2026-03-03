from flask import Flask, Response
import requests
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/api')
def generate_terminal():
    user = "AhmedXMujtaba"
    headers = {}
    
    # 1. Professional Standard: Use token to prevent 403 Rate Limit crashes
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Default fallbacks
    repos, followers, following, account_age = 0, 0, 0, 0
    
    try:
        # Fetch live metrics from the GitHub REST API
        user_response = requests.get(f"https://api.github.com/users/{user}", headers=headers)
        user_response.raise_for_status() # Throws an error if the API is down
        user_data = user_response.json()
        
        repos = user_data.get("public_repos", 0)
        followers = user_data.get("followers", 0)
        following = user_data.get("following", 0)
        
        # Calculate account age for "Uptime"
        created_at = datetime.strptime(user_data.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
        account_age = (datetime.now() - created_at).days
        
    except requests.exceptions.RequestException as e:
        print(f"API Connection Error: {e}")

    # 2. Dynamic Alignment Math: Ensures the right border '|' never breaks
    # The inner width of our ASCII box is exactly 53 characters.
    def pad_line(text):
        return text.ljust(53)

    line1 = pad_line(f"  ARCHITECT: {user}")
    line2 = pad_line(f"  STATUS:    LEAD_ARCHITECT")
    line3 = pad_line(f"  > REPOSITORIES: {repos}")
    line4 = pad_line(f"  > FOLLOWERS:    {followers}")
    line5 = pad_line(f"  > FOLLOWING:    {following}")
    line6 = pad_line(f"  > UPTIME:       {account_age} DAYS")
    
    # The ASCII terminal design
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

    # 3. SVG Wrapper with Neon Glow, SVG Borders, and Blinking Cursor
    svg_content = f"""
    <svg width="520" height="340" viewBox="0 0 520 340" fill="none" xmlns="http://www.w3.org/2000/svg">
        <style>
            .text {{ 
                font: 14px 'Courier New', monospace; 
                fill: #00d4ff; 
                white-space: pre; 
                text-shadow: 0px 0px 4px rgba(0, 212, 255, 0.6);
            }}
            .bg {{ 
                fill: #0d1117; 
                stroke: #30363d; 
                stroke-width: 2; 
            }}
            .cursor {{ animation: blink 1s step-end infinite; }}
            @keyframes blink {{ 50% {{ opacity: 0; }} }}
        </style>
        
        <rect x="5" y="5" width="510" height="330" class="bg" rx="10"/>
        
    <text x="20" y="35" class="text">
            {ascii_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('+', '&#43;')}
            <tspan class="cursor">_</tspan>
        </text>
    </svg>
    """

    # 4. Cache Control: Tells GitHub to only cache this for 30 minutes
    headers = {
        'Cache-Control': 'public, max-age=1800',
        'Content-Type': 'image/svg+xml'
    }
    return Response(svg_content.strip(), mimetype='image/svg+xml', headers=headers)

if __name__ == '__main__':
    app.run()