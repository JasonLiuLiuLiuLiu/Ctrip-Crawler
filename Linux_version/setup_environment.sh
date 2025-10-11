#!/bin/bash

###############################################################################
# Ctrip Flight Scraper - Environment Setup Script
# Description: Automated environment setup for Ubuntu 24.04 Desktop (minimal install)
# Author: Auto-generated
# Date: 2025-10-11
###############################################################################

set -e  # Exit on error

# Color definitions for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root or with sudo
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "This script requires root privileges. Please run with sudo:"
        log_error "sudo bash $0"
        exit 1
    fi
}

# Get the actual user (when script is run with sudo)
ACTUAL_USER=${SUDO_USER:-$USER}
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

log_info "================================================================"
log_info "  Ctrip Flight Scraper - Environment Setup"
log_info "  Target OS: Ubuntu 24.04 Desktop"
log_info "  User: $ACTUAL_USER"
log_info "  Home: $ACTUAL_HOME"
log_info "================================================================"

# Check root privileges
check_root

###############################################################################
# Step 1: Update system and install basic dependencies
###############################################################################
log_info "Step 1: Updating system and installing basic dependencies..."

apt-get update -y
apt-get upgrade -y

# Install essential build tools and development dependencies
apt-get install -y \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    curl \
    wget \
    gnupg \
    lsb-release \
    git \
    unzip \
    xz-utils

log_success "System updated and basic dependencies installed"

###############################################################################
# Step 2: Install Python 3 and pip
###############################################################################
log_info "Step 2: Installing Python 3 and pip..."

apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    python3-setuptools

# Verify Python installation
PYTHON_VERSION=$(python3 --version)
log_success "Python installed: $PYTHON_VERSION"

# Upgrade pip
python3 -m pip install --upgrade pip setuptools wheel

log_success "Python and pip installed successfully"

###############################################################################
# Step 3: Install system libraries required by Python packages
###############################################################################
log_info "Step 3: Installing system libraries for Python packages..."

# libmagic for python-magic
apt-get install -y \
    libmagic1 \
    libmagic-dev \
    file

# Additional libraries for data processing
apt-get install -y \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev

log_success "System libraries installed"

###############################################################################
# Step 4: Install Chrome/Chromium browser
###############################################################################
log_info "Step 4: Installing Google Chrome..."

# Download and install Google Chrome
CHROME_DEB="google-chrome-stable_current_amd64.deb"
if [ ! -f "/tmp/$CHROME_DEB" ]; then
    wget -q -O "/tmp/$CHROME_DEB" https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
fi

# Install Chrome and its dependencies
apt-get install -y "/tmp/$CHROME_DEB" || true
apt-get install -f -y  # Fix any dependency issues

# Verify Chrome installation
if command -v google-chrome &> /dev/null; then
    CHROME_VERSION=$(google-chrome --version)
    log_success "Chrome installed: $CHROME_VERSION"
else
    log_error "Chrome installation failed"
    exit 1
fi

# Clean up
rm -f "/tmp/$CHROME_DEB"

# Install additional dependencies for headed mode (optional)
log_info "Installing optional dependencies for headed mode..."
apt-get install -y \
    xvfb \
    x11-utils \
    xauth \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    libnss3 || log_warning "Some optional packages could not be installed (non-critical)"

log_success "Optional dependencies installed (for headed mode support)"

###############################################################################
# Step 5: Install ChromeDriver
###############################################################################
log_info "Step 5: Installing ChromeDriver..."

# Get Chrome version
CHROME_MAJOR_VERSION=$(google-chrome --version | sed -E 's/.* ([0-9]+)\..*/\1/')
log_info "Chrome major version: $CHROME_MAJOR_VERSION"

# Install chromium-chromedriver which is compatible
apt-get install -y chromium-chromedriver

# Alternative: Download ChromeDriver directly
# We'll create a symlink to make sure it's in PATH
if [ -f "/usr/bin/chromedriver" ]; then
    log_success "ChromeDriver installed successfully"
    chromedriver --version || true
elif [ -f "/usr/lib/chromium-browser/chromedriver" ]; then
    ln -sf /usr/lib/chromium-browser/chromedriver /usr/local/bin/chromedriver
    log_success "ChromeDriver linked to /usr/local/bin/chromedriver"
else
    log_warning "ChromeDriver not found in expected locations, attempting to download..."
    
    # Download the latest ChromeDriver
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
    wget -q -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
    unzip -o /tmp/chromedriver.zip -d /tmp/
    mv /tmp/chromedriver /usr/local/bin/chromedriver
    chmod +x /usr/local/bin/chromedriver
    rm -f /tmp/chromedriver.zip
    
    log_success "ChromeDriver downloaded and installed"
fi

###############################################################################
# Step 6: Install network utilities for proxy functionality
###############################################################################
log_info "Step 6: Installing network utilities..."

apt-get install -y \
    iproute2 \
    iptables \
    net-tools \
    iputils-ping \
    dnsutils \
    netcat-openbsd \
    tcpdump

log_success "Network utilities installed"

###############################################################################
# Step 7: Configure IPv6 (required for proxy functionality)
###############################################################################
log_info "Step 7: Checking IPv6 configuration..."

# Enable IPv6 if disabled
if sysctl net.ipv6.conf.all.disable_ipv6 | grep -q "= 1"; then
    log_info "Enabling IPv6..."
    sysctl -w net.ipv6.conf.all.disable_ipv6=0
    sysctl -w net.ipv6.conf.default.disable_ipv6=0
    
    # Make it persistent
    cat >> /etc/sysctl.conf << EOF

# Enable IPv6 for Ctrip Scraper
net.ipv6.conf.all.disable_ipv6 = 0
net.ipv6.conf.default.disable_ipv6 = 0
EOF
    
    log_success "IPv6 enabled"
else
    log_success "IPv6 is already enabled"
fi

# Test IPv6 connectivity
if ip -6 addr show | grep -q "inet6"; then
    log_success "IPv6 interface detected"
else
    log_warning "No IPv6 interface found. Proxy functionality may be limited."
fi

###############################################################################
# Step 8: Create Python virtual environment
###############################################################################
log_info "Step 8: Creating Python virtual environment..."

VENV_PATH="$SCRIPT_DIR/venv"

# Remove existing venv if present
if [ -d "$VENV_PATH" ]; then
    log_warning "Removing existing virtual environment..."
    rm -rf "$VENV_PATH"
fi

# Create new venv as the actual user
sudo -u $ACTUAL_USER python3 -m venv "$VENV_PATH"

log_success "Virtual environment created at: $VENV_PATH"

###############################################################################
# Step 9: Install Python dependencies
###############################################################################
log_info "Step 9: Installing Python dependencies..."

# Activate venv and install packages
source "$VENV_PATH/bin/activate"

# Upgrade pip in venv
pip install --upgrade pip setuptools wheel

# Install project dependencies
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    log_info "Installing from requirements.txt..."
    pip install -r "$SCRIPT_DIR/requirements.txt"
else
    log_error "requirements.txt not found at $SCRIPT_DIR/requirements.txt"
    exit 1
fi

# Verify installations
log_info "Verifying Python package installations..."
pip list | grep -E "(pandas|selenium|magic)"

deactivate

log_success "Python dependencies installed successfully"

###############################################################################
# Step 10: Create necessary directories
###############################################################################
log_info "Step 10: Creating necessary directories..."

# Create directories as the actual user
sudo -u $ACTUAL_USER mkdir -p "$SCRIPT_DIR/data"
sudo -u $ACTUAL_USER mkdir -p "$SCRIPT_DIR/logs"
sudo -u $ACTUAL_USER mkdir -p "$SCRIPT_DIR/screenshot"
sudo -u $ACTUAL_USER mkdir -p "$SCRIPT_DIR/cookies"

log_success "Directories created successfully"

###############################################################################
# Step 11: Create configuration file if not exists
###############################################################################
log_info "Step 11: Checking configuration file..."

CONFIG_FILE="$SCRIPT_DIR/config.json"
CONFIG_EXAMPLE="$SCRIPT_DIR/config.json.example"

if [ ! -f "$CONFIG_FILE" ]; then
    if [ -f "$CONFIG_EXAMPLE" ]; then
        log_info "Creating config.json from example..."
        sudo -u $ACTUAL_USER cp "$CONFIG_EXAMPLE" "$CONFIG_FILE"
        log_warning "Please edit $CONFIG_FILE to configure your settings"
    else
        log_warning "config.json.example not found. Please create config.json manually"
    fi
else
    log_success "config.json already exists"
fi

###############################################################################
# Step 12: Create activation script
###############################################################################
log_info "Step 12: Creating activation script..."

ACTIVATE_SCRIPT="$SCRIPT_DIR/activate_env.sh"

cat > "$ACTIVATE_SCRIPT" << 'EOF'
#!/bin/bash

# Activation script for Ctrip Flight Scraper environment

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_PATH="$SCRIPT_DIR/venv"

if [ -d "$VENV_PATH" ]; then
    echo "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
    echo "Virtual environment activated!"
    echo "Python version: $(python --version)"
    echo "pip version: $(pip --version)"
    echo ""
    echo "To run the scraper:"
    echo "  python main.py"
    echo ""
    echo "To deactivate the environment:"
    echo "  deactivate"
else
    echo "ERROR: Virtual environment not found at $VENV_PATH"
    echo "Please run setup_environment.sh first"
    exit 1
fi
EOF

chmod +x "$ACTIVATE_SCRIPT"
chown $ACTUAL_USER:$ACTUAL_USER "$ACTIVATE_SCRIPT"

log_success "Activation script created: $ACTIVATE_SCRIPT"

###############################################################################
# Step 13: Create run script
###############################################################################
log_info "Step 13: Creating run script..."

RUN_SCRIPT="$SCRIPT_DIR/run.sh"

cat > "$RUN_SCRIPT" << 'EOF'
#!/bin/bash

# Run script for Ctrip Flight Scraper

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_PATH="$SCRIPT_DIR/venv"

echo "Starting Ctrip Flight Scraper..."

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "ERROR: Virtual environment not found. Please run setup_environment.sh first"
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Check if config.json exists
if [ ! -f "$SCRIPT_DIR/config.json" ]; then
    echo "ERROR: config.json not found. Please create it from config.json.example"
    exit 1
fi

# Run the main script
cd "$SCRIPT_DIR"
python main.py "$@"

# Deactivate virtual environment
deactivate
EOF

chmod +x "$RUN_SCRIPT"
chown $ACTUAL_USER:$ACTUAL_USER "$RUN_SCRIPT"

log_success "Run script created: $RUN_SCRIPT"

###############################################################################
# Step 14: System optimization and cleanup
###############################################################################
log_info "Step 14: System optimization and cleanup..."

# Clean up apt cache
apt-get autoremove -y
apt-get autoclean -y

log_success "System cleanup completed"

###############################################################################
# Step 15: Final verification
###############################################################################
log_info "Step 15: Final verification..."

echo ""
log_info "Verifying installations..."
echo "----------------------------------------"

# Python
if command -v python3 &> /dev/null; then
    echo "✓ Python: $(python3 --version)"
else
    echo "✗ Python: NOT FOUND"
fi

# Chrome
if command -v google-chrome &> /dev/null; then
    echo "✓ Chrome: $(google-chrome --version)"
else
    echo "✗ Chrome: NOT FOUND"
fi

# ChromeDriver
if command -v chromedriver &> /dev/null; then
    echo "✓ ChromeDriver: $(chromedriver --version 2>&1 | head -n 1)"
else
    echo "✗ ChromeDriver: NOT FOUND"
fi

# Virtual environment
if [ -d "$VENV_PATH" ]; then
    echo "✓ Virtual Environment: $VENV_PATH"
else
    echo "✗ Virtual Environment: NOT FOUND"
fi

# IPv6
if ip -6 addr show | grep -q "inet6"; then
    echo "✓ IPv6: Enabled"
else
    echo "✗ IPv6: Disabled or not available"
fi

echo "----------------------------------------"
echo ""

###############################################################################
# Installation Summary
###############################################################################
log_success "================================================================"
log_success "  Environment Setup Completed Successfully!"
log_success "================================================================"
echo ""
log_info "Next steps:"
echo "  1. Configure your settings:"
echo "     nano $SCRIPT_DIR/config.json"
echo ""
echo "  2. Activate the environment:"
echo "     source $SCRIPT_DIR/activate_env.sh"
echo ""
echo "  3. Run the scraper:"
echo "     cd $SCRIPT_DIR"
echo "     ./run.sh"
echo ""
echo "  OR simply run:"
echo "     cd $SCRIPT_DIR"
echo "     ./run.sh"
echo ""
log_warning "Important notes:"
echo "  - If you need to use proxy features, ensure you have IPv6 connectivity"
echo "  - Some operations may require root/sudo privileges (network interface creation)"
echo "  - Edit config.json to set your Ctrip account credentials if needed"
echo "  - Check logs/ directory for debugging information"
echo ""
log_info "Documentation:"
echo "  - Quick start: doc/QUICKSTART.md"
echo "  - Detailed setup: doc/环境配置说明.md"
echo "  - Dependencies: doc/DEPENDENCIES.md"
echo "  - Full documentation index: doc/README_SETUP.md"
echo ""
log_success "Setup completed at: $(date)"
echo ""

