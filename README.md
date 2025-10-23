# Blog

Simple static site generator built with Python. Convert Markdown to a beautiful blog with templating, asset processing, and modern web features.

## 🚀 Quick Start

### 1. Install

```bash
git clone https://github.com/ujangdoubleday/blog.git
cd blog
chmod +x install.sh
./install.sh
```

### 2. Configure

Edit `config/config.yaml`:

```yaml
site:
  title: 'My Blog'
  author: 'Your Name'
  url: 'https://yourdomain.com'
```

### 3. Create Post

Create file `content/posts/hello.md`:

```markdown
---
title: 'Hello World'
date: '2024-10-14'
published: true
---

# Hello World!

My first post.
```

### 4. Build & Run

```bash
./build.sh --serve
```

Open `http://localhost:8000`

## 📝 Commands

### Build

```bash
./build.sh              # build only
./build.sh --serve      # build + serve
./build.sh --port 3000  # custom port
```

### Deploy to IPFS

Setup `.env` with Pinata credentials:

```bash
cp .env.example .env
# edit .env with your API keys
```

Deploy:

```bash
./deploy.sh             # deploy to IPFS
./deploy.sh --snapshots # view snapshots
```

Each deployment automatically saves snapshots (current & previous) in `snapshots.json`.

## 📁 Structure

```
blog/
├── content/
│   ├── posts/         # blog posts (.md)
│   ├── pages/         # static pages (.md)
│   ├── templates/     # jinja2 templates
│   └── static/        # assets (scss, js, images)
├── core/              # core modules
├── scripts/           # build & deploy scripts
├── config/            # configuration
└── output/            # build output
```

## ✍️ Writing

### Post

```markdown
---
title: 'Post Title'
date: '2024-10-14'
author: 'Name'
description: 'Short description'
tags: ['python', 'blog']
published: true
---

# Content

Write your content in Markdown...
```

### Page

```markdown
---
title: 'About'
slug: 'about'
---

# About

Page content...
```

## 🧪 Development

### Testing

```bash
pytest                  # run tests
pytest -v              # verbose
pytest --cov           # with coverage
```

### Pre-commit

```bash
pre-commit install     # install hooks
pre-commit run --all   # run manually
```

## 📦 Requirements

- Python 3.8+
- Virtual environment

## 📄 License

MIT License
