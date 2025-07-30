#!/usr/bin/env python3
"""
Quick start script for Telegram File Bot
This script will install dependencies and start the bot
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_bot_token():
    """Check if bot token is configured"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("📝 Please create .env file with your bot token:")
        print("BOT_TOKEN=your_bot_token_here")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
        if "your_bot_token_here" in content or "BOT_TOKEN=" not in content:
            print("❌ Bot token not configured!")
            print("📝 Please edit .env file with your actual bot token")
            return False
    
    print("✅ Bot token is configured!")
    return True

def create_directories():
    """Create necessary directories"""
    directories = ["files", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created!")

def start_bot():
    """Start the Telegram bot"""
    print("🤖 Starting Telegram File Bot...")
    print("📝 Bot is running! Press Ctrl+C to stop.")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "bot.py"])
    except KeyboardInterrupt:
        print("\n⏹️  Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

def main():
    print("🚀 Telegram File Bot - Quick Start")
    print("=" * 40)
    
    # Create directories
    create_directories()
    
    # Check bot token
    if not check_bot_token():
        return
    
    # Install dependencies
    if not install_requirements():
        return
    
    # Start the bot
    start_bot()

if __name__ == "__main__":
    main()