# Blog

A simple, fast, and flexible static site generator built with Python. Convert Markdown posts to a beautiful blog with templating, asset processing, and modern web features.

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/ujangdoubleday/blog.git
cd blog
```

### 2. Run Installation Script

**Linux/Mac:**
```bash
chmod +x install.sh    # Make script executable
./install.sh
```

**Windows:**
```cmd
install.bat
```

The script will automatically:
- Create virtual environment
- Activate virtual environment
- Install all dependencies

### Manual Installation (Alternative)

<details>
<summary>Click to expand manual steps</summary>

**Setup Virtual Environment:**

Create virtual environment:
```bash
python -m venv venv
```

Activate virtual environment (Linux/Mac):
```bash
source venv/bin/activate
```

Activate virtual environment (Windows):
```cmd
venv\Scripts\activate
```

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

</details>

## Quick Start

### 1. Configure Site

Edit `config/config.yaml`:

```yaml
site:
  title: "My Blog"
  author: "Your Name"
  email: "your@email.com"
  url: "https://yourdomain.com"
```

### 2. Create First Post

Create file `content/posts/hello-world.md`:

```markdown
---
title: "Hello World"
date: "2024-10-14"
author: "Your Name"
published: true
---

# Hello World!

My first blog post.
```

### 3. Build & Run

Make script executable:
```bash
chmod +x build.sh
```

Build site:
```bash
./build.sh
```

Build and serve locally:
```bash
./build.sh --serve
```

Open `http://localhost:8000` in your browser.

## Commands

### Build Scripts (Recommended)

**Linux/Mac:**

Make script executable (first time only):
```bash
chmod +x build.sh
```

Basic build:
```bash
./build.sh
```

Build and serve locally:
```bash
./build.sh --serve
```

Custom port:
```bash
./build.sh --serve --port 3000
```

Build without cleaning:
```bash
./build.sh --no-clean
```

**Windows:**

Basic build:
```cmd
build.bat
```

Build and serve locally:
```cmd
build.bat --serve
```

Custom port:
```cmd
build.bat --serve --port 3000
```

Build without cleaning:
```cmd
build.bat --no-clean
```

### Manual Commands (Alternative)

First activate virtual environment:

Linux/Mac:
```bash
source venv/bin/activate
```

Windows:
```cmd
venv\Scripts\activate
```

Then run build commands:

Basic build:
```bash
python scripts/build.py
```

Build and serve locally:
```bash
python scripts/build.py --serve
```

Custom port:
```bash
python scripts/build.py --serve --port 3000
```

Build without cleaning:
```bash
python scripts/build.py --no-clean
```

## Structure

```
blog/
├── content/           # All content and assets
│   ├── posts/         # Blog posts (.md)
│   ├── pages/         # Static pages (.md)
│   ├── templates/     # Jinja2 templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── post.html
│   │   ├── page.html
│   │   └── partials/
│   └── static/        # Static assets
│       ├── scss/      # Styling (SCSS)
│       ├── js/        # JavaScript
│       └── images/    # Images
├── core/              # Core application modules
│   ├── blog/          # Blog engine (generator, assets, etc.)
│   ├── dev/           # Development server
│   └── utils/         # Utilities (content loader, template renderer)
├── scripts/           # Build scripts
│   └── build.py       # Main build script
├── tests/             # Test suite
├── config/
│   └── config.yaml    # Site configuration
└── output/            # Generated static site
```

## Writing

### Blog Posts

File: `content/posts/my-post.md`

```markdown
---
title: "Post Title"
date: "2024-10-14"
author: "Author Name"
description: "Short description"
tags: ["python", "blog"]
published: true
---

# Post Content

Write your content in Markdown...
```

### Pages

File: `content/pages/about.md`

```markdown
---
title: "About"
slug: "about"
---

# About

About page content...
```

## Development

### Running Tests

This project uses **pytest** for testing with comprehensive test coverage.

Run tests:
```bash
# Basic test run
pytest

# Verbose output
pytest -v

# With coverage report
pytest --cov=core --cov-report=term-missing

# Run specific test file
pytest tests/test_content.py

# Run specific test
pytest tests/test_content.py::TestPost::test_post_creation
```

Test structure:
- **`tests/`** - Test directory
- **`tests/conftest.py`** - Pytest fixtures and configuration
- **`pytest.ini`** - Pytest configuration file
- **Coverage: 71%** - Current test coverage

### Pre-commit Hooks

This project uses **pre-commit** to ensure code quality and consistency.

Install pre-commit hooks:
```bash
pre-commit install
```

Run pre-commit manually:
```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run
```

**Hooks included:**
- **Black** - Python code formatting
- **Flake8** - Python linting
- **YAML check** - Validates YAML files
- **End-of-file fixer** - Ensures files end with newline
- **Trailing whitespace** - Removes trailing whitespace
- **Pytest** - Runs tests on push (optional)


## Requirements

- Python 3.8+
- Virtual environment (recommended)

## License

This project is open source and available under the [MIT License](LICENSE.md).
