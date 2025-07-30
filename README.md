# Telegram File Bot 🤖

A powerful Telegram bot that allows you to distribute files to your members through special links. When users click on your custom links, they get redirected to your Telegram bot which automatically sends them the requested file.

## ✨ Features

- **📎 File Distribution**: Send files to users through custom links
- **🔗 Link Generation**: Automatic generation of shareable links for each file
- **📁 File Management**: Easy file addition, removal, and listing
- **🎛️ Interactive Interface**: Modern inline keyboard interface
- **📊 File Information**: Display file sizes and availability status
- **🔒 Secure**: File access through unique IDs
- **🌐 24/7 Operation**: Designed for continuous operation
- **🐳 Docker Support**: Easy deployment with Docker
- **⚙️ Configurable**: Environment-based configuration

## 🚀 Quick Start

### 1. Setup the Bot

```bash
# Run setup script
chmod +x setup.sh
./setup.sh
```

### 2. Add Files

```bash
# Add a file
python3 file_manager.py add /path/to/your/file.pdf --id document1

# List files
python3 file_manager.py list
```

### 3. Start the Bot

```bash
# Development (polling)
python3 bot.py

# Production (with Docker)
docker-compose up -d
```

## 📖 Usage

### Creating Share Links

After adding files, your share links will be:
```
https://t.me/YOUR_BOT_USERNAME?start=document1
https://t.me/YOUR_BOT_USERNAME?start=image1
```

### Bot Commands

- `/start` - Start the bot or access a specific file
- `/help` - Show help information
- `/list` - Browse all available files
- `/file <file_id>` - Get a specific file

### File Management

```bash
# Add file with custom ID
python3 file_manager.py add document.pdf --id mydoc --name "My Document.pdf"

# Remove file
python3 file_manager.py remove mydoc

# List all files
python3 file_manager.py list

# Check file integrity
python3 file_manager.py check
```

## 🚀 Deployment Options

### Option 1: Docker (Recommended for 24/7)

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 2: Direct Python (Simple)

```bash
# Start the bot
python3 bot.py
```

### Option 3: Systemd Service (24/7 on Linux)

```bash
# Install as system service
sudo cp telegram-file-bot.service /etc/systemd/system/
sudo systemctl enable telegram-file-bot
sudo systemctl start telegram-file-bot
```

## 🔧 File Management

### Adding Files

1. **Using the file manager**:
   ```bash
   python3 file_manager.py add /path/to/file.pdf --id myfile
   ```

2. **Manual method**:
   - Copy files to the `files/` directory
   - Update `file_mappings.json` with the mapping

### Sharing Files

Once a file is added with ID `myfile`, share this link:
```
https://t.me/YOUR_BOT_USERNAME?start=myfile
```

When users click this link:
1. They get redirected to your Telegram bot
2. The bot automatically sends them the file
3. No manual intervention required!

## 🛠️ Troubleshooting

### Common Issues

1. **Bot not responding**: Check bot token and internet connection
2. **Files not found**: Verify file paths in `files/` directory
3. **Permission errors**: Ensure files are readable

### Getting Your Bot Username

After starting the bot, message it and use `/help` to see your bot's username for creating links.

---

**Your bot is now ready for 24/7 file distribution! 🎉**