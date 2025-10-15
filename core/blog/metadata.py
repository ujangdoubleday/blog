"""
metadata generation for HTML head section
handles OpenGraph, Twitter Card, and Schema.org
"""

from typing import Dict, Any, Optional, List
import json


class MetadataGenerator:
    """handles metadata generation for SEO and social media"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config["site"]["url"].rstrip("/")

    def generate_opengraph(
        self,
        title: str,
        description: str,
        url: str,
        og_type: str = "website",
        image: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, str]:
        """generate OpenGraph metadata"""
        og_data = {
            "og:type": og_type,
            "og:title": title,
            "og:description": description,
            "og:url": url,
            "og:site_name": self.config["site"]["title"],
            "og:locale": self.config["site"]["language"],
        }

        if image:
            og_data["og:image"] = (
                f"{self.base_url}{image}" if not image.startswith("http") else image
            )
            og_data["og:image:alt"] = title

        # add article-specific metadata
        for key, value in kwargs.items():
            if value:
                og_data[f"{key}"] = value

        return og_data

    def generate_twitter_card(
        self,
        title: str,
        description: str,
        image: Optional[str] = None,
        card_type: str = "summary_large_image",
    ) -> Dict[str, str]:
        """generate Twitter Card metadata"""
        twitter_data = {
            "twitter:card": card_type,
            "twitter:title": title,
            "twitter:description": description,
        }

        if image:
            twitter_data["twitter:image"] = (
                f"{self.base_url}{image}" if not image.startswith("http") else image
            )

        twitter_site = self.config.get("social", {}).get("twitter")
        if twitter_site:
            twitter_data["twitter:site"] = twitter_site

        return twitter_data

    def generate_schema_blog(self) -> str:
        """generate Schema.org JSON-LD for Blog"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Blog",
            "name": self.config["site"]["title"],
            "description": self.config["site"]["description"],
            "url": f"{self.base_url}/",
            "author": {
                "@type": "Person",
                "name": self.config["site"]["author"],
            },
            "publisher": {
                "@type": "Organization",
                "name": self.config["site"]["title"],
                "url": self.base_url,
            },
        }

        return json.dumps(schema, ensure_ascii=False)

    def generate_schema_blogposting(
        self,
        title: str,
        description: str,
        url: str,
        date_published: str,
        author: str,
        image: Optional[str] = None,
        keywords: Optional[List[str]] = None,
    ) -> str:
        """generate Schema.org JSON-LD for BlogPosting"""
        schema = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": title,
            "description": description,
            "url": url,
            "datePublished": date_published,
            "author": {"@type": "Person", "name": author},
            "publisher": {
                "@type": "Organization",
                "name": self.config["site"]["title"],
                "url": self.base_url,
            },
        }

        if image:
            schema["image"] = {
                "@type": "ImageObject",
                "url": (
                    f"{self.base_url}{image}" if not image.startswith("http") else image
                ),
            }

        if keywords:
            schema["keywords"] = ", ".join(keywords)

        return json.dumps(schema, ensure_ascii=False)

    def generate_schema_webpage(
        self,
        title: str,
        description: str,
        url: str,
        image: Optional[str] = None,
    ) -> str:
        """generate Schema.org JSON-LD for WebPage"""
        schema = {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": title,
            "description": description,
            "url": url,
            "publisher": {
                "@type": "Organization",
                "name": self.config["site"]["title"],
                "url": self.base_url,
            },
        }

        if image:
            schema["image"] = {
                "@type": "ImageObject",
                "url": (
                    f"{self.base_url}{image}" if not image.startswith("http") else image
                ),
            }

        return json.dumps(schema, ensure_ascii=False)
