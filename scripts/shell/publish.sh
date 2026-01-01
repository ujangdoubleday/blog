#!/bin/bash

# Blog Publish Script - Build and Deploy
# Usage: ./publish.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get project root directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# Detect Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Error: Python is not installed!${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found!${NC}"
    echo -e "${YELLOW}Please run: make install${NC}"
    exit 1
fi

# Activate virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    source venv/bin/activate
fi

# Run build
echo -e "${BLUE}=== Building site... ===${NC}"
if ! ${PYTHON_CMD} scripts/build.py; then
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Build complete!${NC}"

echo ""

# Run deploy
echo -e "${BLUE}=== Deploying site... ===${NC}"
if ! ${PYTHON_CMD} scripts/deploy.py; then
    echo -e "${RED}Deploy failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Deploy complete!${NC}"

echo ""
echo -e "${GREEN}=== Publication completed successfully ===${NC}"
exit 0
