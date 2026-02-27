#!/usr/bin/env python3
"""
GitHub Trending Projects Fetcher

Fetches currently trending projects from GitHub with descriptions, stars, and forks.
No API key required - uses web scraping.
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def fetch_trending(timeframe="daily", language=None):
    """
    Fetch trending projects from GitHub
    
    Args:
        timeframe: 'daily', 'weekly', or 'monthly'
        language: Optional programming language filter (e.g., 'python', 'javascript')
    
    Returns:
        List of trending project dicts
    """
    base_url = "https://github.com/trending"
    params = []
    if timeframe and timeframe != "daily":
        params.append(f"since={timeframe}")
    if language:
        params.append(f"spoken_language_code={language}")
    
    url = f"{base_url}?{'&'.join(params)}" if params else base_url
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching GitHub trending: {e}", file=sys.stderr)
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("article", class_="Box-row")
    
    trending_projects = []
    
    for article in articles:
        try:
            # Project name and URL
            h2 = article.find("h2", class_="h3 lh-condensed")
            if not h2:
                continue
            
            link = h2.find("a")
            if not link:
                continue
            
            full_name = link.get("href").strip("/")
            name_parts = full_name.split("/")
            owner = name_parts[0] if len(name_parts) > 0 else ""
            repo_name = name_parts[1] if len(name_parts) > 1 else ""
            
            project_url = f"https://github.com{link.get('href')}"
            
            # Description
            description_elem = article.find("p", class_="col-9 color-fg-muted my-1 pr-4")
            description = description_elem.get_text(strip=True) if description_elem else "No description"
            
            # Language
            language_elem = article.find("span", attrs={"itemprop": "programmingLanguage"})
            language_name = language_elem.get_text(strip=True) if language_elem else None
            
            # Stars and forks
            stats = article.find_all("a", class_="Link--muted")
            stars = 0
            forks = 0
            
            for stat in stats:
                stat_text = stat.get_text(strip=True)
                if "star" in stat.get("href", ""):
                    stars = parse_number(stat_text)
                elif "fork" in stat.get("href", ""):
                    forks = parse_number(stat_text)
            
            # Trending info (built today/week/etc)
            trending_info_elem = article.find("span", class_="d-inline-block float-sm-right")
            trending_info = ""
            if trending_info_elem:
                # Find the svg and get the text after it
                text_content = trending_info_elem.get_text(strip=True)
                trending_info = text_content
            
            project = {
                "owner": owner,
                "name": repo_name,
                "full_name": full_name,
                "url": project_url,
                "description": description,
                "language": language_name,
                "stars": stars,
                "forks": forks,
                "trending_info": trending_info,
            }
            
            trending_projects.append(project)
            
        except Exception as e:
            print(f"Error parsing project: {e}", file=sys.stderr)
            continue
    
    return trending_projects


def parse_number(text):
    """Parse number strings like '1.2k' -> 1200, '3.4M' -> 3400000"""
    if not text:
        return 0
    
    text = text.strip().replace(",", "")
    
    try:
        if "k" in text.lower():
            return int(float(text.lower().replace("k", "")) * 1000)
        elif "m" in text.lower():
            return int(float(text.lower().replace("m", "")) * 1000000)
        else:
            return int(text)
    except ValueError:
        return 0


def format_markdown(projects, timeframe="daily"):
    """Format trending projects as Markdown"""
    if not projects:
        return "No trending projects found."
    
    time_map = {
        "daily": "今日",
        "weekly": "本周",
        "monthly": "本月"
    }
    time_label = time_map.get(timeframe, timeframe)
    
    md = f"# 🔥 GitHub Trending - {time_label}\n\n"
    md += f"*更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
    md += f"共 {len(projects)} 个项目\n\n"
    md += "---\n\n"
    
    for i, proj in enumerate(projects, 1):
        md += f"## {i}. [{proj['owner']}/{proj['name']}]({proj['url']})\n\n"
        md += f"**描述**: {proj['description']}\n\n"
        
        if proj['language']:
            md += f"**语言**: {proj['language']}  |  "
        md += f"**Stars**: ⭐ {proj['stars']:,}  |  "
        md += f"**Forks**: 🍴 {proj['forks']:,}\n"
        
        if proj['trending_info']:
            md += f"**趋势**: {proj['trending_info']}\n"
        
        md += "\n---\n\n"
    
    return md


def format_json(projects):
    """Format trending projects as JSON"""
    return json.dumps({
        "updated_at": datetime.now().isoformat(),
        "count": len(projects),
        "projects": projects
    }, indent=2, ensure_ascii=False)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch GitHub trending projects")
    parser.add_argument("--timeframe", "-t", default="daily", 
                        choices=["daily", "weekly", "monthly"],
                        help="Timeframe: daily, weekly, monthly (default: daily)")
    parser.add_argument("--language", "-l", default=None,
                        help="Filter by language (e.g., python, javascript)")
    parser.add_argument("--format", "-f", default="markdown",
                        choices=["markdown", "json"],
                        help="Output format: markdown or json (default: markdown)")
    parser.add_argument("--limit", "-n", type=int, default=None,
                        help="Limit number of results")
    
    args = parser.parse_args()
    
    projects = fetch_trending(timeframe=args.timeframe, language=args.language)
    
    if args.limit:
        projects = projects[:args.limit]
    
    if args.format == "json":
        print(format_json(projects))
    else:
        print(format_markdown(projects, args.timeframe))


if __name__ == "__main__":
    main()
