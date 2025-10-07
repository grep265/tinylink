#!/bin/bash

VENV_NAME="tinylink-env"

echo "Creating virtual environment '$VENV_NAME'..."
python3 -m venv $VENV_NAME
echo "Virtual environment created."
source $VENV_NAME/bin/activate
echo "Virtual environment activated."

echo "Installing packages..."
pip install llama-cpp-python pymavlink huggingface_hub mavsdk
echo "Packages installed."

echo "Downloading model ..."
hf download the-robot-ai/TinyLink --local-dir models --include TinyLink.gguf
echo "Download complete."