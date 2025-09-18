#!/bin/bash

# Cursor Rules Update Script
# Updates all Cursor rules to latest versions

set -e

echo "🔄 Updating Cursor rules..."

# Backup existing rules
if [ -d ".cursor/rules" ]; then
    echo "📦 Backing up existing rules..."
    cp -r .cursor/rules .cursor/rules.backup.$(date +%Y%m%d_%H%M%S)
fi

# Update rules from template
if [ -d "$HOME/.cursor/rules" ]; then
    echo "📥 Updating rules from template..."
    cp -r "$HOME/.cursor/rules"/* .cursor/rules/
    echo "✅ Rules updated successfully!"
else
    echo "❌ Template rules not found at $HOME/.cursor/rules"
    exit 1
fi

# Update .cursorrules
if [ -f "$HOME/.cursorrules" ]; then
    echo "📝 Updating .cursorrules..."
    cp "$HOME/.cursorrules" .
    echo "✅ .cursorrules updated!"
fi

# Update settings
if [ -f "$HOME/.cursor/settings.json" ]; then
    echo "⚙️ Updating Cursor settings..."
    cp "$HOME/.cursor/settings.json" .cursor/
    echo "✅ Settings updated!"
fi

echo "🎉 All Cursor rules updated successfully!"
echo "📋 Updated components:"
echo "  - Rules directory: ✅"
echo "  - .cursorrules: ✅"
echo "  - Settings: ✅"
echo ""
echo "🔄 Restart Cursor to apply changes"
