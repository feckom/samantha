@echo off
echo Installing required Python packages...

:: Install Python packages
pip install ollama
pip install kokoro-onnx
pip install simpleaudio
pip install nltk
pip install colorama
pip install configparser
pip install asyncio

:: Download NLTK data
python -c "import nltk; nltk.download('punkt', quiet=True)"

echo Installation complete!
pause