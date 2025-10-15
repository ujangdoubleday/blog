"""
sitemap generation for SEO
"""

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree

from .content import Post, Page


class SitemapGenerator:
    """handles sitemap.xml generation for SEO"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config["site"]["url"].rstrip("/")

    def generate(self, posts: List[Post], pages: List[Page]):
        """generate sitemap.xml from posts and pages"""
        urlset = Element("urlset")
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

        # add homepage
        self._add_url(
            urlset,
            url=self.base_url + "/",
            lastmod=datetime.now(),
            changefreq="daily",
            priority="1.0",
        )

        # add posts
        for post in posts:
            if post.published:
                self._add_url(
                    urlset,
                    url=self.base_url + post.url,
                    lastmod=post.date,
                    changefreq="weekly",
                    priority="0.8",
                )

        # add pages
        for page in pages:
            self._add_url(
                urlset,
                url=self.base_url + page.url,
                lastmod=datetime.now(),
                changefreq="monthly",
                priority="0.7",
            )

        # save sitemap
        self._save_sitemap(urlset)
        print("Generated sitemap.xml")

    def _add_url(
        self,
        urlset: Element,
        url: str,
        lastmod: datetime,
        changefreq: str,
        priority: str,
    ):
        """add URL entry to sitemap"""
        url_elem = SubElement(urlset, "url")

        loc = SubElement(url_elem, "loc")
        loc.text = url

        lastmod_elem = SubElement(url_elem, "lastmod")
        lastmod_elem.text = lastmod.strftime("%Y-%m-%d")

        changefreq_elem = SubElement(url_elem, "changefreq")
        changefreq_elem.text = changefreq

        priority_elem = SubElement(url_elem, "priority")
        priority_elem.text = priority

    def _save_sitemap(self, urlset: Element):
        """save sitemap to file"""
        output_file = Path(self.config["build"]["output_dir"]) / "sitemap.xml"

        # format XML with indentation
        self._indent(urlset)

        # save with pretty formatting
        tree = ElementTree(urlset)
        tree.write(output_file, encoding="utf-8", xml_declaration=True, method="xml")

    def _indent(self, elem: Element, level: int = 0):
        """add indentation to XML for pretty printing"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self._indent(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
