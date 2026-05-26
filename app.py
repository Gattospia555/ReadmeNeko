import os
import random
from datetime import datetime
from flask import Flask, request, Response
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# --- FUNZIONI DI RECUPERO DATI ---


def get_advanced_stats(username, token):
    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {token}"}
    query = """
    query($login: String!) {
      user(login: $login) {
        issues { totalCount }
        repositories(first: 100, ownerAffiliations: [OWNER, COLLABORATOR, ORGANIZATION_MEMBER], orderBy: {field: STARGAZERS, direction: DESC}) {
          nodes { stargazerCount }
        }
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks { contributionDays { contributionCount date } }
          }
        }
      }
    }
    """
    variables = {"login": username}
    try:
        response = requests.post(
            url, json={"query": query, "variables": variables}, headers=headers
        )
        if response.status_code == 200 and "errors" not in response.json():
            data = response.json()["data"]["user"]
            stars = sum(
                repo["stargazerCount"] for repo in data["repositories"]["nodes"]
            )
            issues = data["issues"]["totalCount"]
            calendar = data["contributionsCollection"]["contributionCalendar"]
            yearly_contribs = calendar["totalContributions"]

            days = [
                day for week in calendar["weeks"] for day in week["contributionDays"]
            ]
            days.reverse()

            streak = 0
            today_str = datetime.utcnow().strftime("%Y-%m-%d")
            for day in days:
                if day["contributionCount"] > 0:
                    streak += 1
                elif day["date"] != today_str:
                    break
            return {
                "stars": stars,
                "issues": issues,
                "yearly": yearly_contribs,
                "streak": streak,
            }
    except Exception:
        pass
    return {"stars": 0, "issues": 0, "yearly": 0, "streak": 0}


def get_top_languages(username, token):
    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {token}"}
    query = """
    query($login: String!) {
      user(login: $login) {
        repositories(first: 100, ownerAffiliations: [OWNER, COLLABORATOR, ORGANIZATION_MEMBER], isFork: false, orderBy: {field: PUSHED_AT, direction: DESC}) {
          nodes {
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges {
                size
                node {
                  name
                  color
                }
              }
            }
          }
        }
      }
    }
    """
    variables = {"login": username}
    try:
        response = requests.post(
            url, json={"query": query, "variables": variables}, headers=headers
        )
        if response.status_code == 200 and "errors" not in response.json():
            nodes = response.json()["data"]["user"]["repositories"]["nodes"]

            lang_data = {}
            total_size = 0

            for repo in nodes:
                for edge in repo["languages"]["edges"]:
                    name = edge["node"]["name"]
                    color = edge["node"]["color"] or "#cdd6f4"
                    size = edge["size"]

                    if name not in lang_data:
                        lang_data[name] = {"color": color, "size": 0}
                    lang_data[name]["size"] += size
                    total_size += size

            languages = []
            if total_size > 0:
                for name, data in lang_data.items():
                    percent = round((data["size"] / total_size) * 100, 1)
                    languages.append(
                        {"name": name, "color": data["color"], "percent": percent}
                    )

            languages.sort(key=lambda x: x["percent"], reverse=True)
            return languages[:5]
    except Exception:
        pass
    return []


# --- GENERAZIONE SVG (BASE COMUNE) ---


def generate_stars(num_stars=55):
    colors = [
        "#f5c2e7",
        "#89dceb",
        "#cba6f7",
        "#f9e2af",
        "#a6e3a1",
        "#f5e0dc",
        "#fab387",
    ]
    animations = ["drift1", "drift2", "drift3"]
    stars_svg = ""
    for _ in range(num_stars):
        cx = random.randint(10, 470)
        cy = random.randint(10, 230)
        r = round(random.uniform(0.7, 1.9), 1)
        color = random.choice(colors)
        anim_name = random.choice(animations)
        duration = round(random.uniform(3.5, 7.5), 1)
        delay = round(random.uniform(0.0, 5.0), 1)
        stars_svg += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" style="animation: {anim_name} {duration}s infinite ease-in-out {delay}s;" />\n        '
    return stars_svg


def get_base_svg(title):
    stars_elements = generate_stars(55)
    return f"""
        <style>
            @keyframes slideIn {{ from {{ opacity: 0; transform: translateX(-15px); }} to {{ opacity: 1; transform: translateX(0); }} }}
            @keyframes drift1 {{ 0%, 100% {{ transform: translate(0, 0); opacity: 1; }} 50% {{ transform: translate(3px, -4px); opacity: 0.2; }} }}
            @keyframes drift2 {{ 0%, 100% {{ transform: translate(0, 0); opacity: 0.8; }} 50% {{ transform: translate(-3px, 3px); opacity: 0.3; }} }}
            @keyframes drift3 {{ 0%, 100% {{ transform: translate(0, 0); opacity: 1; }} 50% {{ transform: translate(4px, 2px); opacity: 0.1; }} }}
            @keyframes float {{ 0%, 100% {{ transform: translateY(0px) rotate(0deg); }} 50% {{ transform: translateY(-4px) rotate(2deg); }} }}
            .stat-row {{ animation: slideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards; opacity: 0; }}
            .moon-group {{ animation: float 6s infinite ease-in-out; }}
            .glow {{ filter: drop-shadow(0 0 4px var(--gc)); }}
            .text-base {{ font-family: 'Segoe UI', Ubuntu, Arial, sans-serif; fill: #cdd6f4; font-size: 15px; }}
            .text-title {{ font-family: 'Segoe UI', Ubuntu, Arial, sans-serif; fill: #cba6f7; font-size: 24px; font-weight: 800; }}
            .text-bold {{ font-weight: 700; }}
        </style>
        <defs>
            <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#1e1e2e;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#11111b;stop-opacity:1" />
            </linearGradient>
            <radialGradient id="nebula" cx="20%" cy="20%" r="50%" fx="20%" fy="20%">
                <stop offset="0%" style="stop-color:#cba6f7;stop-opacity:0.1" />
                <stop offset="100%" style="stop-color:#cba6f7;stop-opacity:0" />
            </radialGradient>
        </defs>
        <rect width="480" height="240" rx="20" fill="url(#bgGrad)"/>
        <rect width="480" height="240" rx="20" fill="url(#nebula)"/>
        
        <g stroke="#cba6f7" stroke-width="0.5" opacity="0.15">
            <line x1="320" y1="40" x2="350" y2="25" /><line x1="350" y1="25" x2="370" y2="50" /><line x1="370" y1="50" x2="340" y2="70" />
        </g>
        <g id="stars">{stars_elements}</g>
        
        <g transform="translate(390, 50)">
            <g class="moon-group">
                <path d="M 0 -15 A 20 20 0 1 0 32 17 A 25 25 0 1 1 0 -15" fill="#f9e2af" filter="drop-shadow(0 0 5px #f9e2af55)"/>
            </g>
        </g>

        <g transform="translate(35, 55)">
            <g class="stat-row" style="animation-delay:0.1s">
                <g transform="translate(5, -6) scale(0.8)" fill="#f5e0dc">
                    <path d="M-10,2 C-12,-4 -5,-9 0,-9 C5,-9 12,-4 10,2 C7,9 -7,9 -10,2 Z" />
                    <ellipse cx="-12" cy="-10" rx="3.5" ry="5" transform="rotate(-30 -12 -10)" />
                    <ellipse cx="-4" cy="-17" rx="3.5" ry="5" transform="rotate(-10 -4 -17)" />
                    <ellipse cx="4" cy="-17" rx="3.5" ry="5" transform="rotate(10 4 -17)" />
                    <ellipse cx="12" cy="-10" rx="3.5" ry="5" transform="rotate(30 12 -10)" />
                </g>
                <text x="25" y="0" class="text-title">{title}</text>
            </g>
        </g>
        <text x="455" y="25" class="text-base" style="font-size: 10px; font-weight: bold; fill-opacity: 0.2; letter-spacing: 2px;" text-anchor="end">README NEKO</text>
        
        <g transform="translate(415, 185) rotate(-15) scale(0.85)" fill="#f5e0dc" opacity="0.8">
            <path d="M-10,2 C-12,-4 -5,-9 0,-9 C5,-9 12,-4 10,2 C7,9 -7,9 -10,2 Z" />
            <ellipse cx="-12" cy="-10" rx="3.5" ry="5" transform="rotate(-30 -12 -10)" />
            <ellipse cx="-4" cy="-17" rx="3.5" ry="5" transform="rotate(-10 -4 -17)" />
            <ellipse cx="4" cy="-17" rx="3.5" ry="5" transform="rotate(10 4 -17)" />
            <ellipse cx="12" cy="-10" rx="3.5" ry="5" transform="rotate(30 12 -10)" />
        </g>
    """


# --- ROUTE 1: STATISTICHE ---


@app.route("/api")
def get_stats():
    if not GITHUB_TOKEN:
        return "Errore: GITHUB_TOKEN mancante", 500
    username = request.args.get("username")
    if not username:
        return "Errore: Username mancante", 400

    stats = get_advanced_stats(username, GITHUB_TOKEN)
    base_svg = get_base_svg(username)

    svg_template = f"""
    <svg width="480" height="240" viewBox="0 0 480 240" fill="none" xmlns="http://www.w3.org/2000/svg">
        {base_svg}
        <g transform="translate(35, 105)">
            <g class="stat-row" style="animation-delay:0.25s; --gc: #f9e2af">
                <path class="glow" d="M 0 -8 L 2.3 -3.3 L 7.5 -2.5 L 3.8 1.2 L 4.6 6.3 L 0 4 L -4.6 6.3 L -3.8 1.2 L -7.5 -2.5 L -2.3 -3.3 Z" transform="translate(10, -4)" fill="#f9e2af"/>
                <text x="35" y="0" class="text-base">Total Stars:</text>
                <text x="210" y="0" class="text-base text-bold" style="fill: #f9e2af;">{stats['stars']}</text>
            </g>
        </g>
        <g transform="translate(35, 135)">
            <g class="stat-row" style="animation-delay:0.4s; --gc: #a6e3a1">
                <path class="glow" d="M -6 0 A 6 6 0 1 0 6 0 A 6 6 0 1 0 -6 0 M 0 -3 L 0 3 M -3 0 L 3 0" transform="translate(10, -4)" stroke="#a6e3a1" stroke-width="2" fill="none" stroke-linecap="round"/>
                <text x="35" y="0" class="text-base">Contributions (1 yr):</text>
                <text x="210" y="0" class="text-base text-bold" style="fill: #a6e3a1;">{stats['yearly']}</text>
            </g>
        </g>
        <g transform="translate(35, 165)">
            <g class="stat-row" style="animation-delay:0.55s; --gc: #89b4fa">
                <g transform="translate(10, -4)">
                    <circle class="glow" cx="0" cy="0" r="6" stroke="#89b4fa" stroke-width="2" fill="none"/>
                    <circle cx="0" cy="0" r="2" fill="#89b4fa"/>
                </g>
                <text x="35" y="0" class="text-base">Issues Created:</text>
                <text x="210" y="0" class="text-base text-bold" style="fill: #89b4fa;">{stats['issues']}</text>
            </g>
        </g>
        <g transform="translate(35, 195)">
            <g class="stat-row" style="animation-delay:0.7s; --gc: #f38ba8">
                <path class="glow" d="M 0 5 C -4 5 -7 1 -7 -3 C -7 -7 0 -13 0 -13 C 0 -13 7 -7 7 -3 C 7 1 4 5 0 5 Z" transform="translate(10, -4)" fill="#f38ba8"/>
                <text x="35" y="0" class="text-base">Current Streak:</text>
                <text x="210" y="0" class="text-base text-bold" style="fill: #f38ba8;">{stats['streak']} days</text>
            </g>
        </g>
    </svg>
    """
    return Response(
        svg_template,
        mimetype="image/svg+xml",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


# --- ROUTE 2: TOP LANGUAGES ---


@app.route("/api/langs")
def get_langs():
    if not GITHUB_TOKEN:
        return "Errore: GITHUB_TOKEN mancante", 500
    username = request.args.get("username")
    if not username:
        return "Errore: Username mancante", 400

    langs = get_top_languages(username, GITHUB_TOKEN)
    base_svg = get_base_svg("Top Languages")

    bar_segments = ""
    legend_elements = ""
    current_x = 40

    for idx, lang in enumerate(langs):
        segment_width = (lang["percent"] / 100) * 400
        bar_segments += f'<rect x="{current_x}" y="95" width="{segment_width}" height="14" fill="{lang["color"]}" />\n'
        current_x += segment_width

        col = idx % 2
        row = idx // 2
        lx = 45 + (col * 200)
        ly = 145 + (row * 35)
        delay = 0.2 + (idx * 0.15)

        legend_elements += f"""
        <g class="stat-row" style="animation-delay:{delay}s">
            <circle cx="{lx}" cy="{ly - 4}" r="5" fill="{lang['color']}" />
            <text x="{lx + 15}" y="{ly}" class="text-base text-bold" fill="{lang['color']}">{lang['name']}</text>
            <text x="{lx + 105}" y="{ly}" class="text-base" opacity="0.7">{lang['percent']}%</text>
        </g>
        """

    svg_template = f"""
    <svg width="480" height="240" viewBox="0 0 480 240" fill="none" xmlns="http://www.w3.org/2000/svg">
        {base_svg}
        
        <defs>
            <clipPath id="round-corner">
                <rect x="40" y="95" width="400" height="14" rx="7" />
            </clipPath>
        </defs>

        <g class="stat-row" style="animation-delay: 0.15s">
            <rect x="40" y="95" width="400" height="14" rx="7" fill="#313244" />
            <g clip-path="url(#round-corner)">
                {bar_segments}
            </g>
        </g>
        
        {legend_elements}
    </svg>
    """

    return Response(
        svg_template,
        mimetype="image/svg+xml",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


if __name__ == "__main__":
    app.run(debug=True)
