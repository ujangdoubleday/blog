"""
Tests for content models (Post and Page)
"""

import datetime

from core.blog.content import Post, Page


class TestPost:
    """Test Post model"""

    def test_post_creation(self):
        """Test basic post creation"""
        post = Post(
            title="Test Post",
            content="<p>Test content</p>",
            date=datetime.datetime.now(),
            url="/posts/test-post.html",
            file_path="test.md",
            slug="test-post",
        )

        assert post.title == "Test Post"
        assert post.content == "<p>Test content</p>"
        assert post.url == "/posts/test-post.html"
        assert post.slug == "test-post"
        assert post.published is True  # default value

    def test_post_with_optional_fields(self):
        """Test post with all optional fields"""
        post = Post(
            title="Test Post",
            content="<p>Test content</p>",
            date=datetime.datetime.now(),
            url="/posts/test-post.html",
            file_path="test.md",
            slug="test-post",
            author="Test Author",
            description="Test description",
            excerpt="Test excerpt",
            image="/images/test.jpg",
            tags=["test", "blog"],
            reading_time=5,
            published=False,
        )

        assert post.author == "Test Author"
        assert post.description == "Test description"
        assert post.excerpt == "Test excerpt"
        assert post.image == "/images/test.jpg"
        assert post.tags == ["test", "blog"]
        assert post.reading_time == 5
        assert post.published is False

    def test_post_excerpt_generation(self):
        """Test automatic excerpt generation"""
        long_content = "<p>" + "A" * 250 + "</p><p>More content</p>"
        post = Post(
            title="Test Post",
            content=long_content,
            date=datetime.datetime.now(),
            url="/posts/test-post.html",
            file_path="test.md",
            slug="test-post",
        )

        # Should auto-generate excerpt from content
        assert len(post.excerpt) <= 203  # 200 chars + "..."


class TestPage:
    """Test Page model"""

    def test_page_creation(self):
        """Test basic page creation"""
        page = Page(
            title="Test Page",
            content="<p>Test content</p>",
            url="/pages/test-page.html",
            file_path="test.md",
            slug="test-page",
        )

        assert page.title == "Test Page"
        assert page.content == "<p>Test content</p>"
        assert page.url == "/pages/test-page.html"
        assert page.slug == "test-page"

    def test_page_with_optional_fields(self):
        """Test page with optional fields"""
        page = Page(
            title="Test Page",
            content="<p>Test content</p>",
            url="/pages/test-page.html",
            file_path="test.md",
            slug="test-page",
            description="Test description",
            excerpt="Test excerpt",
            image="/images/test.jpg",
        )

        assert page.description == "Test description"
        assert page.excerpt == "Test excerpt"
        assert page.image == "/images/test.jpg"
