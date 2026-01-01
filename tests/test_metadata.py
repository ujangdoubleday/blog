import json

import pytest

from core.blog.metadata import MetadataGenerator


@pytest.fixture
def sample_config():
    return {
        "site": {
            "url": "https://example.com",
            "title": "My Blog",
            "description": "A sample blog",
            "language": "en_US",
            "author": "John Doe",
        }
    }


@pytest.fixture
def metadata_generator(sample_config):
    return MetadataGenerator(sample_config)


class TestMetadataGenerator:
    def test_init(self, metadata_generator):
        assert metadata_generator.base_url == "https://example.com"

    def test_generate_opengraph_basic(self, metadata_generator):
        og_data = metadata_generator.generate_opengraph(
            title="Test Post",
            description="Test Description",
            url="https://example.com/post",
        )
        assert og_data["og:type"] == "website"
        assert og_data["og:title"] == "Test Post"
        assert og_data["og:description"] == "Test Description"
        assert og_data["og:url"] == "https://example.com/post"
        assert og_data["og:site_name"] == "My Blog"
        assert "og:image" not in og_data

    def test_generate_opengraph_with_image_absolute(self, metadata_generator):
        og_data = metadata_generator.generate_opengraph(
            title="Post",
            description="Desc",
            url="url",
            image="https://other.com/img.jpg",
        )
        assert og_data["og:image"] == "https://other.com/img.jpg"

    def test_generate_opengraph_with_image_relative(self, metadata_generator):
        og_data = metadata_generator.generate_opengraph(
            title="Post", description="Desc", url="url", image="/img.jpg"
        )
        assert og_data["og:image"] == "https://example.com/img.jpg"

    def test_generate_opengraph_extra_kwargs(self, metadata_generator):
        og_data = metadata_generator.generate_opengraph(
            title="Post", description="Desc", url="url", **{"article:author": "Me"}
        )
        assert og_data["article:author"] == "Me"

    def test_generate_twitter_card(self, metadata_generator):
        card = metadata_generator.generate_twitter_card(
            title="Title", description="Desc"
        )
        assert card["twitter:card"] == "summary_large_image"
        assert card["twitter:title"] == "Title"
        assert "twitter:image" not in card

    def test_generate_twitter_card_with_image(self, metadata_generator):
        card = metadata_generator.generate_twitter_card(
            title="Title", description="Desc", image="/img.jpg"
        )
        assert card["twitter:image"] == "https://example.com/img.jpg"

    def test_generate_schema_blog(self, metadata_generator):
        json_str = metadata_generator.generate_schema_blog()
        schema = json.loads(json_str)
        assert schema["@type"] == "Blog"
        assert schema["name"] == "My Blog"
        assert schema["author"]["name"] == "John Doe"

    def test_generate_schema_blogposting(self, metadata_generator):
        json_str = metadata_generator.generate_schema_blogposting(
            title="Post",
            description="Desc",
            url="https://example.com/post",
            date_published="2023-01-01",
            author="Jane Doe",
            keywords=["tech", "code"],
        )
        schema = json.loads(json_str)
        assert schema["@type"] == "BlogPosting"
        assert schema["headline"] == "Post"
        assert schema["author"]["name"] == "Jane Doe"
        assert schema["keywords"] == "tech, code"

    def test_generate_schema_webpage(self, metadata_generator):
        json_str = metadata_generator.generate_schema_webpage(
            title="Page",
            description="Desc",
            url="https://example.com/page",
            image="/page.jpg",
        )
        schema = json.loads(json_str)
        assert schema["@type"] == "WebPage"
        assert schema["name"] == "Page"
        assert schema["image"]["url"] == "https://example.com/page.jpg"
