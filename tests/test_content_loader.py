"""
Tests for ContentLoader
"""

from unittest.mock import patch

from core.utils.content_loader import ContentLoader


class TestContentLoader:
    """Test ContentLoader functionality"""

    def test_content_loader_init(self, sample_config):
        """Test ContentLoader initialization"""
        loader = ContentLoader(sample_config)
        assert loader.config == sample_config

    def test_load_posts_empty_directory(self, temp_dir, sample_config):
        """Test loading posts from empty directory"""
        # Update config to use temp directory
        sample_config["build"]["input_dir"] = str(temp_dir)

        loader = ContentLoader(sample_config)
        posts = loader.load_posts()

        assert posts == []

    def test_load_posts_with_content(
        self, temp_dir, sample_config, sample_post_content
    ):
        """Test loading posts with actual content"""
        # Create posts directory and sample post
        posts_dir = temp_dir / "posts"
        posts_dir.mkdir()

        post_file = posts_dir / "test-post.md"
        post_file.write_text(sample_post_content)

        # Update config to use temp directory
        sample_config["build"]["input_dir"] = str(temp_dir)

        loader = ContentLoader(sample_config)
        posts = loader.load_posts()

        assert len(posts) == 1
        post = posts[0]
        assert post.title == "Test Post"
        assert post.author == "Test Author"
        assert post.published is True

    def test_load_pages_empty_directory(self, temp_dir, sample_config):
        """Test loading pages from empty directory"""
        sample_config["build"]["input_dir"] = str(temp_dir)

        loader = ContentLoader(sample_config)
        pages = loader.load_pages()

        assert pages == []

    def test_load_pages_with_content(
        self, temp_dir, sample_config, sample_page_content
    ):
        """Test loading pages with actual content"""
        # Create pages directory and sample page
        pages_dir = temp_dir / "pages"
        pages_dir.mkdir()

        page_file = pages_dir / "test-page.md"
        page_file.write_text(sample_page_content)

        # Update config to use temp directory
        sample_config["build"]["input_dir"] = str(temp_dir)

        loader = ContentLoader(sample_config)
        pages = loader.load_pages()

        assert len(pages) == 1
        page = pages[0]
        assert page.title == "Test Page"
        assert page.slug == "test-page"

    def test_slugify(self, sample_config):
        """Test slugify function"""
        loader = ContentLoader(sample_config)

        assert loader._slugify("Hello World") == "hello-world"
        assert loader._slugify("Test Post!!!") == "test-post"
        assert loader._slugify("Multiple   Spaces") == "multiple-spaces"
        assert loader._slugify("Multiple   Spaces") == "multiple-spaces"
        assert loader._slugify("Special-Characters@#$") == "special-characters"

    @patch("pathlib.Path.rglob", side_effect=Exception("Read error"))
    def test_load_posts_error(self, mock_rglob, temp_dir, sample_config):
        """Test error handling when loading posts"""
        sample_config["build"]["input_dir"] = str(temp_dir)
        loader = ContentLoader(sample_config)
        posts = loader.load_posts()
        assert posts == []

    def test_load_file_error(self, temp_dir, sample_config):
        """Test error handling when reading a file"""
        sample_config["build"]["input_dir"] = str(temp_dir)
        loader = ContentLoader(sample_config)

        # Create a directory but simulate read error by not creating the file content properly
        # or better, mock open to fail
        posts_dir = temp_dir / "posts"
        posts_dir.mkdir()
        (posts_dir / "bad.md").touch()

        with patch("builtins.open", side_effect=Exception("File read error")):
            posts = loader.load_posts()

        assert posts == []
