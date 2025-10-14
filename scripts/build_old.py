#!/usr/bin/env python3
"""
Static Blog Generator
A simple Python-based static site generator for blogs
"""

import os
import sys
import shutil
import datetime
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import argparse

import yaml
import markdown
import frontmatter
from jinja2 import Environment, FileSystemLoader, select_autoescape
import sass
from feedgen.feed import FeedGenerator
from PIL import Image


@dataclass
class Post:
    """Represents a blog post"""
    title: str
    content: str
    date: datetime.datetime
    url: str
    file_path: str
    slug: str
    author: Optional[str] = None
    description: Optional[str] = None
    excerpt: Optional[str] = None
    image: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    reading_time: Optional[int] = None
    published: bool = True
    
    def __post_init__(self):
        if not self.excerpt and self.content:
            # Extract first paragraph as excerpt
            paragraphs = re.split(r'\n\s*\n', self.content)
            if paragraphs:
                self.excerpt = paragraphs[0][:200] + '...' if len(paragraphs[0]) > 200 else paragraphs[0]
        
        if not self.reading_time and self.content:
            # Estimate reading time (average 200 words per minute)
            word_count = len(self.content.split())
            self.reading_time = max(1, round(word_count / 200))


@dataclass 
class Page:
    """Represents a static page"""
    title: str
    content: str
    url: str
    file_path: str
    slug: str
    description: Optional[str] = None
    excerpt: Optional[str] = None
    image: Optional[str] = None


class BlogGenerator:
    """Main blog generator class"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self.load_config(config_path)
        self.posts: List[Post] = []
        self.pages: List[Page] = []
        self.jinja_env = self.setup_jinja()
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
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
    
    def setup_jinja(self) -> Environment:
        """Setup Jinja2 environment"""
        env = Environment(
            loader=FileSystemLoader(self.config['build']['template_dir']),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Add custom filters
        env.filters['markdown'] = lambda text: markdown.markdown(text)
        env.filters['excerpt'] = lambda text, length=200: text[:length] + '...' if len(text) > length else text
        
        return env
    
    def load_posts(self):
        """Load and parse blog posts from markdown files"""
        posts_dir = Path(self.config['build']['input_dir']) / 'posts'
        
        if not posts_dir.exists():
            print("Posts directory not found, creating it...")
            posts_dir.mkdir(parents=True, exist_ok=True)
            return
        
        for md_file in posts_dir.glob('*.md'):
            try:
                post_data = frontmatter.load(md_file)
                
                # Skip drafts unless building drafts
                if not post_data.metadata.get('published', True):
                    continue
                
                # Extract metadata
                title = post_data.metadata.get('title', md_file.stem)
                date_str = post_data.metadata.get('date')
                
                if isinstance(date_str, str):
                    date = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                elif isinstance(date_str, datetime.date):
                    date = datetime.datetime.combine(date_str, datetime.time())
                else:
                    # Use file modification time as fallback
                    date = datetime.datetime.fromtimestamp(md_file.stat().st_mtime)
                
                # Ensure timezone info
                if date.tzinfo is None:
                    date = date.replace(tzinfo=datetime.timezone.utc)
                
                # Generate slug and URL
                slug = post_data.metadata.get('slug', self.slugify(title))
                url = f"/posts/{slug}.html"
                
                # Convert markdown to HTML
                content = markdown.markdown(
                    post_data.content,
                    extensions=['codehilite', 'toc', 'tables', 'fenced_code']
                )
                
                post = Post(
                    title=title,
                    content=content,
                    date=date,
                    url=url,
                    file_path=str(md_file),
                    slug=slug,
                    author=post_data.metadata.get('author'),
                    description=post_data.metadata.get('description'),
                    image=post_data.metadata.get('image'),
                    tags=post_data.metadata.get('tags', []),
                    published=post_data.metadata.get('published', True)
                )
                
                self.posts.append(post)
                
            except Exception as e:
                print(f"Error processing post {md_file}: {e}")
        
        # Sort posts by date (newest first)
        self.posts.sort(key=lambda p: p.date, reverse=True)
        print(f"Loaded {len(self.posts)} posts")
    
    def load_pages(self):
        """Load and parse static pages from markdown files"""
        pages_dir = Path(self.config['build']['input_dir']) / 'pages'
        
        if not pages_dir.exists():
            print("Pages directory not found, creating it...")
            pages_dir.mkdir(parents=True, exist_ok=True)
            return
        
        for md_file in pages_dir.glob('*.md'):
            try:
                page_data = frontmatter.load(md_file)
                
                # Extract metadata
                title = page_data.metadata.get('title', md_file.stem)
                slug = page_data.metadata.get('slug', self.slugify(title))
                url = f"/pages/{slug}.html"
                
                # Convert markdown to HTML
                content = markdown.markdown(
                    page_data.content,
                    extensions=['codehilite', 'toc', 'tables', 'fenced_code']
                )
                
                page = Page(
                    title=title,
                    content=content,
                    url=url,
                    file_path=str(md_file),
                    slug=slug,
                    description=page_data.metadata.get('description'),
                    image=page_data.metadata.get('image')
                )
                
                self.pages.append(page)
                
            except Exception as e:
                print(f"Error processing page {md_file}: {e}")
        
        print(f"Loaded {len(self.pages)} pages")
    
    def slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')
    
    def render_posts(self):
        """Render individual post pages"""
        template = self.jinja_env.get_template('post.html')
        output_dir = Path(self.config['build']['output_dir']) / 'posts'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, post in enumerate(self.posts):
            # Get previous and next posts for navigation
            prev_post = self.posts[i - 1] if i > 0 else None
            next_post = self.posts[i + 1] if i < len(self.posts) - 1 else None
            
            html = template.render(
                post=post,
                config=self.config,
                prev_post=prev_post,
                next_post=next_post,
                current_year=datetime.datetime.now().year
            )
            
            output_file = output_dir / f"{post.slug}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
        
        print(f"Rendered {len(self.posts)} posts")
    
    def render_pages(self):
        """Render static pages"""
        template = self.jinja_env.get_template('page.html')
        output_dir = Path(self.config['build']['output_dir']) / 'pages'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for page in self.pages:
            html = template.render(
                page=page,
                config=self.config,
                current_year=datetime.datetime.now().year
            )
            
            output_file = output_dir / f"{page.slug}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
        
        print(f"Rendered {len(self.pages)} pages")
    
    def render_index(self):
        """Render index page with paginated posts"""
        template = self.jinja_env.get_template('index.html')
        output_dir = Path(self.config['build']['output_dir'])
        posts_per_page = self.config['build'].get('posts_per_page', 10)
        
        # Calculate pagination
        total_posts = len(self.posts)
        total_pages = (total_posts + posts_per_page - 1) // posts_per_page
        
        for page_num in range(1, total_pages + 1):
            start_idx = (page_num - 1) * posts_per_page
            end_idx = start_idx + posts_per_page
            page_posts = self.posts[start_idx:end_idx]
            
            # Pagination info
            pagination = {
                'current_page': page_num,
                'total_pages': total_pages,
                'prev_url': f"/page/{page_num - 1}.html" if page_num > 1 else None,
                'next_url': f"/page/{page_num + 1}.html" if page_num < total_pages else None
            }
            
            # Fix URLs for first page
            if page_num == 1:
                pagination['prev_url'] = None
                if total_pages > 1:
                    pagination['next_url'] = "/page/2.html"
            
            html = template.render(
                posts=page_posts,
                pagination=pagination if total_pages > 1 else None,
                config=self.config,
                current_year=datetime.datetime.now().year
            )
            
            if page_num == 1:
                # First page is index.html
                output_file = output_dir / 'index.html'
            else:
                # Other pages go in /page/ directory
                page_dir = output_dir / 'page'
                page_dir.mkdir(exist_ok=True)
                output_file = page_dir / f"{page_num}.html"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
        
        print(f"Rendered index with {total_pages} page(s)")
    
    def process_assets(self):
        """Process and copy static assets"""
        static_dir = Path(self.config['build']['static_dir'])
        output_assets = Path(self.config['build']['output_dir']) / '_sync'
        
        # Create output directories
        (output_assets / 'css').mkdir(parents=True, exist_ok=True)
        (output_assets / 'js').mkdir(parents=True, exist_ok=True)
        (output_assets / 'images').mkdir(parents=True, exist_ok=True)
        
        # Process SCSS
        scss_file = static_dir / 'scss' / 'main.scss'
        if scss_file.exists():
            try:
                css_content = sass.compile(filename=str(scss_file))
                
                # Minify CSS if configured
                if self.config.get('assets', {}).get('minify_css', False):
                    css_content = self.minify_css(css_content)
                
                css_output = output_assets / 'css' / 'main.css'
                with open(css_output, 'w', encoding='utf-8') as f:
                    f.write(css_content)
                
                print("Compiled SCSS to CSS")
            except Exception as e:
                print(f"Error compiling SCSS: {e}")
        
        # Copy JavaScript
        js_file = static_dir / 'js' / 'main.js'
        if js_file.exists():
            js_content = js_file.read_text(encoding='utf-8')
            
            # Minify JS if configured
            if self.config.get('assets', {}).get('minify_js', False):
                js_content = self.minify_js(js_content)
            
            js_output = output_assets / 'js' / 'main.js'
            with open(js_output, 'w', encoding='utf-8') as f:
                f.write(js_content)
            
            print("Copied JavaScript")
        
        # Copy and process images
        images_dir = static_dir / 'images'
        if images_dir.exists():
            for img_file in images_dir.rglob('*'):
                if img_file.is_file() and img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
                    relative_path = img_file.relative_to(images_dir)
                    output_img = output_assets / 'images' / relative_path
                    output_img.parent.mkdir(parents=True, exist_ok=True)
                    
                    if self.config.get('assets', {}).get('optimize_images', True) and img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                        self.optimize_image(img_file, output_img)
                    else:
                        shutil.copy2(img_file, output_img)
            
            print("Processed images")
        
        # Copy template static files
        template_static = Path(self.config['build']['template_dir']) / 'static'
        if template_static.exists():
            for static_file in template_static.rglob('*'):
                if static_file.is_file():
                    relative_path = static_file.relative_to(template_static)
                    output_file = output_assets / relative_path
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(static_file, output_file)
            
            print("Copied template static files")
    
    def optimize_image(self, input_path: Path, output_path: Path):
        """Optimize image for web"""
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Optimize and save
                quality = self.config.get('assets', {}).get('image_quality', 85)
                img.save(output_path, optimize=True, quality=quality)
        except Exception as e:
            print(f"Error optimizing image {input_path}: {e}")
            shutil.copy2(input_path, output_path)
    
    def minify_css(self, css_content: str) -> str:
        """Basic CSS minification"""
        # Remove comments
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        # Remove extra whitespace
        css_content = re.sub(r'\s+', ' ', css_content)
        # Remove spaces around certain characters
        css_content = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css_content)
        return css_content.strip()
    
    def minify_js(self, js_content: str) -> str:
        """Basic JavaScript minification"""
        # Remove single-line comments
        js_content = re.sub(r'//.*$', '', js_content, flags=re.MULTILINE)
        # Remove multi-line comments
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        # Remove extra whitespace (basic)
        js_content = re.sub(r'\s+', ' ', js_content)
        return js_content.strip()
    
    def generate_rss(self):
        """Generate RSS feed"""
        if not self.config.get('rss', {}).get('enabled', True):
            return
        
        fg = FeedGenerator()
        fg.title(self.config['rss'].get('title', self.config['site']['title']))
        fg.link(href=self.config['site']['url'], rel='alternate')
        fg.description(self.config['rss'].get('description', self.config['site']['description']))
        fg.language(self.config['site'].get('language', 'en'))
        fg.author(name=self.config['site']['author'], email=self.config['site'].get('email'))
        
        # Add posts to feed
        max_items = self.config['rss'].get('max_items', 20)
        for post in self.posts[:max_items]:
            fe = fg.add_entry()
            fe.title(post.title)
            fe.link(href=f"{self.config['site']['url']}{post.url}")
            fe.description(post.excerpt or post.content[:500])
            fe.author(name=post.author or self.config['site']['author'])
            fe.pubDate(post.date)
            fe.guid(f"{self.config['site']['url']}{post.url}")
        
        # Save RSS feed
        output_file = Path(self.config['build']['output_dir']) / 'rss.xml'
        with open(output_file, 'wb') as f:
            f.write(fg.rss_str(pretty=True))
        
        print("Generated RSS feed")
    
    def generate_search_index(self):
        """Generate search index JSON"""
        search_data = []
        
        for post in self.posts:
            search_data.append({
                'title': post.title,
                'url': post.url,
                'content': post.content,
                'excerpt': post.excerpt,
                'date': post.date.strftime('%Y-%m-%d'),
                'tags': post.tags
            })
        
        for page in self.pages:
            search_data.append({
                'title': page.title,
                'url': page.url,
                'content': page.content,
                'excerpt': page.excerpt,
                'date': '',
                'tags': []
            })
        
        output_file = Path(self.config['build']['output_dir']) / 'search.json'
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(search_data, f, ensure_ascii=False, indent=2)
        
        print("Generated search index")
    
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
        self.load_posts()
        self.load_pages()
        
        # Render templates
        self.render_posts()
        self.render_pages() 
        self.render_index()
        
        # Process assets
        self.process_assets()
        
        # Generate additional files
        self.generate_rss()
        self.generate_search_index()
        
        print("Build complete!")


def main():
    parser = argparse.ArgumentParser(description='Static Blog Generator')
    parser.add_argument('--config', '-c', default='config/config.yaml', help='Config file path')
    parser.add_argument('--no-clean', action='store_true', help='Don\'t clean output directory')
    parser.add_argument('--serve', '-s', action='store_true', help='Serve the site locally after building')
    parser.add_argument('--port', '-p', type=int, default=8000, help='Port for local server')
    
    args = parser.parse_args()
    
    generator = BlogGenerator(args.config)
    generator.build(clean=not args.no_clean)
    
    if args.serve:
        import http.server
        import socketserver
        import webbrowser
        import threading
        
        os.chdir(generator.config['build']['output_dir'])
        
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", args.port), Handler) as httpd:
            print(f"Serving at http://localhost:{args.port}")
            
            # Open browser
            def open_browser():
                import time
                time.sleep(1)
                webbrowser.open(f'http://localhost:{args.port}')
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped.")


if __name__ == '__main__':
    main()
