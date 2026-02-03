#!/bin/bash

echo "=========================================="
echo "   ITU Ders Secici - Quick Setup (Bash)"
echo "=========================================="

# 1. Check/Install Git
if ! command -v git &> /dev/null; then
    echo "[INFO] 'Git' not found. Attempting to install..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt &> /dev/null; then
            sudo apt update && sudo apt install -y git
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y git
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm git
        elif command -v apk &> /dev/null; then
            sudo apk add git
        else
            echo "[ERROR] Could not detect package manager. Please install git manually."
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
             brew install git
        else
             echo "[INFO] Prompting for XCode command line tools..."
             xcode-select --install
        fi
    else
         echo "[ERROR] Unsupported OS for automatic git install. Please install git manually."
         exit 1
    fi
fi

# 2. Check for Project/Clone
if [ ! -f "Justfile" ]; then
    echo "[INFO] Justfile not found. Cloning repository..."
    git clone https://github.com/AtaTrkgl/itu-ders-secici
    cd itu-ders-secici || { echo "[ERROR] Failed to enter directory."; exit 1; }
    if [ ! -f "Justfile" ]; then
        echo "[ERROR] Justfile not found after cloning."
        exit 1
    fi
    echo "[INFO] Entered project directory."
fi

# 3. Install Just
if ! command -v just &> /dev/null; then
    echo "[INFO] 'Just' not found. Installing..."
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Try apt first for linux
        if command -v apt &> /dev/null; then
            echo "Detected apt package manager."
             # Just is not always in default repos, using official install script is safer mostly or snap
            curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin || \
            (echo "Failed to install to global bin. Installing to local..." && \
             curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin && \
             export PATH="$HOME/.local/bin:$PATH")
        else
             curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin
             export PATH="$HOME/.local/bin:$PATH"
        fi
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
        echo "Detected Windows (Git Bash/MSYS). Checking for Winget..."
        if command -v winget &> /dev/null; then
            winget install -e --id Casey.Just --accept-source-agreements --accept-package-agreements
            # Refresh path rough simulation for bash
            echo "[INFO] Refreshing PATH for Just..."
            echo "[INFO] You may need to restart your terminal for changes to take effect."
            export PATH="/c/Program Files/Just:$PATH" 
        else
            echo "[ERROR] Winget not found. Please install Just manually."
            exit 1
        fi
    fi
else
    echo "[INFO] 'Just' is already installed."
fi

# 4. Run system-reqs
echo ""
echo "[INFO] Running system requirements..."
just system-reqs

# 5. Refresh Path (Crucial for uv/python if just installed)
# In bash, we can't easily effect the parent shell, but we can try source or export for this session
if [[ -d "$HOME/.local/bin" ]]; then
    export PATH="$HOME/.local/bin:$PATH"
fi
if [[ -d "/c/Users/$USER/AppData/Local/Programs/Python/Python3*" ]]; then
    # Rough attempt to add python path if just installed on Windows
    export PATH=$(find /c/Users/$USER/AppData/Local/Programs/Python -name "Python3*" -type d | head -n 1):$PATH
fi

# 6. Install Dependencies
echo ""
echo "[INFO] Installing Project Dependencies..."
just install

echo ""
echo "=========================================="
echo "   Setup Complete!" 
echo "   Run 'just init' to configure."
echo "=========================================="