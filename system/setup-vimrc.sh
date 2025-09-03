#!/bin/bash

# Standalone Vim Configuration Installer
# Everything is contained within this single script

set -e  # Exit on error

# Configuration - Edit this section with your details
VIMRC_GIST_URL="https://gist.githubusercontent.com/aqrpole/3e32a64e3a8677df8506cfc9573cda58/raw/887fc1cb2a2a3d08a6b5b7decc0ae763964b01be/python-vimrc.txt"
GRUVBOX_INSTALL=true
BACKUP_EXISTING=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Vim is installed
check_vim_installed() {
    if ! command -v vim &> /dev/null; then
        print_error "Vim is not installed. Please install Vim first."
        exit 1
    fi
    print_status "Vim is installed"
}

# Check if git is installed
check_git_installed() {
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    print_status "Git is installed"
}

# Check if curl is installed
check_curl_installed() {
    if ! command -v curl &> /dev/null; then
        print_error "Curl is not installed. Please install curl first."
        exit 1
    fi
    print_status "Curl is installed"
}

# Backup existing configuration
backup_existing_config() {
    if [ "$BACKUP_EXISTING" = true ]; then
        print_step "Backing up existing Vim configuration..."
        local timestamp=$(date +%Y%m%d%H%M%S)
        
        if [ -f ~/.vimrc ]; then
            mv ~/.vimrc ~/.vimrc.backup.$timestamp
            print_status "Existing .vimrc backed up to ~/.vimrc.backup.$timestamp"
        fi
        
        if [ -d ~/.vim ]; then
            mv ~/.vim ~/.vim.backup.$timestamp
            print_status "Existing .vim directory backed up to ~/.vim.backup.$timestamp"
        fi
    else
        print_warning "Skipping backup of existing configuration"
    fi
}

# Install Vundle
install_vundle() {
    print_step "Installing Vundle..."
    mkdir -p ~/.vim/bundle
    
    if [ -d ~/.vim/bundle/Vundle.vim ]; then
        print_status "Vundle already exists, updating..."
        cd ~/.vim/bundle/Vundle.vim && git pull && cd - > /dev/null
    else
        git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim
    fi
    
    if [ $? -eq 0 ]; then
        print_status "Vundle installed/updated successfully"
    else
        print_error "Failed to install Vundle"
        exit 1
    fi
}

# Download and setup .vimrc
setup_vimrc() {
    print_step "Downloading and setting up .vimrc..."
    
    if [ -z "$VIMRC_GIST_URL" ]; then
        print_error "VIMRC_GIST_URL is not set. Please edit the script and add your Gist URL."
        exit 1
    fi
    
    curl -s -o ~/.vimrc "$VIMRC_GIST_URL"
    
    if [ $? -eq 0 ] && [ -s ~/.vimrc ]; then
        print_status ".vimrc downloaded successfully from $VIMRC_GIST_URL"
    else
        print_error "Failed to download .vimrc from $VIMRC_GIST_URL"
        exit 1
    fi
    
    # Ensure Gruvbox is specified in the vimrc if requested
    if [ "$GRUVBOX_INSTALL" = true ] && ! grep -q "gruvbox" ~/.vimrc; then
        print_status "Adding Gruvbox color scheme to .vimrc..."
        echo '' >> ~/.vimrc
        echo '" Gruvbox color scheme' >> ~/.vimrc
        echo 'Plugin "morhetz/gruvbox"' >> ~/.vimrc
        echo 'colorscheme gruvbox' >> ~/.vimrc
        echo 'set background=dark' >> ~/.vimrc
    fi
}

# Install plugins
install_plugins() {
    print_step "Installing Vim plugins (this may take a while)..."
    
    # Create a temporary vim script to install plugins
    cat > /tmp/install_plugins.vim << EOF
set shell=/bin/bash
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
PluginInstall
call vundle#end()
qall
EOF
    
    vim -es -u ~/.vimrc /tmp/install_plugins.vim
    
    if [ $? -eq 0 ]; then
        print_status "Plugins installed successfully"
    else
        print_warning "There were issues during plugin installation"
        print_warning "Trying alternative installation method..."
        vim +PluginInstall +qall
    fi
    
    rm -f /tmp/install_plugins.vim
}

# Install Gruvbox directly if needed
install_gruvbox() {
    if [ "$GRUVBOX_INSTALL" = true ] && [ ! -d ~/.vim/bundle/gruvbox ]; then
        print_step "Installing Gruvbox color scheme directly..."
        git clone https://github.com/morhetz/gruvbox.git ~/.vim/bundle/gruvbox
        print_status "Gruvbox color scheme installed"
    fi
}

# Set terminal for better color support
setup_terminal() {
    print_step "Setting up terminal support..."
    
    # Check if terminal supports 256 colors
    if [ "$TERM" != "xterm-256color" ]; then
        print_warning "Your terminal may not support 256 colors"
        print_warning "Add 'export TERM=xterm-256color' to your ~/.bashrc or ~/.zshrc"
    fi
}

# Main installation function
main_install() {
    print_step "Starting Vim configuration installation..."
    print_status "Gist URL: $VIMRC_GIST_URL"
    print_status "Install Gruvbox: $GRUVBOX_INSTALL"
    print_status "Backup existing: $BACKUP_EXISTING"
    
    check_vim_installed
    check_git_installed
    check_curl_installed
    backup_existing_config
    install_vundle
    setup_vimrc
    install_plugins
    install_gruvbox
    setup_terminal
    
    print_status "Installation completed successfully!"
    echo ""
    print_warning "If you see any formatting issues, you may need to:"
    print_warning "1. Use a terminal that supports 256 colors (iTerm2, GNOME Terminal, etc.)"
    print_warning "2. Add 'export TERM=xterm-256color' to your shell configuration file"
    print_warning "3. Restart your terminal after making changes"
    echo ""
    print_status "You can start Vim with: vim"
}

# Display help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Install Vim configuration from a GitHub Gist"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -n, --no-backup     Skip backing up existing configuration"
    echo "  -g, --no-gruvbox    Skip Gruvbox color scheme installation"
    echo ""
    echo "Edit the script to change the GIST URL and other settings."
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -n|--no-backup)
            BACKUP_EXISTING=false
            shift
            ;;
        -g|--no-gruvbox)
            GRUVBOX_INSTALL=false
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run the installation
main_install
