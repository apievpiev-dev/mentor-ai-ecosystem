#!/bin/bash

# Cursor Project Setup Script
# Automatically sets up a new project with all rules and configurations

set -e

PROJECT_NAME=$1
PROJECT_TYPE=${2:-"web"}

if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: $0 <project-name> [project-type]"
    echo "Project types: web, api, mobile, game, ml, blockchain, iot"
    exit 1
fi

echo "🚀 Setting up project: $PROJECT_NAME ($PROJECT_TYPE)"

# Create project directory
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Copy cursor rules
cp -r ~/.cursor/rules .cursor/
cp ~/.cursorrules .

# Create project structure based on type
case $PROJECT_TYPE in
    "web")
        echo "📱 Setting up web project..."
        mkdir -p {src/{components,pages,hooks,utils,types,styles},public,tests,docs}
        touch src/main.tsx src/App.tsx package.json tsconfig.json tailwind.config.js
        ;;
    "api")
        echo "🔌 Setting up API project..."
        mkdir -p {app/{api,models,services,utils},tests,docs}
        touch app/main.py requirements.txt Dockerfile
        ;;
    "mobile")
        echo "📱 Setting up mobile project..."
        mkdir -p {src/{components,screens,services,utils},android,ios}
        touch package.json App.tsx
        ;;
    "game")
        echo "🎮 Setting up game project..."
        mkdir -p {Assets/{Scripts,Scenes,Prefabs},Builds}
        touch Assets/Scripts/GameManager.cs
        ;;
    "ml")
        echo "🤖 Setting up ML project..."
        mkdir -p {src/{models,data,training},notebooks,tests}
        touch src/main.py requirements.txt
        ;;
    "blockchain")
        echo "⛓️ Setting up blockchain project..."
        mkdir -p {contracts,scripts,tests,frontend}
        touch contracts/Contract.sol package.json
        ;;
    "iot")
        echo "🌐 Setting up IoT project..."
        mkdir -p {src/{sensors,communication,data},firmware,config}
        touch src/main.py requirements.txt
        ;;
esac

# Create README
cat > README.md << EOF
# $PROJECT_NAME

## Project Type: $PROJECT_TYPE

## Getting Started
1. Install dependencies
2. Configure environment
3. Start development

## Cursor Rules
This project uses comprehensive Cursor rules for:
- Autonomous development
- Visual intelligence
- Multi-agent coordination
- User research
- Quality assurance

## Development
- Follow all rules in .cursor/rules/
- Maintain visual consistency
- Ensure autonomous operation
- Prioritize user experience
EOF

echo "✅ Project $PROJECT_NAME created successfully!"
echo "📁 Project structure:"
tree -L 3

echo "🎯 Next steps:"
echo "1. cd $PROJECT_NAME"
echo "2. Install dependencies"
echo "3. Start coding with Cursor AI assistance"
