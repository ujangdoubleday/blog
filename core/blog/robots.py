"""
robots.txt generation for SEO
"""

from pathlib import Path
from typing import Any, Dict


class RobotsGenerator:
    """handles robots.txt generation"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def generate(self):
        """generate robots.txt file"""
        base_url = self.config["site"]["url"].rstrip("/")
        sitemap_url = f"{base_url}/sitemap.xml"

        robots_content = f"""Sitemap: {sitemap_url}

User-agent: *
Allow: /
"""

        # save robots.txt to output root
        output_file = Path(self.config["build"]["output_dir"]) / "robots.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(robots_content)

        print("Generated robots.txt")
