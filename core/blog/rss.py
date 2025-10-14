"""
RSS feed generation
"""

from pathlib import Path
from typing import List, Dict, Any

from feedgen.feed import FeedGenerator

from .content import Post


class RSSGenerator:
    """Handles RSS feed generation"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def generate(self, posts: List[Post]):
        """Generate RSS feed from posts"""
        if not self.config.get("rss", {}).get("enabled", True):
            return

        fg = FeedGenerator()
        fg.title(self.config["rss"].get("title", self.config["site"]["title"]))
        fg.link(href=self.config["site"]["url"], rel="alternate")
        rss_config = self.config["rss"]
        site_config = self.config["site"]
        description = rss_config.get("description", site_config["description"])
        fg.description(description)
        fg.language(site_config.get("language", "en"))
        fg.author(name=site_config["author"], email=site_config.get("email"))

        # Add posts to feed
        max_items = self.config["rss"].get("max_items", 20)
        for post in posts[:max_items]:
            fe = fg.add_entry()
            fe.title(post.title)
            fe.link(href=f"{self.config['site']['url']}{post.url}")
            fe.description(post.excerpt or post.content[:500])
            fe.author(name=post.author or self.config["site"]["author"])
            fe.pubDate(post.date)
            fe.guid(f"{self.config['site']['url']}{post.url}")

        # Save RSS feed
        output_file = Path(self.config["build"]["output_dir"]) / "rss.xml"
        with open(output_file, "wb") as f:
            f.write(fg.rss_str(pretty=True))

        print("Generated RSS feed")
