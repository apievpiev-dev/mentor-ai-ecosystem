#!/bin/bash

# Resource Analysis and Modernization Script
# Analyzes existing resources and suggests modernizations

set -e

echo "🔍 Analyzing existing resources..."

# Function to analyze Python files
analyze_python_files() {
    echo "🐍 Analyzing Python files..."
    
    # Find all Python files
    PYTHON_FILES=$(find . -name "*.py" -type f | head -20)
    
    if [ -n "$PYTHON_FILES" ]; then
        echo "  Found Python files:"
        echo "$PYTHON_FILES" | while read -r file; do
            echo "    - $file"
            
            # Check if file has proper structure
            if grep -q "def\|class" "$file"; then
                echo "      ✅ Contains functions/classes"
            else
                echo "      ⚠️ May need structure improvement"
            fi
            
            # Check for imports
            if grep -q "import\|from" "$file"; then
                echo "      ✅ Has imports"
            else
                echo "      ⚠️ No imports found"
            fi
            
            # Check for documentation
            if grep -q '"""\|"""' "$file"; then
                echo "      ✅ Has documentation"
            else
                echo "      ⚠️ Missing documentation"
            fi
        done
    fi
}

# Function to analyze project structure
analyze_project_structure() {
    echo "📁 Analyzing project structure..."
    
    # Check for common directories
    DIRS=("jarvis_data" "ai_manager" "mentor" "venv" "visual_reports" "visual_screenshots")
    
    for dir in "${DIRS[@]}"; do
        if [ -d "$dir" ]; then
            echo "  ✅ Found: $dir"
            
            # Count files in directory
            FILE_COUNT=$(find "$dir" -type f | wc -l)
            echo "    Files: $FILE_COUNT"
            
            # Check if directory is being used
            if [ "$FILE_COUNT" -gt 0 ]; then
                echo "    Status: Active"
            else
                echo "    Status: Empty (can be utilized)"
            fi
        else
            echo "  ❌ Missing: $dir"
        fi
    done
}

# Function to analyze running processes
analyze_processes() {
    echo "⚡ Analyzing running processes..."
    
    # Check for Python processes
    PYTHON_PROCS=$(ps aux | grep python | grep -v grep | wc -l)
    echo "  Python processes: $PYTHON_PROCS"
    
    # Check for specific JARVIS processes
    JARVIS_PROCS=$(ps aux | grep jarvis | grep -v grep | wc -l)
    echo "  JARVIS processes: $JARVIS_PROCS"
    
    # Check for web servers
    WEB_PROCS=$(ps aux | grep -E "(server|http|nginx|apache)" | grep -v grep | wc -l)
    echo "  Web server processes: $WEB_PROCS"
}

# Function to analyze configuration files
analyze_config() {
    echo "⚙️ Analyzing configuration..."
    
    CONFIG_FILES=("config.py" "requirements.txt" "package.json" "Dockerfile" ".env")
    
    for config in "${CONFIG_FILES[@]}"; do
        if [ -f "$config" ]; then
            echo "  ✅ Found: $config"
            
            # Analyze config content
            case $config in
                "config.py")
                    if grep -q "API\|TOKEN\|KEY" "$config"; then
                        echo "    Contains API configurations"
                    fi
                    ;;
                "requirements.txt")
                    DEP_COUNT=$(wc -l < "$config")
                    echo "    Dependencies: $DEP_COUNT"
                    ;;
            esac
        else
            echo "  ❌ Missing: $config"
        fi
    done
}

# Function to suggest modernizations
suggest_modernizations() {
    echo "🚀 Modernization suggestions:"
    
    # Check for outdated patterns
    if [ -f "requirements.txt" ]; then
        if grep -q "requests==\|urllib3==" requirements.txt; then
            echo "  📦 Update HTTP libraries to latest versions"
        fi
    fi
    
    # Check for missing modern tools
    if [ ! -f "pyproject.toml" ]; then
        echo "  📦 Consider adding pyproject.toml for modern Python packaging"
    fi
    
    if [ ! -f "docker-compose.yml" ]; then
        echo "  🐳 Consider adding Docker Compose for containerization"
    fi
    
    # Check for missing testing
    if [ ! -d "tests" ]; then
        echo "  🧪 Add comprehensive testing suite"
    fi
    
    # Check for missing documentation
    if [ ! -f "README.md" ]; then
        echo "  📚 Create comprehensive README"
    fi
}

# Function to identify idle resources
identify_idle_resources() {
    echo "💤 Identifying idle resources..."
    
    # Check for unused files
    UNUSED_FILES=$(find . -name "*.py" -mtime +30 -type f | head -5)
    if [ -n "$UNUSED_FILES" ]; then
        echo "  📄 Recently unused files (can be modernized):"
        echo "$UNUSED_FILES" | while read -r file; do
            echo "    - $file"
        done
    fi
    
    # Check for empty directories
    EMPTY_DIRS=$(find . -type d -empty | head -5)
    if [ -n "$EMPTY_DIRS" ]; then
        echo "  📁 Empty directories (can be utilized):"
        echo "$EMPTY_DIRS" | while read -r dir; do
            echo "    - $dir"
        done
    fi
}

# Main analysis
echo "🔍 Starting comprehensive resource analysis..."
echo "=================================================="

analyze_python_files
echo ""
analyze_project_structure
echo ""
analyze_processes
echo ""
analyze_config
echo ""
identify_idle_resources
echo ""
suggest_modernizations

echo ""
echo "✅ Resource analysis complete!"
echo "📊 Summary:"
echo "  - Existing resources identified"
echo "  - Idle resources found"
echo "  - Modernization opportunities identified"
echo "  - Next steps suggested"
echo ""
echo "🎯 Recommended actions:"
echo "  1. Modernize existing Python files"
echo "  2. Utilize idle resources"
echo "  3. Complete unfinished projects"
echo "  4. Integrate existing components"
