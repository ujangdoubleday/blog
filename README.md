# Python Static Blog Generator

A simple, fast, and flexible static site generator built with Python. Convert Markdown posts to a beautiful blog with templating, asset processing, and modern web features.

## Features

- **Markdown Support**: Write posts in Markdown with YAML frontmatter
- **Jinja2 Templates**: Flexible templating system with inheritance
- **SCSS Processing**: Modern CSS with variables and mixins
- **Asset Optimization**: Automatic image compression and minification
- **RSS Feed**: Automatic RSS feed generation
- **Search**: Client-side search functionality
- **Responsive**: Mobile-first responsive design
- **Fast Builds**: Optimized Python-based generation
- **SEO Friendly**: Proper meta tags and semantic HTML

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Your Site**
   Edit `config/config.yaml` to customize your blog settings.

3. **Write Content**
   - Add blog posts to `content/posts/` in Markdown format
   - Add static pages to `content/pages/`

4. **Build Your Site**
   ```bash
   python scripts/build.py
   ```

5. **Serve Locally** (optional)
   ```bash
   python scripts/build.py --serve
   ```

## Project Structure

```
blog/
├── content/
│   ├── posts/              # Blog posts in Markdown
│   │   ├── hello-world.md
│   │   └── second-post.md
│   └── pages/              # Static pages
│       └── about.md
├── templates/              # Jinja2 templates
│   ├── base.html          # Base template
│   ├── post.html          # Individual post template
│   ├── page.html          # Static page template
│   ├── index.html         # Homepage template
│   ├── partials/          # Template partials
│   │   ├── header.html
│   │   └── footer.html
│   └── static/            # Template-specific static files
│       ├── logo.svg
│       └── placeholder.jpg
├── static/                # Source assets
│   ├── images/
│   │   └── uploads/       # Images for posts
│   ├── scss/
│   │   └── main.scss      # Main stylesheet
│   └── js/
│       └── main.js        # JavaScript functionality
├── output/                # Generated site (deployable)
│   ├── assets/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── posts/
│   ├── pages/
│   ├── index.html
│   ├── rss.xml
│   └── search.json
├── config/
│   └── config.yaml        # Site configuration
├── scripts/
│   └── build.py          # Main build script
└── requirements.txt       # Python dependencies
```

## Writing Content

### Blog Posts

Create Markdown files in `content/posts/` with YAML frontmatter:

```markdown
---
title: "My Blog Post"
date: "2024-10-14"
author: "Your Name"
description: "A short description of the post"
tags: ["python", "blog", "tutorial"]
image: "/_sync/images/post-image.jpg"
published: true
---

# Your Content Here

Write your blog post content in Markdown...
```

### Static Pages

Create Markdown files in `content/pages/`:

```markdown
---
title: "About"
description: "About this blog"
---

# About This Blog

Your page content here...
```

## Configuration

Edit `config/config.yaml` to customize your site:

```yaml
site:
  title: "Your Blog Title"
  description: "Your blog description"
  author: "Your Name"
  email: "your@email.com"
  url: "https://yourdomain.com"

build:
  posts_per_page: 10
  date_format: "%Y-%m-%d"

rss:
  enabled: true
  max_items: 20

assets:
  minify_css: false
  minify_js: false
  optimize_images: true
  image_quality: 85
```

## Build Commands

- **Basic build**: `python scripts/build.py`
- **Build and serve**: `python scripts/build.py --serve`
- **Custom port**: `python scripts/build.py --serve --port 3000`
- **No clean build**: `python scripts/build.py --no-clean`
- **Custom config**: `python scripts/build.py --config path/to/config.yaml`

## Customization

### Templates

Templates use Jinja2 syntax and support:
- Template inheritance (`{% extends "base.html" %}`)
- Includes (`{% include "partials/header.html" %}`)
- Variables (`{{ post.title }}`)
- Filters (`{{ content|markdown }}`)
- Loops and conditionals

### Styling

- Edit `static/scss/main.scss` for styling
- Uses modern SCSS features (variables, nesting, mixins)
- Automatically compiled to CSS during build
- Responsive design with mobile-first approach

### JavaScript

- Edit `static/js/main.js` for interactivity
- Includes mobile menu, reading progress, and copy code functionality
- Easy to extend with additional features

## Deployment

The generator creates a static site in the `output/` directory that can be deployed to:

- **GitHub Pages**: Push to repository and enable Pages
- **Netlify**: Connect repository for automatic deployments
- **Vercel**: Similar to Netlify with excellent performance
- **Traditional hosting**: Upload files via FTP/SFTP
- **CDN**: Any static file hosting service

## Dependencies

- `markdown`: Markdown processing
- `jinja2`: Template engine
- `pyyaml`: YAML configuration parsing
- `libsass`: SCSS compilation
- `python-frontmatter`: Frontmatter parsing
- `feedgen`: RSS feed generation
- `pillow`: Image processing
- `watchdog`: File system monitoring

## License

This project is open source and available under the [MIT License](LICENSE.md).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.