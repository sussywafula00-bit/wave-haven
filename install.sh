#!/bin/bash
# Wave-Haven Installation Script
# Version: 1.0.0

set -e

echo "🌊 Wave-Haven Installation Script"
echo "================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking prerequisites..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo -e "${RED}❌ Python 3.8+ required. Found: $python_version${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $python_version found${NC}"

# Check if OpenClaw is installed
if ! command -v claw &> /dev/null; then
    echo -e "${YELLOW}⚠️  OpenClaw not found. Please install OpenClaw first.${NC}"
    echo "   Visit: https://docs.openclaw.ai/installation"
    exit 1
fi
echo -e "${GREEN}✓ OpenClaw found${NC}"

# Installation directory
INSTALL_DIR="${HOME}/.openclaw/workspace_shared/skills/wave-haven"
BACKUP_DIR="${HOME}/.openclaw/workspace_shared/skills/wave-haven-backup-$(date +%Y%m%d-%H%M%S)"

# Backup existing installation
if [ -d "$INSTALL_DIR" ]; then
    echo "📦 Backing up existing installation..."
    mv "$INSTALL_DIR" "$BACKUP_DIR"
    echo -e "${GREEN}✓ Backup created: $BACKUP_DIR${NC}"
fi

# Create installation directory
echo "📁 Creating installation directory..."
mkdir -p "$INSTALL_DIR"

# Copy files
echo "📂 Installing Wave-Haven..."
cp -r wave/* "$INSTALL_DIR/"
cp -r haven/* "$INSTALL_DIR/"
cp -r shared/* "$INSTALL_DIR/"
cp -r agents/* "$INSTALL_DIR/"

# Set permissions
chmod +x "$INSTALL_DIR"/*.sh
chmod +x "$INSTALL_DIR"/**/*.py 2>/dev/null || true

# Create configuration
echo "⚙️  Creating default configuration..."
CONFIG_DIR="${HOME}/.openclaw/config"
mkdir -p "$CONFIG_DIR"

if [ ! -f "$CONFIG_DIR/wave-haven.yaml" ]; then
cat > "$CONFIG_DIR/wave-haven.yaml" << 'EOF'
# Wave-Haven Configuration
system:
  base_path: "~/.openclaw"
  log_level: "INFO"

wave:
  enabled: true
  max_concurrent_waves: 10
  default_timeout: 3600
  port: 8000

haven:
  enabled: true
  memory_layers: 4
  auto_optimize: true
  semantic_search: true

agents:
  nova:
    enabled: true
    role: coordinator
  luna:
    enabled: true
    role: memory_keeper
  dreamnova:
    enabled: true
    role: explorer
  kiki:
    enabled: true
    role: optimizer
  coco:
    enabled: true
    role: executor

logging:
  level: "INFO"
  file: "~/.openclaw/logs/wave-haven.log"
EOF
    echo -e "${GREEN}✓ Default configuration created${NC}"
else
    echo -e "${YELLOW}⚠️  Configuration file already exists, skipping${NC}"
fi

# Create necessary directories
echo "📂 Creating system directories..."
mkdir -p "${HOME}/.openclaw/shared/wave-haven/waves"
mkdir -p "${HOME}/.openclaw/shared/wave-haven/haven"
mkdir -p "${HOME}/.openclaw/logs"
mkdir -p "${HOME}/.openclaw/agents"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -q -r "$INSTALL_DIR/requirements.txt"

echo ""
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}✅ Wave-Haven installed successfully!${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo "📍 Installation directory: $INSTALL_DIR"
echo "⚙️  Configuration file: $CONFIG_DIR/wave-haven.yaml"
echo ""
echo "🚀 Quick Start:"
echo "   1. Start Wave:  claw skills run wave-haven --start-wave"
echo "   2. Start Haven: claw skills run wave-haven --start-haven"
echo "   3. Check status: claw skills run wave-haven --status"
echo ""
echo "📖 Documentation: https://github.com/sussywafula00-bit/wave-haven#readme"
echo ""
