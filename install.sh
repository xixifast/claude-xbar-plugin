#!/bin/bash
# Claude xbar Plugin Installer

set -e

PLUGIN_NAME="claude-usage.10s.py"
PLUGIN_URL="https://raw.githubusercontent.com/YOUR_USERNAME/claude-xbar-plugin/main/${PLUGIN_NAME}"
XBAR_PLUGIN_DIR="$HOME/Library/Application Support/xbar/plugins"

echo "🤖 Claude xbar Plugin Installer"
echo "=============================="
echo ""

# Check if xbar is installed
if ! command -v xbar &> /dev/null && [ ! -d "/Applications/xbar.app" ]; then
    echo "❌ xbar is not installed."
    echo ""
    echo "Please install xbar first:"
    echo "  brew install --cask xbar"
    echo ""
    echo "Or download from: https://xbarapp.com"
    exit 1
fi

# Create plugins directory if it doesn't exist
if [ ! -d "$XBAR_PLUGIN_DIR" ]; then
    echo "📁 Creating xbar plugins directory..."
    mkdir -p "$XBAR_PLUGIN_DIR"
fi

# Check if plugin already exists
if [ -f "$XBAR_PLUGIN_DIR/$PLUGIN_NAME" ]; then
    echo "⚠️  Plugin already exists. Overwrite? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
fi

# Download plugin
echo "📥 Downloading plugin..."
if curl -sSL "$PLUGIN_URL" -o "$XBAR_PLUGIN_DIR/$PLUGIN_NAME"; then
    echo "✅ Plugin downloaded successfully"
else
    echo "❌ Failed to download plugin"
    exit 1
fi

# Make executable
chmod +x "$XBAR_PLUGIN_DIR/$PLUGIN_NAME"
echo "✅ Plugin made executable"

# Check for Claude data directory
if [ ! -d "$HOME/.claude/projects" ]; then
    echo ""
    echo "⚠️  Warning: Claude data directory not found at ~/.claude/projects"
    echo "   The plugin will show 'No Claude usage found' until you have usage data."
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "📊 The Claude usage monitor should now appear in your menu bar."
echo "   If not, please refresh xbar or restart the app."
echo ""
echo "💡 Tips:"
echo "   - Click the menu bar item to see detailed usage"
echo "   - The plugin updates every 10 seconds"
echo "   - To change refresh rate, rename the file (e.g., claude-usage.1m.py)"
echo ""
echo "🐛 Issues? Visit: https://github.com/YOUR_USERNAME/claude-xbar-plugin"