#!/bin/bash

# Blog Deployment Script to IPFS via Pinata
# Usage: ./deploy.sh [options]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    echo -e "${YELLOW}Please run: ./install.sh${NC}"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to activate virtual environment!${NC}"
        exit 1
    fi
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo -e "${YELLOW}Please create .env file with your Pinata credentials${NC}"
    echo -e "${YELLOW}Copy from .env.example and fill in your API keys${NC}"
    exit 1
fi

# Check if output directory exists
if [ ! -d "output" ]; then
    echo -e "${RED}Error: Output directory not found!${NC}"
    echo -e "${YELLOW}Please build your blog first: ./build.sh${NC}"
    exit 1
fi

# Run deployment script
echo -e "${BLUE}🚀 Deploying to IPFS via Pinata...${NC}"
echo ""
${PYTHON_CMD} scripts/deploy.py "$@"

# Check if deployment was successful
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
else
    echo ""
    echo -e "${RED}❌ Deployment failed!${NC}"
    exit 1
fi
