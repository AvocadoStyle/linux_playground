#!/bin/bash
# Ollama Setup Script for Linux
# Run: chmod +x setup_ollama_linux.sh && ./setup_ollama_linux.sh

MODEL="${1:-llama3.2}"

echo "============================="
echo "  Ollama Setup - Linux"
echo "============================="

# Step 1: Check if Ollama is installed
echo ""
echo "[1/4] Checking if Ollama is installed..."
if command -v ollama &> /dev/null; then
    echo "  Ollama found: $(ollama --version)"
else
    echo "  Ollama not found. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
    if [ $? -ne 0 ]; then
        echo "  ERROR: Installation failed"
        exit 1
    fi
    echo "  Ollama installed successfully"
fi

# Step 2: Check if Ollama server is running
echo ""
echo "[2/4] Checking Ollama server..."
if curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo "  Ollama server is running"
else
    echo "  Starting Ollama server..."
    ollama serve &> /dev/null &
    sleep 3
    echo "  Ollama server started (PID: $!)"
fi

# Step 3: Pull model
echo ""
echo "[3/4] Pulling model: $MODEL ..."
ollama pull "$MODEL"
if [ $? -eq 0 ]; then
    echo "  Model '$MODEL' ready"
else
    echo "  ERROR: Failed to pull model '$MODEL'"
    exit 1
fi

# Step 4: Install Python client
echo ""
echo "[4/4] Installing Python ollama client..."
PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$PROJECT_ROOT"
if [ -f "pyproject.toml" ]; then
    if command -v poetry &> /dev/null; then
        poetry add ollama 2>/dev/null && echo "  Python ollama client installed via poetry" || {
            pip install ollama 2>/dev/null
            echo "  Python ollama client installed via pip"
        }
    else
        pip install ollama
        echo "  Python ollama client installed via pip"
    fi
else
    pip install ollama
    echo "  Python ollama client installed via pip"
fi

# Done
echo ""
echo "============================="
echo "  Setup Complete!"
echo "  Model: $MODEL"
echo "  Server: http://localhost:11434"
echo "============================="
