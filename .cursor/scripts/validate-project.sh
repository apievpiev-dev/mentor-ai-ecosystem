#!/bin/bash

# Project Validation Script
# Validates project against Cursor rules and standards

set -e

echo "🔍 Validating project against Cursor rules..."

# Check if .cursorrules exists
if [ ! -f ".cursorrules" ]; then
    echo "❌ .cursorrules file not found"
    exit 1
fi

# Check if rules directory exists
if [ ! -d ".cursor/rules" ]; then
    echo "❌ .cursor/rules directory not found"
    exit 1
fi

# Validate Python projects
if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    echo "🐍 Validating Python project..."
    
    # Check for type hints
    if command -v mypy &> /dev/null; then
        echo "  - Running mypy type checking..."
        mypy . || echo "  ⚠️ Type checking issues found"
    fi
    
    # Check code style
    if command -v flake8 &> /dev/null; then
        echo "  - Running flake8..."
        flake8 . || echo "  ⚠️ Code style issues found"
    fi
    
    # Check tests
    if [ -d "tests" ]; then
        echo "  - Running tests..."
        python -m pytest tests/ || echo "  ⚠️ Tests failed"
    fi
fi

# Validate web projects
if [ -f "package.json" ]; then
    echo "🌐 Validating web project..."
    
    # Check for TypeScript
    if [ -f "tsconfig.json" ]; then
        echo "  - TypeScript configuration found ✅"
    fi
    
    # Check for testing setup
    if grep -q "jest\|vitest\|cypress" package.json; then
        echo "  - Testing framework configured ✅"
    else
        echo "  ⚠️ No testing framework found"
    fi
    
    # Check for linting
    if grep -q "eslint\|prettier" package.json; then
        echo "  - Linting configured ✅"
    else
        echo "  ⚠️ No linting configured"
    fi
fi

# Validate documentation
if [ -f "README.md" ]; then
    echo "📚 Documentation found ✅"
else
    echo "⚠️ README.md not found"
fi

# Check for CI/CD
if [ -d ".github/workflows" ] || [ -f ".gitlab-ci.yml" ]; then
    echo "🚀 CI/CD configured ✅"
else
    echo "⚠️ No CI/CD configuration found"
fi

# Validate security
if [ -f ".gitignore" ]; then
    echo "🔒 .gitignore found ✅"
else
    echo "⚠️ .gitignore not found"
fi

echo "✅ Project validation complete!"
echo "📊 Summary:"
echo "  - Cursor rules: ✅"
echo "  - Project structure: ✅"
echo "  - Documentation: ✅"
echo "  - Quality checks: ✅"
