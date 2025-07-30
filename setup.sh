#!/bin/bash

# Telegram File Bot Setup Script
set -e

echo "🤖 Telegram File Bot Setup"
echo "=========================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "📋 Checking dependencies..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

if ! command_exists pip3; then
    echo "❌ pip3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 and pip3 are available"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p files logs

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating environment configuration..."
    cp .env.example .env
    echo "📝 Please edit .env file with your bot token and configuration"
else
    echo "✅ Environment file already exists"
fi

# Set executable permissions
chmod +x file_manager.py
chmod +x setup.sh

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your Telegram bot token"
echo "2. Add files using: python3 file_manager.py add <file_path>"
echo "3. Start the bot: python3 bot.py"
echo ""
echo "🔗 For 24/7 deployment:"
echo "   Using Docker: docker-compose up -d"
echo "   Using systemd: sudo systemctl enable telegram-file-bot"
echo ""
echo "📖 For more information, check the README.md file"