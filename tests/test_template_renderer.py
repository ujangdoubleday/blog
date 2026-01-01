from unittest.mock import MagicMock, mock_open, patch

import pytest

from core.blog.content import Page, Post
from core.utils.template_renderer import TemplateRenderer


@pytest.fixture
def mock_config(tmp_path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    (template_dir / "base.html").write_text(
        "<html><body>{% block content %}{% endblock %}</body></html>"
    )
    (template_dir / "post.html").write_text(
        "{% extends 'base.html' %}{% block content %}{{ post.content }}{% endblock %}"
    )
    (template_dir / "page.html").write_text(
        "{% extends 'base.html' %}{% block content %}{{ page.content }}{% endblock %}"
    )
    (template_dir / "index.html").write_text(
        "{% extends 'base.html' %}{% block content %}Index{% endblock %}"
    )

    return {
        "site": {
            "url": "https://example.com",
            "title": "My Blog",
            "description": "Desc",
            "language": "en",
            "author": "Me",
        },
        "build": {
            "template_dir": str(template_dir),
            "output_dir": str(tmp_path / "output"),
            "posts_per_page": 5,
        },
        "assets": {"minify_html": True, "minify_js": True},
    }


@pytest.fixture
def renderer(mock_config):
    return TemplateRenderer(mock_config)


class TestTemplateRenderer:
    def test_init(self, renderer):
        assert renderer.jinja_env is not None
        assert "markdown" in renderer.jinja_env.filters
        assert "asset" in renderer.jinja_env.filters

    def test_asset_url_no_manifest(self, renderer):
        assert renderer._asset_url("css/style.css") == "/_sync/css/style.css"

    def test_asset_url_with_manifest(self, renderer):
        renderer.set_asset_manifest({"css/style.css": "css/style-hash.css"})
        assert renderer._asset_url("css/style.css") == "/_sync/css/style-hash.css"

    def test_image_url(self, renderer):
        assert renderer._image_url("images/pic.jpg") == "/_sync/images/pic.jpg"
        # Test implicit images prefix
        assert renderer._image_url("pic.jpg") == "/_sync/images/pic.jpg"

    def test_generate_img_tag(self, renderer):
        tag = renderer._generate_img_tag("pic.jpg", alt="Alt text")
        assert 'src="/_sync/images/pic.jpg"' in tag
        assert 'alt="Alt text"' in tag
        assert 'loading="lazy"' in tag

    def test_generate_img_tag_with_dimensions(self, renderer):
        renderer.image_dimensions = {"images/pic.jpg": {"width": 100, "height": 200}}
        tag = renderer._generate_img_tag("pic.jpg")
        assert 'width="100"' in tag
        assert 'height="200"' in tag

    def test_minify_html(self, renderer):
        html = """
        <div>
            <p>  Hello   World  </p>
        </div>
        """
        minified = renderer._minify_html(html)
        assert "> <" not in minified
        assert "Hello World" in minified

    def test_minify_inline_js(self, renderer):
        js = """
        function test() {
            var x = 1;
            // comment
            return x + 1;
        }
        """
        minified = renderer._minify_inline_js(js)
        assert "// comment" not in minified
        assert "var x=1" in minified or "var x = 1" in minified
        # Regex might vary slightly depending on exact implementation details
        # but spaces should be reduced

    @patch("builtins.open", new_callable=mock_open)
    def test_render_posts(self, mock_file, renderer):
        post = MagicMock(spec=Post)
        post.slug = "test-post"
        post.content = "Content"
        post.category = None

        # We need to mock os.makedirs or Path.mkdir to avoid actual FS errors
        # if not using tmp_path for output. But here config uses tmp_path so
        # it's fine to let it try to write if the dir exists.
        # However, we are mocking open, so we should also mock mkdir probably
        # or ensure dir exists
        with patch("pathlib.Path.mkdir"):
            renderer.render_posts([post])

        mock_file.assert_called()

    @patch("builtins.open", new_callable=mock_open)
    def test_render_pages(self, mock_file, renderer):
        page = MagicMock(spec=Page)
        page.slug = "about"
        page.content = "About page"

        with patch("pathlib.Path.mkdir"):
            renderer.render_pages([page])

        mock_file.assert_called()

    @patch("builtins.open", new_callable=mock_open)
    def test_render_category_pages(self, mock_file, renderer):
        post1 = MagicMock(spec=Post)
        post1.category = "tech"
        post1.slug = "post1"
        post2 = MagicMock(spec=Post)
        post2.category = "life"
        post2.slug = "post2"

        with patch("pathlib.Path.mkdir"):
            renderer.render_category_pages([post1, post2])

        # Should create 2 category pages
        # Note: calling open() might also happen for reading templates
        # So we check that we at least wrote 2 files
        write_calls = 0
        for call in mock_file.call_args_list:
            args, kwargs = call
            mode = "r"
            if len(args) > 1:
                mode = args[1]
            elif "mode" in kwargs:
                mode = kwargs["mode"]

            if "w" in mode:
                write_calls += 1

        assert write_calls == 2

    def test_minify_script_with_js_minification(self, renderer):
        html = "<script> var x = 1; // comment </script>"
        minified = renderer._minify_html(html)
        assert "varx=1" in minified.replace(" ", "")

    def test_minify_script_without_js_minification(self, renderer):
        renderer.config["assets"]["minify_js"] = False
        html = "<script> var x = 1; // comment </script>"
        minified = renderer._minify_html(html)
        # Should strip extra whitespace but keep comments maybe?
        # Actually logic is: re.sub(r"\s+", " ", script_content).strip() if minify_js is False
        assert (
            "var x = 1; // comment" in minified
            or "var x = 1; // comment" in minified.replace("  ", " ")
        )
