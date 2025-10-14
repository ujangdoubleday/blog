#!/usr/bin/env python3
"""
Static Blog Generator - Main Build Script
A modular Python-based static site generator for blogs
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.blog.generator import BlogGenerator  # noqa: E402
from core.dev.server import DevServer  # noqa: E402


def main():
    """Main entry point for the blog generator"""
    parser = argparse.ArgumentParser(description="Static Blog Generator")
    parser.add_argument(
        "--config", "-c", default="config/config.yaml", help="Config file path"
    )
    parser.add_argument(
        "--no-clean", action="store_true", help="Don't clean output directory"
    )
    parser.add_argument(
        "--serve",
        "-s",
        action="store_true",
        help="Serve the site locally after building",
    )
    parser.add_argument(
        "--port", "-p", type=int, default=8000, help="Port for local server"
    )

    args = parser.parse_args()

    try:
        # Initialize generator
        generator = BlogGenerator(args.config)

        # Build the site
        generator.build(clean=not args.no_clean)

        # Serve locally if requested
        if args.serve:
            server = DevServer(generator.config)
            server.serve(port=args.port)

    except KeyboardInterrupt:
        print("\nBuild interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
