# Blog Generator Makefile
# Usage: make [target]

.PHONY: help install build serve deploy publish test lint clean all

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
VENV := venv
SHELL_DIR := scripts/shell
SCRIPTS_DIR := scripts
OUTPUT_DIR := output

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

#==============================================================================
# HELP
#==============================================================================

help: ## Show this help message
	@echo ""
	@echo "$(BLUE)Blog Generator$(NC)"
	@echo ""
	@echo "$(YELLOW)Setup$(NC)"
	@echo "  $(GREEN)install$(NC)       Setup venv and dependencies"
	@echo ""
	@echo "$(YELLOW)Development$(NC)"
	@echo "  $(GREEN)build$(NC)         Build static site"
	@echo "  $(GREEN)serve$(NC)         Local server (PORT=3000)"
	@echo "  $(GREEN)dev$(NC)           install → build → serve"
	@echo ""
	@echo "$(YELLOW)Production$(NC)"
	@echo "  $(GREEN)deploy$(NC)        Deploy to IPFS/Pinata"
	@echo "  $(GREEN)publish$(NC)       build → deploy"
	@echo "  $(GREEN)all$(NC)           install → build → deploy"
	@echo ""
	@echo "$(YELLOW)Quality$(NC)"
	@echo "  $(GREEN)test$(NC)          Run tests"
	@echo "  $(GREEN)test-cov$(NC)      Tests + coverage"
	@echo "  $(GREEN)lint$(NC)          Linting (flake8)"
	@echo "  $(GREEN)format$(NC)        Format (black, isort)"
	@echo "  $(GREEN)check$(NC)         lint → test"
	@echo ""
	@echo "$(YELLOW)Cleanup$(NC)"
	@echo "  $(GREEN)clean$(NC)         Remove output/cache"
	@echo "  $(GREEN)clean-all$(NC)     Remove all + venv"
	@echo ""

#==============================================================================
# SETUP
#==============================================================================

install: ## Setup virtual environment and install dependencies
	@echo "$(BLUE)🔧 Running installation...$(NC)"
	@bash $(SHELL_DIR)/install.sh
	@echo "$(GREEN)✅ Installation complete!$(NC)"

#==============================================================================
# BUILD
#==============================================================================

build: ## Build the static site
	@echo "$(BLUE)🔨 Building site...$(NC)"
	@bash $(SHELL_DIR)/build.sh
	@echo "$(GREEN)✅ Build complete!$(NC)"

serve: ## Build and serve locally (PORT=3000 for custom port)
	@echo "$(BLUE)🌐 Starting local server...$(NC)"
ifdef PORT
	@bash $(SHELL_DIR)/build.sh --serve --port $(PORT)
else
	@bash $(SHELL_DIR)/build.sh --serve
endif

#==============================================================================
# DEPLOYMENT
#==============================================================================

deploy: ## Deploy to IPFS via Pinata
	@echo "$(BLUE)🚀 Deploying to IPFS...$(NC)"
	@bash $(SHELL_DIR)/deploy.sh
	@echo "$(GREEN)✅ Deployment complete!$(NC)"

publish: ## Build and deploy (full pipeline)
	@echo "$(BLUE)📦 Publishing (build + deploy)...$(NC)"
	@bash $(SHELL_DIR)/publish.sh
	@echo "$(GREEN)✅ Publication complete!$(NC)"

#==============================================================================
# TESTING & LINTING
#==============================================================================

test: ## Run pytest tests
	@echo "$(BLUE)🧪 Running tests...$(NC)"
	@$(VENV)/bin/pytest tests/ -v
	@echo "$(GREEN)✅ Tests complete!$(NC)"

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)🧪 Running tests with coverage...$(NC)"
	@$(VENV)/bin/pytest tests/ -v --cov=core --cov=scripts --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)✅ Coverage report generated! Open htmlcov/index.html$(NC)"

lint: ## Run linting checks
	@echo "$(BLUE)🔍 Running linters...$(NC)"
	@$(VENV)/bin/flake8 $(SCRIPTS_DIR)/ core/ tests/ --max-line-length=120
	@echo "$(GREEN)✅ Linting complete!$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)✨ Formatting code...$(NC)"
	@$(VENV)/bin/black $(SCRIPTS_DIR)/ core/ tests/
	@$(VENV)/bin/isort $(SCRIPTS_DIR)/ core/ tests/
	@echo "$(GREEN)✅ Formatting complete!$(NC)"

#==============================================================================
# CLEANUP
#==============================================================================

clean: ## Remove build artifacts and cache
	@echo "$(YELLOW)🧹 Cleaning up...$(NC)"
	@rm -rf $(OUTPUT_DIR)
	@rm -rf __pycache__ .pytest_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup complete!$(NC)"

clean-all: clean ## Remove all generated files including venv
	@echo "$(YELLOW)🧹 Removing virtual environment...$(NC)"
	@rm -rf $(VENV)
	@echo "$(GREEN)✅ Full cleanup complete!$(NC)"

#==============================================================================
# DEVELOPMENT
#==============================================================================

dev: install build serve ## Full dev setup: install, build, and serve

check: lint test ## Run all checks (lint + test)

all: install build deploy ## Full pipeline: install, build, deploy
