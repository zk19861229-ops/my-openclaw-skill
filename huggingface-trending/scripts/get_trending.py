#!/usr/bin/env python3
"""
Hugging Face Trending Models & Datasets Fetcher

Fetches currently trending models and datasets from Hugging Face.
Uses the Hugging Face API (no authentication required for public data).
"""

import requests
import json
import sys
from datetime import datetime
from typing import List, Dict, Optional


# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def fetch_trending_models(limit=20, library=None, task=None) -> List[Dict]:
    """
    Fetch trending models from Hugging Face
    
    Args:
        limit: Number of models to fetch (default: 20)
        library: Filter by library (e.g., 'transformers', 'diffusers', 'peft')
        task: Filter by task (e.g., 'text-generation', 'image-classification')
    
    Returns:
        List of model dicts
    """
    url = "https://huggingface.co/api/models"
    params = {
        "sort": "trendingScore",
        "direction": -1,
        "limit": limit,
    }
    
    if library:
        params["library"] = library
    if task:
        params["pipeline_tag"] = task
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching Hugging Face models: {e}", file=sys.stderr)
        return []
    
    models = response.json()
    
    trending_models = []
    for model in models:
        try:
            model_info = {
                "id": model.get("id", "unknown"),
                "author": model.get("author", "unknown"),
                "name": model.get("modelId", "unknown").split("/")[-1],
                "url": f"https://huggingface.co/{model.get('id', '')}",
                "task": model.get("pipeline_tag", "N/A"),
                "library": model.get("library_name", "N/A"),
                "downloads": model.get("downloads", 0),
                "likes": model.get("likes", 0),
                "trending_score": model.get("trendingScore", 0),
                "last_modified": model.get("lastModified", "N/A"),
                "tags": model.get("tags", [])[:5],  # Limit tags
            }
            trending_models.append(model_info)
        except Exception as e:
            print(f"Error parsing model: {e}", file=sys.stderr)
            continue
    
    return trending_models


def fetch_trending_datasets(limit=20) -> List[Dict]:
    """
    Fetch trending datasets from Hugging Face
    
    Args:
        limit: Number of datasets to fetch (default: 20)
    
    Returns:
        List of dataset dicts
    """
    url = "https://huggingface.co/api/datasets"
    params = {
        "sort": "trendingScore",
        "direction": -1,
        "limit": limit,
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching Hugging Face datasets: {e}", file=sys.stderr)
        return []
    
    datasets = response.json()
    
    trending_datasets = []
    for dataset in datasets:
        try:
            dataset_info = {
                "id": dataset.get("id", "unknown"),
                "author": dataset.get("author", "unknown"),
                "name": dataset.get("id", "unknown").split("/")[-1],
                "url": f"https://huggingface.co/datasets/{dataset.get('id', '')}",
                "downloads": dataset.get("downloads", 0),
                "likes": dataset.get("likes", 0),
                "trending_score": dataset.get("trendingScore", 0),
                "last_modified": dataset.get("lastModified", "N/A"),
                "tags": dataset.get("tags", [])[:5],
            }
            trending_datasets.append(dataset_info)
        except Exception as e:
            print(f"Error parsing dataset: {e}", file=sys.stderr)
            continue
    
    return trending_datasets


def fetch_trending_spaces(limit=20) -> List[Dict]:
    """
    Fetch trending Spaces from Hugging Face
    
    Args:
        limit: Number of spaces to fetch (default: 20)
    
    Returns:
        List of space dicts
    """
    url = "https://huggingface.co/api/spaces"
    params = {
        "sort": "trendingScore",
        "direction": -1,
        "limit": limit,
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching Hugging Face spaces: {e}", file=sys.stderr)
        return []
    
    spaces = response.json()
    
    trending_spaces = []
    for space in spaces:
        try:
            space_info = {
                "id": space.get("id", "unknown"),
                "author": space.get("author", "unknown"),
                "name": space.get("id", "unknown").split("/")[-1],
                "url": f"https://huggingface.co/spaces/{space.get('id', '')}",
                "sdk": space.get("sdk", "N/A"),
                "likes": space.get("likes", 0),
                "trending_score": space.get("trendingScore", 0),
                "last_modified": space.get("lastModified", "N/A"),
                "tags": space.get("tags", [])[:5],
            }
            trending_spaces.append(space_info)
        except Exception as e:
            print(f"Error parsing space: {e}", file=sys.stderr)
            continue
    
    return trending_spaces


def format_markdown(models=None, datasets=None, spaces=None) -> str:
    """Format trending items as Markdown"""
    md = "# 🤗 Hugging Face Trending - 今日热点\n\n"
    md += f"*更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
    
    # Models section
    if models:
        md += f"## 🔥 热门模型 (Top {len(models)})\n\n"
        md += "| # | 模型 | 任务 | 库 | 👍 Likes | 📥 下载 | 🔥 Trending |\n"
        md += "|---|------|------|-----|---------|--------|-------------|\n"
        
        for i, model in enumerate(models, 1):
            task = model['task'] if model['task'] else 'N/A'
            library = model['library'] if model['library'] else 'N/A'
            md += f"| {i} | [{model['author']}/{model['name']}]({model['url']}) | {task} | {library} | {model['likes']:,} | {model['downloads']:,} | {model['trending_score']:.1f} |\n"
        
        md += "\n---\n\n"
    
    # Datasets section
    if datasets:
        md += f"## 📊 热门数据集 (Top {len(datasets)})\n\n"
        md += "| # | 数据集 | 👍 Likes | 📥 下载 | 🔥 Trending |\n"
        md += "|---|--------|---------|--------|-------------|\n"
        
        for i, dataset in enumerate(datasets, 1):
            md += f"| {i} | [{dataset['author']}/{dataset['name']}]({dataset['url']}) | {dataset['likes']:,} | {dataset['downloads']:,} | {dataset['trending_score']:.1f} |\n"
        
        md += "\n---\n\n"
    
    # Spaces section
    if spaces:
        md += f"## 🚀 热门 Spaces (Top {len(spaces)})\n\n"
        md += "| # | Space | SDK | 👍 Likes | 🔥 Trending |\n"
        md += "|---|-------|-----|---------|-------------|\n"
        
        for i, space in enumerate(spaces, 1):
            md += f"| {i} | [{space['author']}/{space['name']}]({space['url']}) | {space['sdk']} | {space['likes']:,} | {space['trending_score']:.1f} |\n"
        
        md += "\n---\n\n"
    
    return md


def format_json(models=None, datasets=None, spaces=None) -> str:
    """Format trending items as JSON"""
    return json.dumps({
        "updated_at": datetime.now().isoformat(),
        "models": models or [],
        "datasets": datasets or [],
        "spaces": spaces or []
    }, indent=2, ensure_ascii=False)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch Hugging Face trending items")
    parser.add_argument("--type", "-t", default="all",
                        choices=["models", "datasets", "spaces", "all"],
                        help="Type: models, datasets, spaces, or all (default: all)")
    parser.add_argument("--library", "-l", default=None,
                        help="Filter models by library (e.g., transformers, diffusers)")
    parser.add_argument("--task", default=None,
                        help="Filter models by task (e.g., text-generation)")
    parser.add_argument("--limit", "-n", type=int, default=10,
                        help="Limit number of results per type (default: 10)")
    parser.add_argument("--format", "-f", default="markdown",
                        choices=["markdown", "json"],
                        help="Output format: markdown or json (default: markdown)")
    
    args = parser.parse_args()
    
    models = None
    datasets = None
    spaces = None
    
    if args.type in ["models", "all"]:
        models = fetch_trending_models(limit=args.limit, library=args.library, task=args.task)
    
    if args.type in ["datasets", "all"]:
        datasets = fetch_trending_datasets(limit=args.limit)
    
    if args.type in ["spaces", "all"]:
        spaces = fetch_trending_spaces(limit=args.limit)
    
    if args.format == "json":
        print(format_json(models, datasets, spaces))
    else:
        print(format_markdown(models, datasets, spaces))


if __name__ == "__main__":
    main()
