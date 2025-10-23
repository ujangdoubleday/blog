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

Each deployment automatically:

- Converts CID to v1 (silent)
- Deletes previous deployment from Pinata (saves storage)
- Saves snapshots (current & previous) in `snapshots.json`

### Cloudflare DNS (Optional)

Update DNSLink automatically after deployment. Default: `false`

Set in `.env`:

```bash
CLOUDFLARE=true
CLOUDFLARE_EMAIL=your-email@example.com
CLOUDFLARE_API_KEY=your-api-key
CLOUDFLARE_ZONE_ID=your-zone-id
CLOUDFLARE_HOSTNAME=your-hostname-id
```

When enabled, deployment will update Cloudflare DNSLink to point to the new IPFS CID.

Full docs: https://developers.cloudflare.com/api/resources/web3/

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
