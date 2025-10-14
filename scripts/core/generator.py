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
from utils.content_loader import ContentLoader
from utils.template_renderer import TemplateRenderer


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
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
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
        self.template_renderer.render_posts(self.posts)
        self.template_renderer.render_pages(self.pages)
        self.template_renderer.render_index(self.posts)
    
    def process_assets(self):
        """Process all static assets"""
        self.asset_processor.process_all()
    
    def generate_feeds(self):
        """Generate RSS feed and search index"""
        self.rss_generator.generate(self.posts)
        self.search_indexer.generate(self.posts, self.pages)
    
    def clean_output(self):
        """Clean the output directory"""
        output_dir = Path(self.config['build']['output_dir'])
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Cleaned output directory: {output_dir}")
    
    def build(self, clean: bool = True):
        """Build the entire site"""
        print("Starting blog build...")
        
        if clean:
            self.clean_output()
        
        # Load content
        self.load_content()
        
        # Render templates
        self.render_templates()
        
        # Process assets
        self.process_assets()
        
        # Generate additional files
        self.generate_feeds()
        
        print("Build complete!")
