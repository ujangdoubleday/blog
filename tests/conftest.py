"""
Pytest configuration and fixtures
"""

import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

import pytest
import yaml

# Add root directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Sample configuration for testing"""
    return {
        "site": {
            "title": "Test Blog",
            "description": "A test blog",
            "url": "http://localhost:8000",
            "author": "Test Author",
            "email": "test@example.com",
            "language": "en",
        },
        "build": {
            "input_dir": "content",
            "output_dir": "output",
            "template_dir": "content/templates",
            "static_dir": "content/static",
            "posts_per_page": 10,
            "minify_html": True,
        },
        "rss": {
            "enabled": True,
            "title": "Test Blog RSS",
            "description": "Test RSS feed",
            "max_items": 20,
        },
        "assets": {
            "minify_css": True,
            "minify_js": True,
            "optimize_images": True,
            "image_quality": 85,
        },
    }


@pytest.fixture
def config_file(temp_dir, sample_config):
    """Create a temporary config file"""
    config_path = temp_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(sample_config, f)
    return config_path


@pytest.fixture
def sample_post_content():
    """Sample markdown post content"""
    return """---
title: "Test Post"
date: "2024-10-14"
author: "Test Author"
description: "A test post"
tags: ["test", "blog"]
published: true
---

# Test Post

This is a test post with some **bold** text and *italic* text.

## Code Example

```python
def hello():
    print("Hello, World!")
```

That's it!
"""


@pytest.fixture
def sample_page_content():
    """Sample markdown page content"""
    return """---
title: "Test Page"
slug: "test-page"
description: "A test page"
---

# Test Page

This is a test page with some content.

- Item 1
- Item 2
- Item 3
"""
