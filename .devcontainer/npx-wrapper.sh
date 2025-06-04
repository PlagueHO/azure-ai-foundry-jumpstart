#!/bin/bash
# NPX wrapper script for MCP servers
# This script ensures npx is available regardless of the environment

# Try different locations where npx might be installed
NPX_LOCATIONS=(
    "/usr/local/bin/npx"
    "/usr/bin/npx"
    "$(which npx 2>/dev/null)"
    "${NVM_DIR}/current/bin/npx"
    "/root/.nvm/current/bin/npx"
    "/home/vscode/.nvm/current/bin/npx"
)

# Function to find npx
find_npx() {
    for location in "${NPX_LOCATIONS[@]}"; do
        if [ -n "$location" ] && [ -x "$location" ]; then
            echo "$location"
            return 0
        fi
    done
    
    # If npx is not found, try to source nvm and find it
    if [ -s "${NVM_DIR}/nvm.sh" ]; then
        . "${NVM_DIR}/nvm.sh"
        local npx_path=$(which npx 2>/dev/null)
        if [ -n "$npx_path" ] && [ -x "$npx_path" ]; then
            echo "$npx_path"
            return 0
        fi
    fi
    
    return 1
}

# Find and execute npx
NPX_PATH=$(find_npx)
if [ $? -eq 0 ]; then
    exec "$NPX_PATH" "$@"
else
    echo "Error: npx not found in any expected location" >&2
    echo "Checked locations:" >&2
    printf '  %s\n' "${NPX_LOCATIONS[@]}" >&2
    exit 1
fi