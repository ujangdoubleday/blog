# Blog Generator Scripts

Modular Python static site generator with clean architecture.

## Structure

```
scripts/
├── build.py              # Main entry point
├── core/                 # Core functionality
│   ├── __init__.py      # Core exports
│   ├── generator.py     # Main BlogGenerator class
│   ├── content.py       # Post and Page models
│   ├── assets.py        # Asset processing (SCSS, JS, images)
│   ├── rss.py          # RSS feed generation
│   └── search.py       # Search index generation
├── dev/                 # Development utilities
│   ├── __init__.py     # Dev exports
│   └── server.py       # Local development server
└── utils/              # Utility functions
    ├── __init__.py     # Utils exports
    ├── content_loader.py    # Content loading and parsing
    └── template_renderer.py # Jinja2 template rendering
```

## Usage

```bash
# Basic build
python scripts/build.py

# Build and serve locally
python scripts/build.py --serve

# Custom port
python scripts/build.py --serve --port 3000

# No clean build (keep existing files)
python scripts/build.py --no-clean

# Custom config file
python scripts/build.py --config path/to/config.yaml
```

## Architecture

### Core Components

- **BlogGenerator**: Main orchestrator class that coordinates all components
- **ContentLoader**: Loads and parses Markdown files with frontmatter
- **TemplateRenderer**: Handles Jinja2 template rendering
- **AssetProcessor**: Processes SCSS, JavaScript, and images
- **RSSGenerator**: Creates RSS feeds from posts
- **SearchIndexer**: Generates JSON search index

### Development Tools

- **DevServer**: Local HTTP server for testing the generated site

### Benefits of Modular Structure

1. **Maintainability**: Each component has a single responsibility
2. **Testability**: Individual components can be tested in isolation
3. **Extensibility**: Easy to add new features without touching existing code
4. **Readability**: Clean separation of concerns makes code easier to understand
5. **Reusability**: Components can be reused in different contexts

## Extending the Generator

### Adding New Content Types

1. Create a new model in `core/content.py`
2. Add loading logic in `utils/content_loader.py`
3. Add rendering logic in `utils/template_renderer.py`
4. Update `core/generator.py` to use the new content type

### Adding Asset Processing

1. Add new methods to `core/assets.py`
2. Update `AssetProcessor.process_all()` to call new methods

### Adding Build Features

1. Create new classes in appropriate modules
2. Initialize them in `core/generator.py`
3. Call them from `BlogGenerator.build()`
