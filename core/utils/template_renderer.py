"""
Template rendering utilities
"""

import re
import datetime
from pathlib import Path
from typing import List, Dict, Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
import markdown

from core.blog.content import Post, Page
from core.blog.metadata import MetadataGenerator


class TemplateRenderer:
    """Handles Jinja2 template rendering"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.asset_manifest = {}
        self.metadata_generator = MetadataGenerator(config)
        self.jinja_env = self._setup_jinja()

    def _setup_jinja(self) -> Environment:
        """Setup Jinja2 environment"""
        env = Environment(
            loader=FileSystemLoader(self.config["build"]["template_dir"]),
            autoescape=select_autoescape(["html", "xml"]),
        )

        # Add custom filters
        env.filters["markdown"] = lambda text: markdown.markdown(text)
        env.filters["excerpt"] = (
            lambda text, length=200: text[:length] + "..."
            if len(text) > length
            else text
        )
        env.filters["asset"] = self._asset_url
        env.filters["image"] = self._image_url

        return env

    def set_asset_manifest(self, manifest: Dict[str, str]):
        """Set the asset manifest"""
        self.asset_manifest = manifest

    def _asset_url(self, path: str) -> str:
        """Get the actual asset URL from manifest"""
        # Remove leading slash if present
        path = path.lstrip("/")

        # Check if path is in manifest
        if path in self.asset_manifest:
            return f"/_sync/{self.asset_manifest[path]}"

        # Fallback to original path
        return f"/_sync/{path}"

    def _image_url(self, path: str) -> str:
        """Get the actual image URL from manifest"""
        if not path:
            return ""

        # Remove leading slash and _sync if present
        path = path.lstrip("/")
        if path.startswith("_sync/"):
            path = path[6:]  # Remove "_sync/"

        # If path doesn't start with images/, add it
        if not path.startswith("images/"):
            path = f"images/{path}"

        # Check if path is in manifest
        if path in self.asset_manifest:
            return f"/_sync/{self.asset_manifest[path]}"

        # Fallback to original path
        return f"/_sync/{path}"

    def _minify_html(self, html: str) -> str:
        """Minify HTML content"""
        if not self.config.get("assets", {}).get("minify_html", False):
            return html

        # Remove HTML comments (but keep conditional comments)
        html = re.sub(r"<!--(?!\[if).*?-->", "", html, flags=re.DOTALL)

        # Remove extra whitespace between tags
        html = re.sub(r">\s+<", "><", html)

        # Remove leading and trailing whitespace
        html = re.sub(r"^\s+|\s+$", "", html, flags=re.MULTILINE)

        # Replace multiple spaces with single space
        html = re.sub(r" {2,}", " ", html)

        # Handle inline JavaScript minification in script tags
        script_pattern = r"<script(?:[^>]*)>(.*?)</script>"

        def minify_script_content(match):
            script_tag_start = match.group(0).split(">")[0] + ">"
            script_content = match.group(1)
            script_tag_end = "</script>"

            # Only minify if JavaScript minification is enabled
            if self.config.get("assets", {}).get("minify_js", False):
                # Apply JavaScript minification
                minified_js = self._minify_inline_js(script_content)
                return script_tag_start + minified_js + script_tag_end
            else:
                # Keep original content but remove excessive whitespace
                script_content = re.sub(r"\s+", " ", script_content).strip()
                return script_tag_start + script_content + script_tag_end

        flags = re.DOTALL | re.IGNORECASE
        html = re.sub(script_pattern, minify_script_content, html, flags=flags)

        # Remove newlines and tabs
        # (preserve content in pre and style tags only)
        # First, protect content in pre and style tags
        # (but not script, as we handled it above)
        protected_content = {}
        counter = 0

        for tag in ["pre", "style"]:
            pattern = f"<{tag}[^>]*?>.*?</{tag}>"
            matches = re.finditer(pattern, html, re.DOTALL | re.IGNORECASE)
            for match in matches:
                placeholder = f"__PROTECTED_CONTENT_{counter}__"
                protected_content[placeholder] = match.group(0)
                html = html.replace(match.group(0), placeholder)
                counter += 1

        # Now minify the rest
        html = re.sub(r"\n+", "", html)
        html = re.sub(r"\t+", "", html)

        # Restore protected content
        for placeholder, content in protected_content.items():
            html = html.replace(placeholder, content)

        return html.strip()

    def _minify_inline_js(self, js_content: str) -> str:
        """Minify inline JavaScript content"""
        # Remove single-line comments (but keep URLs)
        js_content = re.sub(
            r"(?<!http:)(?<!https:)//.*$", "", js_content, flags=re.MULTILINE
        )
        # Remove multi-line comments
        js_content = re.sub(r"/\*.*?\*/", "", js_content, flags=re.DOTALL)
        # Remove unnecessary whitespace around operators and delimiters
        js_content = re.sub(r"\s*([{}();,:])\s*", r"\1", js_content)
        js_content = re.sub(r"\s*=\s*", "=", js_content)
        js_content = re.sub(r"\s*\|\|\s*", "||", js_content)
        js_content = re.sub(r"\s*&&\s*", "&&", js_content)
        # Remove extra newlines and spaces
        js_content = re.sub(r"\n+", "", js_content)
        js_content = re.sub(r"\s+", " ", js_content)
        return js_content.strip()

    def render_posts(self, posts: List[Post]):
        """Render individual post pages"""
        template = self.jinja_env.get_template("post.html")
        output_base_dir = Path(self.config["build"]["output_dir"])

        for i, post in enumerate(posts):
            # Get previous and next posts for navigation
            prev_post = posts[i - 1] if i > 0 else None
            next_post = posts[i + 1] if i < len(posts) - 1 else None

            html = template.render(
                post=post,
                config=self.config,
                prev_post=prev_post,
                next_post=next_post,
                current_year=datetime.datetime.now().year,
                metadata=self.metadata_generator,
            )

            # Minify HTML if enabled
            html = self._minify_html(html)

            # Create directory structure based on URL
            # URL format: /{category}/{slug}/ or /{slug}/
            if post.category:
                # Create category/slug/ folder
                post_dir = output_base_dir / post.category / post.slug
            else:
                # Create slug/ folder directly
                post_dir = output_base_dir / post.slug

            post_dir.mkdir(parents=True, exist_ok=True)
            output_file = post_dir / "index.html"

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html)

        minify_status = (
            " (minified)"
            if self.config.get("assets", {}).get("minify_html", False)
            else ""
        )
        print(f"Rendered {len(posts)} posts{minify_status}")

    def render_pages(self, pages: List[Page]):
        """Render static pages"""
        template = self.jinja_env.get_template("page.html")
        output_base_dir = Path(self.config["build"]["output_dir"])

        for page in pages:
            current_year = datetime.datetime.now().year
            html = template.render(
                page=page,
                config=self.config,
                current_year=current_year,
                metadata=self.metadata_generator,
            )

            # Minify HTML if enabled
            html = self._minify_html(html)

            # Create directory structure: /{slug}/index.html
            page_dir = output_base_dir / page.slug
            page_dir.mkdir(parents=True, exist_ok=True)
            output_file = page_dir / "index.html"

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html)

        minify_status = (
            " (minified)"
            if self.config.get("assets", {}).get("minify_html", False)
            else ""
        )
        print(f"Rendered {len(pages)} pages{minify_status}")

    def render_index(self, posts: List[Post]):
        """Render index page with paginated posts"""
        template = self.jinja_env.get_template("index.html")
        output_dir = Path(self.config["build"]["output_dir"])
        posts_per_page = self.config["build"].get("posts_per_page", 10)

        # Calculate pagination
        total_posts = len(posts)
        total_pages = (total_posts + posts_per_page - 1) // posts_per_page

        for page_num in range(1, total_pages + 1):
            start_idx = (page_num - 1) * posts_per_page
            end_idx = start_idx + posts_per_page
            page_posts = posts[start_idx:end_idx]

            # Pagination info
            prev_url = f"/page/{page_num - 1}.html" if page_num > 1 else None
            if page_num < total_pages:
                next_url = f"/page/{page_num + 1}.html"
            else:
                next_url = None
            pagination = {
                "current_page": page_num,
                "total_pages": total_pages,
                "prev_url": prev_url,
                "next_url": next_url,
            }

            # Fix URLs for first page
            if page_num == 1:
                pagination["prev_url"] = None
                if total_pages > 1:
                    pagination["next_url"] = "/page/2.html"

            html = template.render(
                posts=page_posts,
                pagination=pagination if total_pages > 1 else None,
                config=self.config,
                current_year=datetime.datetime.now().year,
                metadata=self.metadata_generator,
            )

            # Minify HTML if enabled
            html = self._minify_html(html)

            if page_num == 1:
                # First page is index.html
                output_file = output_dir / "index.html"
            else:
                # Other pages go in /page/ directory
                page_dir = output_dir / "page"
                page_dir.mkdir(exist_ok=True)
                output_file = page_dir / f"{page_num}.html"

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html)

        minify_status = (
            " (minified)"
            if self.config.get("assets", {}).get("minify_html", False)
            else ""
        )
        print(f"Rendered index with {total_pages} page(s){minify_status}")
