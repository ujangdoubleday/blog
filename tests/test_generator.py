"""
Tests for BlogGenerator
"""

import pytest
from pathlib import Path

from core.blog.generator import BlogGenerator


class TestBlogGenerator:
    """Test BlogGenerator functionality"""

    def test_generator_init_with_sample_config(self, config_file):
        """Test BlogGenerator initialization with config file"""
        generator = BlogGenerator(str(config_file))

        assert generator.config is not None
        assert generator.config["site"]["title"] == "Test Blog"
        assert generator.posts == []
        assert generator.pages == []

    def test_generator_init_nonexistent_config(self):
        """Test BlogGenerator with nonexistent config file"""
        with pytest.raises(SystemExit):
            BlogGenerator("nonexistent.yaml")

    def test_load_config_valid(self, config_file):
        """Test loading valid config file"""
        generator = BlogGenerator(str(config_file))
        config = generator._load_config(str(config_file))

        assert config["site"]["title"] == "Test Blog"
        assert config["build"]["posts_per_page"] == 10

    def test_build_process(
        self, temp_dir, sample_config, sample_post_content, sample_page_content
    ):
        """Test basic build process"""
        # Setup directory structure
        content_dir = temp_dir / "content"
        posts_dir = content_dir / "posts"
        pages_dir = content_dir / "pages"
        posts_dir.mkdir(parents=True)
        pages_dir.mkdir(parents=True)

        # Create sample content
        (posts_dir / "test-post.md").write_text(sample_post_content)
        (pages_dir / "test-page.md").write_text(sample_page_content)

        # Create templates directory (minimal)
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()
        (templates_dir / "base.html").write_text("<html>{{ content }}</html>")
        (templates_dir / "post.html").write_text(
            "{% extends 'base.html' %}{% block content %}Post{% endblock %}"
        )
        (templates_dir / "page.html").write_text(
            "{% extends 'base.html' %}{% block content %}Page{% endblock %}"
        )
        (templates_dir / "index.html").write_text(
            "{% extends 'base.html' %}{% block content %}Index{% endblock %}"
        )

        # Create static directory
        static_dir = temp_dir / "static"
        static_dir.mkdir()

        # Update config paths
        sample_config["build"]["input_dir"] = str(content_dir)
        sample_config["build"]["output_dir"] = str(temp_dir / "output")
        sample_config["build"]["template_dir"] = str(templates_dir)
        sample_config["build"]["static_dir"] = str(static_dir)

        # Create config file
        config_file = temp_dir / "config.yaml"
        import yaml

        with open(config_file, "w") as f:
            yaml.dump(sample_config, f)

        # Test build
        generator = BlogGenerator(str(config_file))
        generator.build(clean=True)

        # Check that content was loaded
        assert len(generator.posts) == 1
        assert len(generator.pages) == 1

        # Check that output directory was created
        output_dir = Path(sample_config["build"]["output_dir"])
        assert output_dir.exists()
        assert (output_dir / "index.html").exists()
