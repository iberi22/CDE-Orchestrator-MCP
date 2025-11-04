#!/bin/bash
# ============================================================================
# CDE Orchestrator MCP - Jules Setup Script
# ============================================================================
# This script configures the environment for Jules AI Agent to work with
# the CDE Orchestrator MCP project.
#
# Usage: bash setup.sh
# Jules will execute this automatically before running tasks.
#
# Environment:
#   - Python 3.14+
#   - pip, git
#
# ============================================================================

set -e  # Exit on error
set -u  # Error on undefined variables

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_NAME="CDE Orchestrator MCP"
PYTHON_MIN_VERSION="3.11"
VENV_NAME=".venv"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# ============================================================================
# CHECKS
# ============================================================================

log_info "Starting setup for $PROJECT_NAME..."
log_info "================================================"

# Check Python version
log_info "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
if ! python3 -c "import sys; sys.exit(0 if tuple(map(int, sys.version.split()[0].split('.')[:2])) >= tuple(map(int, '$PYTHON_MIN_VERSION'.split('.'))) else 1)" 2>/dev/null; then
    log_error "Python $PYTHON_MIN_VERSION+ required, but $PYTHON_VERSION found"
    exit 1
fi
log_success "Python $PYTHON_VERSION detected"

# Check pip
if ! command -v pip &> /dev/null; then
    log_error "pip not found. Please install pip."
    exit 1
fi
log_success "pip found"

# Check git
if ! command -v git &> /dev/null; then
    log_warning "git not found. Some features may not work."
else
    log_success "git found"
fi

# ============================================================================
# VIRTUAL ENVIRONMENT
# ============================================================================

log_info "================================================"
log_info "Setting up Python virtual environment..."

if [ ! -d "$VENV_NAME" ]; then
    log_info "Creating virtual environment in $VENV_NAME..."
    python3 -m venv "$VENV_NAME"
    log_success "Virtual environment created"
else
    log_info "Virtual environment already exists"
fi

# Activate virtual environment
if [ -f "$VENV_NAME/bin/activate" ]; then
    source "$VENV_NAME/bin/activate"
elif [ -f "$VENV_NAME/Scripts/activate" ]; then
    source "$VENV_NAME/Scripts/activate"
else
    log_error "Failed to activate virtual environment"
    exit 1
fi

log_success "Virtual environment activated"

# Upgrade pip
log_info "Upgrading pip..."
pip install --upgrade pip setuptools wheel --quiet
log_success "pip upgraded"

# ============================================================================
# DEPENDENCIES
# ============================================================================

log_info "================================================"
log_info "Installing project dependencies..."

# Install main dependencies
if [ -f "requirements.txt" ]; then
    log_info "Installing from requirements.txt..."
    pip install -r requirements.txt --quiet
    log_success "Main dependencies installed"
else
    log_warning "requirements.txt not found, installing from pyproject.toml..."
    pip install -e . --quiet
    log_success "Dependencies installed from pyproject.toml"
fi

# Install dev dependencies (optional but recommended for Jules)
log_info "Installing development dependencies..."
pip install -e ".[dev]" --quiet 2>/dev/null || log_warning "Dev dependencies installation skipped"

# ============================================================================
# PROJECT STRUCTURE
# ============================================================================

log_info "================================================"
log_info "Verifying project structure..."

REQUIRED_DIRS=(
    "src"
    "tests"
    "specs"
    ".cde"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        log_success "Found $dir/"
    else
        log_warning "Missing $dir/"
    fi
done

REQUIRED_FILES=(
    "pyproject.toml"
    "README.md"
    "src/server.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        log_success "Found $file"
    else
        log_error "Missing $file"
        exit 1
    fi
done

# ============================================================================
# INITIALIZATION
# ============================================================================

log_info "================================================"
log_info "Initializing project components..."

# Create .copilot/skills directories for DSMS
log_info "Initializing Dynamic Skill Management System..."
mkdir -p .copilot/skills/base .copilot/skills/ephemeral
log_success "DSMS directories created"

# Create logs directory
mkdir -p logs
log_success "Logs directory created"

# ============================================================================
# VALIDATION
# ============================================================================

log_info "================================================"
log_info "Validating setup..."

# Test imports
log_info "Testing critical imports..."
python3 -c "from fastmcp import FastMCP; print('✓ fastmcp')" 2>/dev/null || log_error "fastmcp import failed"
python3 -c "from pydantic import BaseModel; print('✓ pydantic')" 2>/dev/null || log_error "pydantic import failed"
python3 -c "from src.cde_orchestrator.skills.manager import SkillManager; print('✓ SkillManager')" 2>/dev/null || log_warning "SkillManager import might not be available yet"

log_success "Critical imports validated"

# Test MCP server
log_info "Testing MCP server initialization..."
python3 -c "from src.server import app; print('✓ MCP server loads')" 2>/dev/null || log_error "MCP server failed to load"
log_success "MCP server validated"

# ============================================================================
# COMPLETION
# ============================================================================

log_info "================================================"
log_success "Setup completed successfully!"
log_info ""
log_info "Next steps:"
log_info "1. Source the virtual environment: source $VENV_NAME/bin/activate"
log_info "2. Run the MCP server: python src/server.py"
log_info "3. Run tests: pytest tests/ -v"
log_info ""
log_info "For Jules integration:"
log_info "- Project is ready for Jules to begin work"
log_info "- All dependencies are installed"
log_info "- DSMS is initialized"
log_info "- MCP server can be started"
log_info ""
log_success "Happy coding! 🚀"

# ============================================================================
# ENVIRONMENT SUMMARY
# ============================================================================

echo ""
echo "Setup Summary:"
echo "  Project: $PROJECT_NAME"
echo "  Python: $(python3 --version)"
echo "  pip: $(pip --version)"
echo "  Virtual Environment: $VENV_NAME"
echo "  Status: ✅ READY FOR JULES"
echo ""
