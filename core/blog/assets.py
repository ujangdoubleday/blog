"""
Asset processing for SCSS, JavaScript, and images
"""

import re
import json
import hashlib
import shutil
import time
from pathlib import Path
from typing import Dict, Any

import sass
from PIL import Image


class AssetProcessor:
    """Handles processing of static assets (CSS, JS, images)"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.asset_manifest = {}  # Maps original names to hashed names
        self.build_timestamp = str(int(time.time()))  # Unique build identifier

    def process_all(self):
        """Process all static assets"""
        static_dir = Path(self.config["build"]["static_dir"])
        output_assets = Path(self.config["build"]["output_dir"]) / "_sync"

        # Create output directories
        (output_assets / "css").mkdir(parents=True, exist_ok=True)
        (output_assets / "js").mkdir(parents=True, exist_ok=True)
        (output_assets / "images").mkdir(parents=True, exist_ok=True)

        # Reset asset manifest
        self.asset_manifest = {}

        # Process different asset types
        self._process_scss(static_dir, output_assets)
        self._process_javascript(static_dir, output_assets)
        self._process_images(static_dir, output_assets)
        self._process_fonts(static_dir, output_assets)
        self._copy_template_assets(output_assets)

        # Save asset manifest
        self._save_asset_manifest(output_assets)

        print("Processed all assets")

    def _process_scss(self, static_dir: Path, output_assets: Path):
        """Compile SCSS to CSS"""
        scss_file = static_dir / "scss" / "main.scss"
        if scss_file.exists():
            try:
                css_content = sass.compile(filename=str(scss_file))

                # Minify CSS if configured
                if self.config.get("assets", {}).get("minify_css", False):
                    css_content = self._minify_css(css_content)
                    print("Compiled and minified SCSS to CSS")
                else:
                    print("Compiled SCSS to CSS")

                # Generate hashed filename
                original_name = "main.css"
                hashed_name = self._get_hashed_filename(original_name, css_content)

                # Update manifest
                manifest_key = f"css/{original_name}"
                self.asset_manifest[manifest_key] = f"css/{hashed_name}"

                css_output = output_assets / "css" / hashed_name
                with open(css_output, "w", encoding="utf-8") as f:
                    f.write(css_content)

                print(f"Generated CSS: {hashed_name}")
            except Exception as e:
                print(f"Error compiling SCSS: {e}")

    def _process_javascript(self, static_dir: Path, output_assets: Path):
        """Copy and optionally minify JavaScript"""
        js_file = static_dir / "js" / "main.js"
        if js_file.exists():
            js_content = js_file.read_text(encoding="utf-8")

            # Minify JS if configured
            if self.config.get("assets", {}).get("minify_js", False):
                js_content = self._minify_js(js_content)
                print("Copied and minified JavaScript")
            else:
                print("Copied JavaScript")

            # Generate hashed filename
            original_name = "main.js"
            hashed_name = self._get_hashed_filename(original_name, js_content)

            # Update manifest
            self.asset_manifest[f"js/{original_name}"] = f"js/{hashed_name}"

            js_output = output_assets / "js" / hashed_name
            with open(js_output, "w", encoding="utf-8") as f:
                f.write(js_content)

            print(f"Generated JS: {hashed_name}")

    def _process_images(self, static_dir: Path, output_assets: Path):
        """Copy and optimize images"""
        images_dir = static_dir / "images"
        if images_dir.exists():
            for img_file in images_dir.rglob("*"):
                if img_file.is_file() and img_file.suffix.lower() in [
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".gif",
                    ".webp",
                    ".svg",
                ]:
                    relative_path = img_file.relative_to(images_dir)

                    # Read file content for hashing
                    img_content = img_file.read_bytes()

                    # Generate hashed filename
                    original_name = str(relative_path).replace("\\", "/")
                    hashed_name = self._get_hashed_filename(original_name, img_content)

                    # Update manifest
                    self.asset_manifest[
                        f"images/{original_name}"
                    ] = f"images/{hashed_name}"

                    output_img = output_assets / "images" / hashed_name
                    output_img.parent.mkdir(parents=True, exist_ok=True)

                    if self.config.get("assets", {}).get(
                        "optimize_images", True
                    ) and img_file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
                        self._optimize_image(img_file, output_img)
                    else:
                        shutil.copy2(img_file, output_img)

            print("Processed images")

    def _process_fonts(self, static_dir: Path, output_assets: Path):
        """copy font files to output"""
        fonts_dir = static_dir / "fonts"
        if fonts_dir.exists():
            output_fonts = output_assets / "fonts"
            output_fonts.mkdir(parents=True, exist_ok=True)

            # copy all font files recursively
            for font_file in fonts_dir.rglob("*"):
                if font_file.is_file():
                    relative_path = font_file.relative_to(fonts_dir)
                    output_file = output_fonts / relative_path
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(font_file, output_file)

            print("Processed fonts")

    def _copy_template_assets(self, output_assets: Path):
        """Copy template static files"""
        template_static = Path(self.config["build"]["template_dir"]) / "static"
        if template_static.exists():
            for static_file in template_static.rglob("*"):
                if static_file.is_file():
                    relative_path = static_file.relative_to(template_static)
                    output_file = output_assets / relative_path
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(static_file, output_file)

            print("Copied template static files")

    def _optimize_image(self, input_path: Path, output_path: Path):
        """Optimize image for web"""
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")

                # Optimize and save
                assets_config = self.config.get("assets", {})
                quality = assets_config.get("image_quality", 85)
                img.save(output_path, optimize=True, quality=quality)
        except Exception as e:
            print(f"Error optimizing image {input_path}: {e}")
            shutil.copy2(input_path, output_path)

    def _minify_css(self, css_content: str) -> str:
        """Basic CSS minification"""
        # Remove comments
        css_content = re.sub(r"/\*.*?\*/", "", css_content, flags=re.DOTALL)
        # Remove extra whitespace
        css_content = re.sub(r"\s+", " ", css_content)
        # Remove spaces around certain characters
        css_content = re.sub(r"\s*([{}:;,>+~])\s*", r"\1", css_content)
        return css_content.strip()

    def _minify_js(self, js_content: str) -> str:
        """Enhanced JavaScript minification"""
        # Remove single-line comments (but keep URLs)
        js_content = re.sub(
            r"(?<!http:)(?<!https:)//.*$", "", js_content, flags=re.MULTILINE
        )
        # Remove multi-line comments
        js_content = re.sub(r"/\*.*?\*/", "", js_content, flags=re.DOTALL)
        # Remove unnecessary whitespace
        js_content = re.sub(r"\s*([{}();,:])\s*", r"\1", js_content)
        js_content = re.sub(r"\s*=\s*", "=", js_content)
        js_content = re.sub(r"\s*\+\s*", "+", js_content)
        js_content = re.sub(r"\s*-\s*", "-", js_content)
        js_content = re.sub(r"\s*\*\s*", "*", js_content)
        js_content = re.sub(r"\s*/\s*", "/", js_content)
        # Remove extra newlines and spaces
        js_content = re.sub(r"\n+", "", js_content)
        js_content = re.sub(r"\s+", " ", js_content)
        return js_content.strip()

    def _generate_hash(self, content, length: int = 8) -> str:
        """Generate hash from content + build timestamp for cache busting"""
        if isinstance(content, str):
            content_bytes = content.encode()
        else:
            content_bytes = content

        # Combine content with build timestamp for unique hash every build
        combined_content = content_bytes + self.build_timestamp.encode()
        return hashlib.md5(combined_content).hexdigest()[:length]

    def _get_hashed_filename(self, original_name: str, content) -> str:
        """Generate hashed filename"""
        use_hash = self.config.get("assets", {}).get("use_hash", True)
        if not use_hash:
            return original_name

        name_parts = original_name.rsplit(".", 1)
        if len(name_parts) == 2:
            name, ext = name_parts
            file_hash = self._generate_hash(content)
            return f"{name}-{file_hash}.{ext}"
        return original_name

    def _save_asset_manifest(self, output_assets: Path):
        """Save asset manifest to JSON file"""
        manifest_file = output_assets / "manifest.json"
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(self.asset_manifest, f, indent=2)
        print("Generated asset manifest")
