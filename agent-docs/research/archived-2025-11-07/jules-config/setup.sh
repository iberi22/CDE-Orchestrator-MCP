#!/bin/bash
# Jules Environment Setup Script for CDE Orchestrator MCP
# This script prepares the Jules VM environment with all dependencies

set -e

echo "🔧 CDE Orchestrator MCP - Jules Environment Setup"
echo "=================================================="
echo ""

# 1. Upgrade pip
echo "📦 Upgrading pip..."
pip install -q --upgrade pip
echo "✅ pip upgraded"
echo ""

# 2. Install Python dependencies
echo "📦 Installing Python dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "⚠️  requirements.txt not found, skipping"
fi
echo ""

# 3. Verify Python environment
echo "🐍 Python environment:"
python --version
pip --version
echo ""

# 4. Verify key packages
echo "📚 Verifying key packages..."
python -c "import fastmcp; print('✅ fastmcp:', fastmcp.__version__)" 2>/dev/null || echo "❌ fastmcp not found"
python -c "import pydantic; print('✅ pydantic:', pydantic.__version__)" 2>/dev/null || echo "❌ pydantic not found"
python -c "import yaml; print('✅ PyYAML: installed')" 2>/dev/null || echo "❌ PyYAML not found"
python -c "import jules_agent_sdk; print('✅ jules-agent-sdk:', jules_agent_sdk.__version__ if hasattr(jules_agent_sdk, '__version__') else 'installed')" 2>/dev/null || echo "❌ jules-agent-sdk not found"
echo ""

# 5. Install pre-commit hooks (if available)
if command -v pre-commit &> /dev/null && [ -f ".pre-commit-config.yaml" ]; then
    echo "🪝 Setting up pre-commit hooks..."
    pre-commit install
    echo "✅ Pre-commit hooks installed"
    echo ""
fi

# 6. Run tests (optional, can be commented out for faster setup)
if [ "${RUN_TESTS:-true}" = "true" ] && [ -d "tests" ]; then
    echo "🧪 Running tests to verify setup..."
    pytest tests/ -v --tb=short -k "not integration" || {
        echo "⚠️  Some tests failed, but continuing..."
    }
    echo ""
fi

# 7. Check code quality (optional, can be commented out for faster setup)
if [ "${RUN_LINTING:-false}" = "true" ]; then
    echo "🔍 Checking code quality..."

    if command -v ruff &> /dev/null; then
        ruff check src/ --select I,E,F,B,SIM || echo "⚠️  Linting issues found"
    fi

    if command -v black &> /dev/null; then
        black src/ tests/ --check || echo "⚠️  Formatting issues found"
    fi
    echo ""
fi

# 8. Type checking (optional, can be commented out for faster setup)
if [ "${RUN_MYPY:-false}" = "true" ] && command -v mypy &> /dev/null; then
    echo "🔬 Type checking..."
    mypy src/ --ignore-missing-imports || echo "⚠️  Type issues found"
    echo ""
fi

# 9. Display environment summary
echo "📊 Environment Summary"
echo "====================="
echo "Python: $(python --version)"
echo "Pip: $(pip --version | awk '{print $2}')"
echo "Working Directory: $(pwd)"
echo "Git Branch: $(git branch --show-current 2>/dev/null || echo 'N/A')"
echo ""

echo "✅ Environment setup complete!"
echo "🚀 Ready for Jules execution."
echo ""
echo "💡 To disable tests/linting in setup, set:"
echo "   export RUN_TESTS=false"
echo "   export RUN_LINTING=false"
echo "   export RUN_MYPY=false"
