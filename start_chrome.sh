#!/bin/bash
# Script to start Chrome in debug mode for CiteAgent

# Configuration
DEBUG_PORT=9222
USER_DATA_DIR="$HOME/ChromeProfile"

# Detect OS and set Chrome path
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    CHROME_PATH="google-chrome"
else
    echo "Unsupported OS. Please start Chrome manually."
    exit 1
fi

# Check if Chrome is already running
if lsof -Pi :$DEBUG_PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "Chrome is already running on port $DEBUG_PORT"
    echo "Please close all Chrome windows and try again."
    exit 1
fi

echo "Starting Chrome in debug mode..."
echo "Debug port: $DEBUG_PORT"
echo "User data directory: $USER_DATA_DIR"
echo ""
echo "After Chrome opens:"
echo "1. Navigate to https://www.overleaf.com"
echo "2. Log in and open your project"
echo "3. Run: python main.py --interactive"
echo ""

# Start Chrome
"$CHROME_PATH" \
    --remote-debugging-port=$DEBUG_PORT \
    --user-data-dir="$USER_DATA_DIR" \
    > /dev/null 2>&1 &

echo "Chrome started! (PID: $!)"
