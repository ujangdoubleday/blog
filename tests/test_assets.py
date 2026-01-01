from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from core.blog.assets import AssetProcessor


@pytest.fixture
def mock_config(tmp_path):
    return {
        "build": {
            "static_dir": str(tmp_path / "static"),
            "output_dir": str(tmp_path / "output"),
            "template_dir": str(tmp_path / "templates"),
        },
        "assets": {
            "minify_css": True,
            "minify_js": True,
            "use_hash": True,
            "webp_quality": 80,
        },
    }


@pytest.fixture
def asset_processor(mock_config):
    return AssetProcessor(mock_config)


class TestAssetProcessor:
    def test_init(self, asset_processor):
        assert asset_processor.asset_manifest == {}
        assert asset_processor.image_dimensions == {}

    def test_generate_hash(self, asset_processor):
        h1 = asset_processor._generate_hash("content")
        h2 = asset_processor._generate_hash("content")
        assert h1 == h2
        assert len(h1) == 8

    def test_get_hashed_filename(self, asset_processor):
        name = asset_processor._get_hashed_filename("style.css", "content")
        assert "style-" in name
        assert ".css" in name

    def test_get_hashed_filename_no_hash(self, asset_processor):
        asset_processor.config["assets"]["use_hash"] = False
        name = asset_processor._get_hashed_filename("style.css", "content")
        assert name == "style.css"

    def test_minify_css(self, asset_processor):
        css = """
        body {
            color: red;
        }
        /* comment */
        """
        minified = asset_processor._minify_css(css)
        assert "body{color:red;}" in minified or "body{color:red}" in minified.replace(
            " ", ""
        )

    def test_minify_js(self, asset_processor):
        js = """
        var x = 1;
        // comment
        var y = 2;
        """
        minified = asset_processor._minify_js(js)
        assert "// comment" not in minified
        assert "varx=1" in minified.replace(" ", "")

    @patch("sass.compile")
    @patch("builtins.open", new_callable=mock_open)
    def test_process_scss(self, mock_file, mock_sass, asset_processor):
        mock_sass.return_value = "body { color: red; }"
        # Mocking existence of scss file
        with patch("pathlib.Path.exists", return_value=True):
            asset_processor._process_scss(Path("static"), Path("output"))

        mock_sass.assert_called()
        assert "css/main.css" in asset_processor.asset_manifest or any(
            "css/main-" in k for k in asset_processor.asset_manifest.values()
        )

    @patch("PIL.Image.open")
    def test_convert_to_webp(self, mock_img_open, asset_processor):
        mock_img = MagicMock()
        mock_img.size = (100, 100)
        mock_img.mode = "RGB"
        mock_img_open.return_value.__enter__.return_value = mock_img

        with patch("io.BytesIO") as mock_io:
            mock_io.return_value.getvalue.return_value = b"webp_data"
            content, w, h = asset_processor._convert_to_webp(Path("img.jpg"))

            assert w == 100
            assert h == 100
            assert content == b"webp_data"

    @patch("shutil.copy2")
    def test_copy_favicon(self, mock_copy, asset_processor):
        with patch("pathlib.Path.exists", return_value=True):
            asset_processor._copy_favicon(Path("static"), Path("output"))
            mock_copy.assert_called()

    @patch("core.blog.assets.AssetProcessor._convert_to_webp")
    @patch("pathlib.Path.rglob")
    def test_process_images(self, mock_rglob, mock_convert, asset_processor):
        # Mocking an image file
        mock_file = MagicMock()
        mock_file.is_file.return_value = True
        mock_file.suffix = ".jpg"
        mock_file.relative_to.return_value = Path("test.jpg")

        mock_rglob.return_value = [mock_file]
        mock_convert.return_value = (b"data", 100, 100)

        # Patch write_bytes to avoid opening file
        with patch("pathlib.Path.write_bytes"):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.mkdir"):  # mock mkdir to prevent FS error
                    asset_processor._process_images(Path("static"), Path("output"))

        assert "images/test.jpg" in asset_processor.asset_manifest

    @patch("shutil.copy2")
    @patch("pathlib.Path.rglob")
    def test_process_images_other_format(self, mock_rglob, mock_copy, asset_processor):
        mock_file = MagicMock()
        mock_file.is_file.return_value = True
        mock_file.suffix = ".svg"
        mock_file.relative_to.return_value = Path("test.svg")
        mock_rglob.return_value = [mock_file]

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.mkdir"):
                asset_processor._process_images(Path("static"), Path("output"))

        mock_copy.assert_called()
        assert "images/test.svg" in asset_processor.asset_manifest

    @patch("shutil.copy2")
    @patch("pathlib.Path.rglob")
    def test_process_fonts(self, mock_rglob, mock_copy, asset_processor):
        mock_file = MagicMock()
        mock_file.is_file.return_value = True
        mock_file.relative_to.return_value = Path("font.ttf")
        mock_rglob.return_value = [mock_file]

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.mkdir"):
                asset_processor._process_fonts(Path("static"), Path("output"))

        mock_copy.assert_called()

    @patch("shutil.copy2")
    @patch("pathlib.Path.rglob")
    def test_copy_template_assets(self, mock_rglob, mock_copy, asset_processor):
        mock_file = MagicMock()
        mock_file.is_file.return_value = True
        mock_file.relative_to.return_value = Path("script.js")
        mock_rglob.return_value = [mock_file]

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.mkdir"):
                asset_processor._copy_template_assets(Path("output"))

        mock_copy.assert_called()

    @patch("core.blog.assets.AssetProcessor._process_scss")
    @patch("core.blog.assets.AssetProcessor._process_javascript")
    @patch("core.blog.assets.AssetProcessor._process_images")
    @patch("core.blog.assets.AssetProcessor._process_icons")
    @patch("core.blog.assets.AssetProcessor._copy_favicon")
    @patch("core.blog.assets.AssetProcessor._copy_template_assets")
    @patch("core.blog.assets.AssetProcessor._save_asset_manifest")
    def test_process_all(
        self,
        mock_save,
        mock_tmpl,
        mock_fav,
        mock_ico,
        mock_img,
        mock_js,
        mock_scss,
        asset_processor,
    ):
        with patch("pathlib.Path.mkdir"):
            asset_processor.process_all()

        mock_scss.assert_called()
        mock_js.assert_called()
        mock_img.assert_called()
        mock_save.assert_called()

    @patch("core.blog.assets.AssetProcessor._convert_to_webp")
    @patch("shutil.copy2")
    @patch("pathlib.Path.rglob")
    def test_process_icons(self, mock_rglob, mock_copy, mock_convert, asset_processor):
        # Mocking an icon file
        mock_file = MagicMock()
        mock_file.is_file.return_value = True
        mock_file.suffix = ".png"
        mock_file.relative_to.return_value = Path("icon.png")

        mock_rglob.return_value = [mock_file]
        mock_convert.return_value = (b"data", 32, 32)

        with patch("pathlib.Path.write_bytes"):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.mkdir"):
                    asset_processor._process_icons(Path("static"), Path("output"))

        assert "icons/icon.png" in asset_processor.asset_manifest
