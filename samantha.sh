#!/bin/bash

# Variables
VENV_DIR=".venv"
REQUIREMENTS_FILE="requirements.txt"

# Create a virtual environment
echo "Creating virtual environment in: $VENV_DIR"
python3 -m venv "$VENV_DIR"

# Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip and setuptools
echo "Upgrading pip and setuptools..."
pip install --upgrade pip setuptools

# Install Python packages from requirements.txt
if [[ -f "$REQUIREMENTS_FILE" ]]; then
    echo "Installing Python packages from $REQUIREMENTS_FILE..."
    pip install -r "$REQUIREMENTS_FILE"
else
    echo "Creating $REQUIREMENTS_FILE and installing required packages..."
    cat <<EOF > "$REQUIREMENTS_FILE"
concurrent-log-handler
asyncio
ollama
kokoro-onnx
simpleaudio
nltk
colorama
configparser
EOF
    pip install -r "$REQUIREMENTS_FILE"
fi

# Install nltk data
echo "Downloading nltk data..."
python3 - <<EOF
import nltk
nltk.download('punkt')
EOF

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "ffmpeg is not installed. Installing ffmpeg..."
    sudo apt update
    sudo apt install -y ffmpeg
fi

echo "Environment setup complete!"
echo "To activate the virtual environment, run: source $VENV_DIR/bin/activate"