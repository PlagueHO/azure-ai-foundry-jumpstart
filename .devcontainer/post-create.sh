#!/bin/bash
# Post-create command script for Azure AI Foundry Jumpstart dev container
# This script is executed after the dev container is created

set -e  # Exit on any error

echo "🚀 Running post-create setup for Azure AI Foundry Jumpstart devcontainer..."

# Configure Git settings
echo "📝 Configuring Git settings..."
git config --global core.autocrlf input
git config --global core.fileMode false

# Install Python development dependencies
echo "🐍 Installing Python development dependencies..."
pip3 install -r ./requirements-dev.txt

# Ensure Node.js tools are properly sourced and available
echo "🔧 Setting up Node.js environment..."
# Source nvm to ensure it's available
if [ -s "${NVM_DIR}/nvm.sh" ]; then
    . "${NVM_DIR}/nvm.sh"
    echo "  NVM sourced successfully"
else
    echo "  Warning: NVM not found at ${NVM_DIR}/nvm.sh"
fi

# Verify installations
echo "✅ Verifying installations..."
echo "  Node.js version: $(node --version 2>/dev/null || echo 'Not found')"
echo "  NPM version: $(npm --version 2>/dev/null || echo 'Not found')"
echo "  NPX version: $(npx --version 2>/dev/null || echo 'Not found')"
echo "  NPX location: $(which npx 2>/dev/null || echo 'Not found')"
echo "  Python version: $(python3 --version 2>/dev/null || echo 'Not found')"

# Configure GitHub Copilot in the CLI alias (ghcs) for bash
echo "🤖 Configuring GitHub Copilot CLI alias..."
if command -v gh >/dev/null 2>&1; then
    # Ensure ~/.bashrc exists
    touch ~/.bashrc
    # Add alias if not already present
    if ! grep -q 'gh copilot alias -- bash' ~/.bashrc; then
        echo 'eval "$(gh copilot alias -- bash)"' >> ~/.bashrc
        echo "  Added ghcs alias to ~/.bashrc"
    else
        echo "  ghcs alias already present in ~/.bashrc"
    fi
    # Source it for current session (if we're in bash)
    if [ -n "$BASH_VERSION" ]; then
        # shellcheck source=/dev/null
        . ~/.bashrc
    fi
    echo "  gh version: $(gh --version | head -n 1)"
else
    echo "  Warning: GitHub CLI (gh) not found; skipping ghcs alias setup."
fi

echo "🎉 Post-create setup completed successfully!"
