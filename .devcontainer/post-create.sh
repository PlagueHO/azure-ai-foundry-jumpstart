#!/bin/bash
# Post-create command script for Azure AI Foundry Jumpstart dev container
# This script is executed after the dev container is created

set -e  # Exit on any error

echo "🚀 Running post-create setup for Azure AI Foundry Jumpstart..."

# Configure Git settings
echo "📝 Configuring Git settings..."
git config --global core.autocrlf input
git config --global core.fileMode false

# Install Python development dependencies
echo "🐍 Installing Python development dependencies..."
pip3 install -r /workspaces/azure-ai-foundry-jumpstart/requirements-dev.txt

# Ensure Node.js tools are properly sourced and available
echo "🔧 Setting up Node.js environment..."
# Source nvm to ensure it's available
if [ -s "${NVM_DIR}/nvm.sh" ]; then
    . "${NVM_DIR}/nvm.sh"
    echo "  NVM sourced successfully"
else
    echo "  Warning: NVM not found at ${NVM_DIR}/nvm.sh"
fi

# Make the npx wrapper executable
chmod +x /workspaces/azure-ai-foundry-jumpstart/.devcontainer/npx-wrapper.sh

# Create symlinks for npx to ensure it's available globally for all users
if command -v npx >/dev/null 2>&1; then
    NPX_PATH=$(which npx)
    echo "  Found npx at: $NPX_PATH"
    
    # Create a global symlink if npx is not already in /usr/local/bin
    if [ "$NPX_PATH" != "/usr/local/bin/npx" ]; then
        sudo ln -sf "$NPX_PATH" /usr/local/bin/npx
        echo "  Created global symlink for npx"
    fi
    
    # Also create a backup symlink to our wrapper
    sudo ln -sf /workspaces/azure-ai-foundry-jumpstart/.devcontainer/npx-wrapper.sh /usr/local/bin/npx-mcp
    echo "  Created MCP-specific npx wrapper"
else
    echo "  Warning: npx not found in PATH, using wrapper only"
    sudo ln -sf /workspaces/azure-ai-foundry-jumpstart/.devcontainer/npx-wrapper.sh /usr/local/bin/npx
    sudo ln -sf /workspaces/azure-ai-foundry-jumpstart/.devcontainer/npx-wrapper.sh /usr/local/bin/npx-mcp
fi

# Verify installations
echo "✅ Verifying installations..."
echo "  Node.js version: $(node --version 2>/dev/null || echo 'Not found')"
echo "  NPM version: $(npm --version 2>/dev/null || echo 'Not found')"
echo "  NPX version: $(npx --version 2>/dev/null || echo 'Not found')"
echo "  NPX location: $(which npx 2>/dev/null || echo 'Not found')"
echo "  NPX-MCP wrapper: $(which npx-mcp 2>/dev/null || echo 'Not found')"
echo "  Python version: $(python3 --version 2>/dev/null || echo 'Not found')"

# Test MCP server availability
echo "🧪 Testing MCP server package availability..."
if command -v npx >/dev/null 2>&1; then
    echo "  Testing @modelcontextprotocol/server-filesystem availability..."
    timeout 10 npx -y @modelcontextprotocol/server-filesystem --help >/dev/null 2>&1 && echo "    ✅ Available" || echo "    ⚠️  May need internet connection"
    
    echo "  Testing @playwright/mcp availability..."
    timeout 10 npx -y @playwright/mcp --help >/dev/null 2>&1 && echo "    ✅ Available" || echo "    ⚠️  May need internet connection"
else
    echo "  ⚠️  Cannot test - npx not available"
fi

echo "🎉 Post-create setup completed successfully!"
