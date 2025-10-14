"""
Content models for blog posts and pages
"""

import re
import datetime
from dataclasses import dataclass, field
from typing import List, Optional


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
            paragraphs = re.split(r"\n\s*\n", self.content)
            if paragraphs:
                self.excerpt = (
                    paragraphs[0][:200] + "..."
                    if len(paragraphs[0]) > 200
                    else paragraphs[0]
                )

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
