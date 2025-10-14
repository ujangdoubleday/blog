#!/bin/bash

# Blog Generator Installation Script
# This script will setup virtual environment and install dependencies

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "=================================="
echo "   Blog Generator Installation"
echo "=================================="
echo -e "${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python is not installed!${NC}"
    echo -e "${YELLOW}Please install Python 3.8+ first.${NC}"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo -e "${YELLOW}Using Python: $(${PYTHON_CMD} --version)${NC}"
echo

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Skipping creation...${NC}"
else
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    ${PYTHON_CMD} -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to create virtual environment!${NC}"
        echo -e "${YELLOW}Make sure you have venv module installed: pip install virtualenv${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Virtual environment created successfully!${NC}"
fi

echo

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to activate virtual environment!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Virtual environment activated!${NC}"

echo

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install dependencies!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Dependencies installed successfully!${NC}"

echo
echo -e "${BLUE}"
echo "=================================="
echo "   Installation Complete! 🎉"
echo "=================================="
echo -e "${NC}"

echo -e "${GREEN}Next steps:${NC}"
echo -e "1. Configure your site: ${YELLOW}config/config.yaml${NC}"
echo -e "2. Create your first post: ${YELLOW}content/posts/my-post.md${NC}"
echo -e "3. Build your blog: ${YELLOW}./build.sh${NC}"
echo -e "4. Serve locally: ${YELLOW}./build.sh --serve${NC}"

echo
echo -e "${BLUE}Happy blogging! 📝${NC}"
