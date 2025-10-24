"""
Main blog generator class
"""

import sys
import shutil
from pathlib import Path
from typing import Dict, Any, List

import yaml

from .content import Post, Page
from .assets import AssetProcessor
from .rss import RSSGenerator
from .search import SearchIndexer
from .sitemap import SitemapGenerator
from .robots import RobotsGenerator
from core.utils.content_loader import ContentLoader
from core.utils.template_renderer import TemplateRenderer


class BlogGenerator:
    """Main blog generator class"""

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.posts: List[Post] = []
        self.pages: List[Page] = []

        # Initialize components
        self.content_loader = ContentLoader(self.config)
        self.template_renderer = TemplateRenderer(self.config)
        self.asset_processor = AssetProcessor(self.config)
        self.rss_generator = RSSGenerator(self.config)
        self.search_indexer = SearchIndexer(self.config)
        self.sitemap_generator = SitemapGenerator(self.config)
        self.robots_generator = RobotsGenerator(self.config)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"Config file {config_path} not found!")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing config file: {e}")
            sys.exit(1)

    def load_content(self):
        """Load all content (posts and pages)"""
        self.posts = self.content_loader.load_posts()
        self.pages = self.content_loader.load_pages()

    def render_templates(self):
        """Render all templates"""
        manifest = self.asset_processor.asset_manifest
        self.template_renderer.set_asset_manifest(manifest)

        self.template_renderer.render_posts(self.posts)
        self.template_renderer.render_pages(self.pages)
        self.template_renderer.render_index(self.posts)
        self.template_renderer.render_category_pages(self.posts)

    def process_assets(self):
        """Process all static assets"""
        self.asset_processor.process_all()

    def generate_feeds(self):
        """Generate RSS feed, search index, sitemap, and robots.txt"""
        self.rss_generator.generate(self.posts)
        self.search_indexer.generate(self.posts, self.pages)
        self.sitemap_generator.generate(self.posts, self.pages)
        self.robots_generator.generate()

    def clean_output(self):
        """Clean the output directory"""
        output_dir = Path(self.config["build"]["output_dir"])
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Cleaned output directory: {output_dir}")

    def build(self, clean: bool = True):
        """Build the entire site"""
        print("Starting blog build...")

        if clean:
            self.clean_output()

        self.load_content()
        self.process_assets()
        self.render_templates()
        self.generate_feeds()

        print("Build complete!")
