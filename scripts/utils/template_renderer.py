"""
Template rendering utilities
"""

import re
import datetime
from pathlib import Path
from typing import List, Dict, Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
import markdown

from core.content import Post, Page


class TemplateRenderer:
    """Handles Jinja2 template rendering"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.jinja_env = self._setup_jinja()
    
    def _setup_jinja(self) -> Environment:
        """Setup Jinja2 environment"""
        env = Environment(
            loader=FileSystemLoader(self.config['build']['template_dir']),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Add custom filters
        env.filters['markdown'] = lambda text: markdown.markdown(text)
        env.filters['excerpt'] = lambda text, length=200: text[:length] + '...' if len(text) > length else text
        
        return env
    
    def _minify_html(self, html: str) -> str:
        """Minify HTML content"""
        if not self.config.get('assets', {}).get('minify_html', False):
            return html
        
        # Remove HTML comments (but keep conditional comments)
        html = re.sub(r'<!--(?!\[if).*?-->', '', html, flags=re.DOTALL)
        
        # Remove extra whitespace between tags
        html = re.sub(r'>\s+<', '><', html)
        
        # Remove leading and trailing whitespace
        html = re.sub(r'^\s+|\s+$', '', html, flags=re.MULTILINE)
        
        # Replace multiple spaces with single space
        html = re.sub(r' {2,}', ' ', html)
        
        # Remove newlines and tabs (but preserve content in pre, script, style tags)
        # First, protect content in pre, script, style tags
        protected_content = {}
        counter = 0
        
        for tag in ['pre', 'script', 'style']:
            pattern = f'<{tag}[^>]*?>.*?</{tag}>'
            matches = re.finditer(pattern, html, re.DOTALL | re.IGNORECASE)
            for match in matches:
                placeholder = f'__PROTECTED_CONTENT_{counter}__'
                protected_content[placeholder] = match.group(0)
                html = html.replace(match.group(0), placeholder)
                counter += 1
        
        # Now minify the rest
        html = re.sub(r'\n+', '', html)
        html = re.sub(r'\t+', '', html)
        
        # Restore protected content
        for placeholder, content in protected_content.items():
            html = html.replace(placeholder, content)
        
        return html.strip()
    
    def render_posts(self, posts: List[Post]):
        """Render individual post pages"""
        template = self.jinja_env.get_template('post.html')
        output_dir = Path(self.config['build']['output_dir']) / 'posts'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, post in enumerate(posts):
            # Get previous and next posts for navigation
            prev_post = posts[i - 1] if i > 0 else None
            next_post = posts[i + 1] if i < len(posts) - 1 else None
            
            html = template.render(
                post=post,
                config=self.config,
                prev_post=prev_post,
                next_post=next_post,
                current_year=datetime.datetime.now().year
            )
            
            # Minify HTML if enabled
            html = self._minify_html(html)
            
            output_file = output_dir / f"{post.slug}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
        
        minify_status = " (minified)" if self.config.get('assets', {}).get('minify_html', False) else ""
        print(f"Rendered {len(posts)} posts{minify_status}")
    
    def render_pages(self, pages: List[Page]):
        """Render static pages"""
        template = self.jinja_env.get_template('page.html')
        output_dir = Path(self.config['build']['output_dir']) / 'pages'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for page in pages:
            html = template.render(
                page=page,
                config=self.config,
                current_year=datetime.datetime.now().year
            )
            
            # Minify HTML if enabled
            html = self._minify_html(html)
            
            output_file = output_dir / f"{page.slug}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
        
        minify_status = " (minified)" if self.config.get('assets', {}).get('minify_html', False) else ""
        print(f"Rendered {len(pages)} pages{minify_status}")
    
    def render_index(self, posts: List[Post]):
        """Render index page with paginated posts"""
        template = self.jinja_env.get_template('index.html')
        output_dir = Path(self.config['build']['output_dir'])
        posts_per_page = self.config['build'].get('posts_per_page', 10)
        
        # Calculate pagination
        total_posts = len(posts)
        total_pages = (total_posts + posts_per_page - 1) // posts_per_page
        
        for page_num in range(1, total_pages + 1):
            start_idx = (page_num - 1) * posts_per_page
            end_idx = start_idx + posts_per_page
            page_posts = posts[start_idx:end_idx]
            
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
            
            # Minify HTML if enabled
            html = self._minify_html(html)
            
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
        
        minify_status = " (minified)" if self.config.get('assets', {}).get('minify_html', False) else ""
        print(f"Rendered index with {total_pages} page(s){minify_status}")
