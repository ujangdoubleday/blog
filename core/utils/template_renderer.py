"""
Template rendering utilities
"""

import datetime
import re
from pathlib import Path
from typing import Any, Dict, List

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

from core.blog.content import Page, Post
from core.blog.metadata import MetadataGenerator


class TemplateRenderer:
    """Handles Jinja2 template rendering"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.asset_manifest = {}
        self.image_dimensions = {}
        self.metadata_generator = MetadataGenerator(config)
        self.jinja_env = self._setup_jinja()

    def _setup_jinja(self) -> Environment:
        """Setup Jinja2 environment"""
        env = Environment(
            loader=FileSystemLoader(self.config["build"]["template_dir"]),
            autoescape=select_autoescape(["html", "xml"]),
        )

        # Add custom filters
        env.filters["markdown"] = lambda text: markdown.markdown(
            text,
            extensions=[
                "markdown.extensions.extra",
                "markdown.extensions.tables",
                "markdown.extensions.fenced_code",
            ],
        )
        env.filters["excerpt"] = lambda text, length=200: (
            text[:length] + "..." if len(text) > length else text
        )
        env.filters["asset"] = self._asset_url
        env.filters["image"] = self._image_url
        env.filters["img_tag"] = self._generate_img_tag

        return env

    def set_asset_manifest(self, manifest: Dict[str, str]):
        """set asset manifest and load image dimensions"""
        import json

        self.asset_manifest = manifest

        # load image dimensions
        dimensions_file = (
            Path(self.config["build"]["output_dir"]) / "_sync" / "image-dimensions.json"
        )
        if dimensions_file.exists():
            with open(dimensions_file, "r", encoding="utf-8") as f:
                self.image_dimensions = json.load(f)

    def _asset_url(self, path: str) -> str:
        """Get the actual asset URL from manifest"""
        path = path.lstrip("/")
        if path in self.asset_manifest:
            return f"/_sync/{self.asset_manifest[path]}"
        return f"/_sync/{path}"

    def _image_url(self, path: str) -> str:
        """Get the actual image URL from manifest"""
        if not path:
            return ""

        path = path.lstrip("/")
        if path.startswith("_sync/"):
            path = path[6:]

        if not path.startswith("images/"):
            path = f"images/{path}"

        if path in self.asset_manifest:
            return f"/_sync/{self.asset_manifest[path]}"

        return f"/_sync/{path}"

    def _generate_img_tag(self, path: str, alt: str = "") -> str:
        """generate complete img tag with SEO attributes"""
        if not path:
            return ""

        img_url = self._image_url(path)
        path = path.lstrip("/")
        if path.startswith("_sync/"):
            path = path[6:]
        if not path.startswith("images/"):
            path = f"images/{path}"

        if path in self.asset_manifest:
            actual_path = self.asset_manifest[path]
        else:
            actual_path = path

        dimensions = self.image_dimensions.get(actual_path, {})
        width = dimensions.get("width", 0)
        height = dimensions.get("height", 0)

        attrs = [f'src="{img_url}"', f'alt="{alt}"']

        if width and height:
            attrs.append(f'width="{width}"')
            attrs.append(f'height="{height}"')

        attrs.append('loading="lazy"')
        attrs.append('decoding="async"')

        return f'<img {" ".join(attrs)}>'

    def _minify_html(self, html: str) -> str:
        """Minify HTML content"""
        if not self.config.get("assets", {}).get("minify_html", False):
            return html

        # FIRST: Protect pre, code, and style content BEFORE any minification
        protected_content = {}
        counter = 0

        for tag in ["pre", "code", "style"]:
            pattern = f"<{tag}[^>]*?>.*?</{tag}>"
            matches = re.finditer(pattern, html, re.DOTALL | re.IGNORECASE)
            for match in matches:
                placeholder = f"__PROTECTED_CONTENT_{counter}__"
                protected_content[placeholder] = match.group(0)
                html = html.replace(match.group(0), placeholder)
                counter += 1

        # THEN: Apply minification
        html = re.sub(r"<!--(?!\[if).*?-->", "", html, flags=re.DOTALL)
        html = re.sub(r">\s+<", "><", html)
        html = re.sub(r"^\s+|\s+$", "", html, flags=re.MULTILINE)
        html = re.sub(r" {2,}", " ", html)

        script_pattern = r"<script(?:[^>]*)>(.*?)</script>"

        def minify_script_content(match):
            script_tag_start = match.group(0).split(">")[0] + ">"
            script_content = match.group(1)
            script_tag_end = "</script>"

            if self.config.get("assets", {}).get("minify_js", False):
                minified_js = self._minify_inline_js(script_content)
                return script_tag_start + minified_js + script_tag_end
            else:
                script_content = re.sub(r"\s+", " ", script_content).strip()
                return script_tag_start + script_content + script_tag_end

        flags = re.DOTALL | re.IGNORECASE
        html = re.sub(script_pattern, minify_script_content, html, flags=flags)

        html = re.sub(r"\n+", "", html)
        html = re.sub(r"\t+", "", html)

        # FINALLY: Restore protected content
        for placeholder, content in protected_content.items():
            html = html.replace(placeholder, content)

        return html.strip()

    def _minify_inline_js(self, js_content: str) -> str:
        """Minify inline JavaScript content"""
        js_content = re.sub(
            r"(?<!http:)(?<!https:)//.*$", "", js_content, flags=re.MULTILINE
        )
        js_content = re.sub(r"/\*.*?\*/", "", js_content, flags=re.DOTALL)
        js_content = re.sub(r"\s*([{}();,:])\s*", r"\1", js_content)
        js_content = re.sub(r"\s*=\s*", "=", js_content)
        js_content = re.sub(r"\s*\|\|\s*", "||", js_content)
        js_content = re.sub(r"\s*&&\s*", "&&", js_content)
        js_content = re.sub(r"\n+", "", js_content)
        js_content = re.sub(r"\s+", " ", js_content)
        return js_content.strip()

    def render_posts(self, posts: List[Post]):
        """Render individual post pages"""
        template = self.jinja_env.get_template("post.html")
        output_base_dir = Path(self.config["build"]["output_dir"])

        for i, post in enumerate(posts):
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

            html = self._minify_html(html)

            if post.category:
                post_dir = output_base_dir / post.category / post.slug
            else:
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

            html = self._minify_html(html)

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

        categories = sorted(set(post.category for post in posts if post.category))

        total_posts = len(posts)
        total_pages = (total_posts + posts_per_page - 1) // posts_per_page

        for page_num in range(1, total_pages + 1):
            start_idx = (page_num - 1) * posts_per_page
            end_idx = start_idx + posts_per_page
            page_posts = posts[start_idx:end_idx]

            # pagination logic
            if page_num == 1:
                prev_url = None
            elif page_num == 2:
                prev_url = "/"
            else:
                prev_url = f"/page/{page_num - 1}/"

            if page_num < total_pages:
                next_url = f"/page/{page_num + 1}/"
            else:
                next_url = None

            pagination = {
                "current_page": page_num,
                "total_pages": total_pages,
                "prev_url": prev_url,
                "next_url": next_url,
            }

            html = template.render(
                posts=page_posts,
                categories=categories,
                pagination=pagination if total_pages > 1 else None,
                config=self.config,
                current_year=datetime.datetime.now().year,
                metadata=self.metadata_generator,
            )

            html = self._minify_html(html)

            if page_num == 1:
                output_file = output_dir / "index.html"
            else:
                page_dir = output_dir / "page" / str(page_num)
                page_dir.mkdir(parents=True, exist_ok=True)
                output_file = page_dir / "index.html"

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html)

        minify_status = (
            " (minified)"
            if self.config.get("assets", {}).get("minify_html", False)
            else ""
        )
        print(f"Rendered index with {total_pages} page(s){minify_status}")

    def render_category_pages(self, posts: List[Post]):
        """Render category pages using index.html template"""
        template = self.jinja_env.get_template("index.html")
        output_dir = Path(self.config["build"]["output_dir"])

        categories = sorted(set(post.category for post in posts if post.category))

        for category in categories:
            category_posts = [p for p in posts if p.category == category]

            temp_config = self.config.copy()
            temp_config["site"] = temp_config["site"].copy()
            temp_config["site"]["title"] = category

            html = template.render(
                posts=category_posts,
                categories=categories,
                pagination=None,
                config=temp_config,
                current_year=datetime.datetime.now().year,
                metadata=self.metadata_generator,
            )

            html = self._minify_html(html)

            category_dir = output_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            output_file = category_dir / "index.html"

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html)

        minify_status = (
            " (minified)"
            if self.config.get("assets", {}).get("minify_html", False)
            else ""
        )
        print(f"Rendered {len(categories)} category page(s){minify_status}")
