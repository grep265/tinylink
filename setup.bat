@echo off
SET VENV_NAME=tinylink-env

echo Creating virtual environment '%VENV_NAME%'...
python -m venv %VENV_NAME%
echo Virtual environment created.

echo Activating virtual environment...
call %VENV_NAME%\Scripts\activate
echo Virtual environment activated.

echo Installing packages...
pip install llama-cpp-python pymavlink huggingface_hub
echo Packages installed.

echo Downloading model ...
hf download the-robot-ai/TinyLink --local-dir models --include TinyLink.gguf
echo Download complete.