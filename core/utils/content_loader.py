"""
Content loading utilities
"""

import datetime
import re
from pathlib import Path
from typing import Any, Dict, List

import frontmatter
import markdown

from core.blog.content import Page, Post


class ContentLoader:
    """Loads and parses markdown content"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def load_posts(self) -> List[Post]:
        """Load and parse blog posts from markdown files"""
        posts = []
        posts_dir = Path(self.config["build"]["input_dir"]) / "posts"

        if not posts_dir.exists():
            print("Posts directory not found, creating it...")
            posts_dir.mkdir(parents=True, exist_ok=True)
            return posts

        for md_file in posts_dir.rglob("*.md"):
            try:
                post_data = frontmatter.load(md_file)

                # Skip drafts unless building drafts
                if not post_data.metadata.get("published", True):
                    continue

                # Extract metadata
                title = post_data.metadata.get("title", md_file.stem)
                date_str = post_data.metadata.get("date")

                # Parse date
                date = self._parse_date(date_str, md_file)

                # Detect category from folder structure
                relative_path = md_file.relative_to(posts_dir)
                category = None
                if len(relative_path.parts) > 1:
                    # File is in a subfolder, use the folder name as category
                    category = relative_path.parts[0]

                # Generate slug and URL
                slug = post_data.metadata.get("slug", self._slugify(title))

                # Create URL structure
                if category:
                    url = f"/{category}/{slug}/"
                else:
                    url = f"/{slug}/"

                # Convert markdown to HTML
                content = markdown.markdown(
                    post_data.content,
                    extensions=["codehilite", "toc", "tables", "fenced_code"],
                )

                # Convert H1 to H2 to avoid multiple H1 tags (SEO best practice)
                content = self._convert_h1_to_h2(content)

                post = Post(
                    title=title,
                    content=content,
                    date=date,
                    url=url,
                    file_path=str(md_file),
                    slug=slug,
                    category=category,
                    author=post_data.metadata.get("author"),
                    description=post_data.metadata.get("description"),
                    image=post_data.metadata.get("image"),
                    published=post_data.metadata.get("published", True),
                )

                posts.append(post)

            except Exception as e:
                print(f"Error processing post {md_file}: {e}")

        # Sort posts by date (newest first)
        posts.sort(key=lambda p: p.date, reverse=True)
        print(f"Loaded {len(posts)} posts")
        return posts

    def load_pages(self) -> List[Page]:
        """Load and parse static pages from markdown files"""
        pages = []
        pages_dir = Path(self.config["build"]["input_dir"]) / "pages"

        if not pages_dir.exists():
            print("Pages directory not found, creating it...")
            pages_dir.mkdir(parents=True, exist_ok=True)
            return pages

        for md_file in pages_dir.glob("*.md"):
            try:
                page_data = frontmatter.load(md_file)

                # Extract metadata
                title = page_data.metadata.get("title", md_file.stem)
                slug = page_data.metadata.get("slug", self._slugify(title))
                url = f"/{slug}/"

                # Convert markdown to HTML
                content = markdown.markdown(
                    page_data.content,
                    extensions=["codehilite", "toc", "tables", "fenced_code"],
                )

                # Convert H1 to H2 to avoid multiple H1 tags (SEO best practice)
                content = self._convert_h1_to_h2(content)

                page = Page(
                    title=title,
                    content=content,
                    url=url,
                    file_path=str(md_file),
                    slug=slug,
                    description=page_data.metadata.get("description"),
                    image=page_data.metadata.get("image"),
                )

                pages.append(page)

            except Exception as e:
                print(f"Error processing page {md_file}: {e}")

        print(f"Loaded {len(pages)} pages")
        return pages

    def _parse_date(self, date_str, md_file: Path) -> datetime.datetime:
        """Parse date from various formats"""
        if isinstance(date_str, str):
            iso_date = date_str.replace("Z", "+00:00")
            date = datetime.datetime.fromisoformat(iso_date)
        elif isinstance(date_str, datetime.date):
            date = datetime.datetime.combine(date_str, datetime.time())
        else:
            # Use file modification time as fallback
            date = datetime.datetime.fromtimestamp(md_file.stat().st_mtime)

        # Ensure timezone info
        if date.tzinfo is None:
            date = date.replace(tzinfo=datetime.timezone.utc)

        return date

    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        text = text.lower()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[-\s]+", "-", text)
        return text.strip("-")

    def _convert_h1_to_h2(self, html_content: str) -> str:
        """convert H1 tags to H2 to avoid multiple H1 tags on page"""
        # replace opening h1 tags with h2
        html_content = re.sub(r"<h1(\s[^>]*)?>", r"<h2\1>", html_content)
        # replace closing h1 tags with h2
        html_content = re.sub(r"</h1>", "</h2>", html_content)
        return html_content
