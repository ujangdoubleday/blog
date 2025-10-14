"""
Search index generation
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from .content import Post, Page


class SearchIndexer:
    """Handles search index generation"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def generate(self, posts: List[Post], pages: List[Page]):
        """Generate search index JSON"""
        search_data = []

        # Add posts to search index
        for post in posts:
            search_data.append(
                {
                    "title": post.title,
                    "url": post.url,
                    "content": post.content,
                    "excerpt": post.excerpt,
                    "date": post.date.strftime("%Y-%m-%d"),
                    "tags": post.tags,
                    "type": "post",
                }
            )

        # Add pages to search index
        for page in pages:
            search_data.append(
                {
                    "title": page.title,
                    "url": page.url,
                    "content": page.content,
                    "excerpt": page.excerpt,
                    "date": "",
                    "tags": [],
                    "type": "page",
                }
            )

        # Save search index
        output_file = Path(self.config["build"]["output_dir"]) / "search.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(search_data, f, ensure_ascii=False, indent=2)

        print("Generated search index")
