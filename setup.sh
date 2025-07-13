#!/bin/bash

# Plausible Stats Aggregator Setup Script

echo "🚀 Setting up Plausible Stats Aggregator"
echo "========================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3.7+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not found. Please install pip first."
    exit 1
fi

echo "✅ pip3 found"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit the .env file and add your Plausible API keys:"
    echo "   - PLAUSIBLE_SITES_API_KEY"
    echo "   - PLAUSIBLE_STATS_API_KEY"
    echo ""
    echo "   You can get these keys from your Plausible account:"
    echo "   Settings → API Keys → New API Key"
    echo ""
else
    echo "ℹ️  .env file already exists, skipping..."
fi

# Create output directory
mkdir -p output
echo "✅ Output directory created"

# Create logs directory
mkdir -p logs
echo "✅ Logs directory created"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your Plausible API keys"
echo "2. Run the script: python3 main.py"
echo ""
echo "For help getting API keys, see README.md"
