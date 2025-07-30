import logging
import asyncio
import os
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from telegram.error import TelegramError
import aiofiles
from config import config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramFileBot:
    def __init__(self):
        self.application = Application.builder().token(config.BOT_TOKEN).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("list", self.list_files_command))
        self.application.add_handler(CommandHandler("file", self.file_command))
        
        # Callback query handler for inline buttons
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handler for file uploads (admin only)
        self.application.add_handler(MessageHandler(filters.Document.ALL, self.handle_document))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command with optional file parameter"""
        args = context.args
        user = update.effective_user
        
        logger.info(f"User {user.id} ({user.username}) started the bot")
        
        if args:
            # User clicked a link with file parameter
            file_id = args[0]
            await self.send_file(update, context, file_id)
        else:
            # Regular start message
            keyboard = [
                [InlineKeyboardButton("📁 Browse Files", callback_data="list_files")],
                [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            welcome_message = (
                f"👋 Welcome {user.first_name}!\n\n"
                "I'm your file distribution bot. I can send you files when you click "
                "on specific links or you can browse available files.\n\n"
                "Use the buttons below to get started!"
            )
            
            await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "🤖 **Bot Commands:**\n\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/list - List available files\n"
            "/file <file_id> - Get a specific file\n\n"
            "📎 **How to use:**\n"
            "1. Click on a shared link to get a specific file\n"
            "2. Use /list to browse all available files\n"
            "3. Click on file buttons to download\n\n"
            "🔗 **Link format:**\n"
            f"`https://t.me/{context.bot.username}?start=<file_id>`"
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def list_files_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command to show available files"""
        await self.show_file_list(update, context)
    
    async def file_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /file command to get a specific file"""
        args = context.args
        
        if not args:
            await update.message.reply_text(
                "Please specify a file ID. Example: `/file document1`",
                parse_mode='Markdown'
            )
            return
        
        file_id = args[0]
        await self.send_file(update, context, file_id)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "list_files":
            await self.show_file_list(update, context, edit_message=True)
        elif data == "help":
            help_text = (
                "🤖 **Bot Commands:**\n\n"
                "/start - Start the bot\n"
                "/help - Show this help message\n"
                "/list - List available files\n"
                "/file <file_id> - Get a specific file\n\n"
                "📎 **How to use:**\n"
                "Click on file buttons below to download them instantly!"
            )
            await query.edit_message_text(help_text, parse_mode='Markdown')
        elif data.startswith("file_"):
            file_id = data.replace("file_", "")
            await self.send_file(update, context, file_id, query=query)
        elif data == "back_to_menu":
            keyboard = [
                [InlineKeyboardButton("📁 Browse Files", callback_data="list_files")],
                [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "👋 Welcome back!\n\nChoose an option:",
                reply_markup=reply_markup
            )
    
    async def show_file_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE, edit_message=False):
        """Show list of available files"""
        if not config.file_mappings:
            message = "📭 No files are currently available."
            keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
        else:
            message = "📁 **Available Files:**\n\nClick on any file to download it:\n\n"
            keyboard = []
            
            for file_id, filename in config.file_mappings.items():
                file_path = config.get_file_path(file_id)
                if file_path and os.path.exists(file_path):
                    # Get file size
                    size = os.path.getsize(file_path)
                    size_str = self._format_file_size(size)
                    
                    button_text = f"📄 {filename} ({size_str})"
                    keyboard.append([InlineKeyboardButton(button_text, callback_data=f"file_{file_id}")])
            
            keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if edit_message and update.callback_query:
            await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def send_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE, file_id: str, query=None):
        """Send a specific file to the user"""
        file_path = config.get_file_path(file_id)
        user = update.effective_user
        
        if not file_path or not os.path.exists(file_path):
            error_message = f"❌ File '{file_id}' not found or not available."
            if query:
                await query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
            return
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > config.MAX_FILE_SIZE:
            error_message = (
                f"❌ File '{file_id}' is too large ({self._format_file_size(file_size)}). "
                f"Maximum allowed size is {self._format_file_size(config.MAX_FILE_SIZE)}."
            )
            if query:
                await query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
            return
        
        try:
            # Send typing action
            chat_id = update.effective_chat.id
            await context.bot.send_chat_action(chat_id=chat_id, action="upload_document")
            
            # Get filename and send file
            filename = config.file_mappings[file_id]
            
            with open(file_path, 'rb') as file:
                caption = f"📎 {filename}\n💾 Size: {self._format_file_size(file_size)}"
                
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=file,
                    filename=filename,
                    caption=caption
                )
            
            logger.info(f"File '{file_id}' sent to user {user.id} ({user.username})")
            
            # Send success message with back button
            keyboard = [[InlineKeyboardButton("📁 Browse More Files", callback_data="list_files")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            success_message = f"✅ File '{filename}' sent successfully!"
            
            if query:
                await query.edit_message_text(success_message, reply_markup=reply_markup)
            else:
                await update.message.reply_text(success_message, reply_markup=reply_markup)
                
        except TelegramError as e:
            logger.error(f"Error sending file '{file_id}' to user {user.id}: {e}")
            error_message = f"❌ Failed to send file '{file_id}'. Please try again later."
            
            if query:
                await query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle document uploads (for adding files to the bot)"""
        # This is a basic implementation - you might want to add admin authentication
        user = update.effective_user
        document = update.message.document
        
        # For security, you might want to restrict this to specific users
        # allowed_users = [123456789]  # Add admin user IDs
        # if user.id not in allowed_users:
        #     await update.message.reply_text("❌ You don't have permission to upload files.")
        #     return
        
        await update.message.reply_text("🚧 File upload feature not implemented yet. Please use manual file management.")
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    async def start_webhook(self):
        """Start the bot with webhook (for production)"""
        if not config.WEBHOOK_URL:
            logger.error("WEBHOOK_URL not configured")
            return
        
        await self.application.initialize()
        await self.application.start()
        
        # Set webhook
        webhook_url = f"{config.WEBHOOK_URL}/webhook"
        await self.application.bot.set_webhook(webhook_url)
        
        logger.info(f"Webhook set to: {webhook_url}")
        
        # Keep the application running
        await self.application.updater.start_webhook(
            listen="0.0.0.0",
            port=config.PORT,
            webhook_url=webhook_url
        )
    
    async def start_polling(self):
        """Start the bot with polling (for development/simple deployment)"""
        logger.info("Starting bot with polling...")
        
        await self.application.initialize()
        await self.application.start()
        
        # Start polling
        await self.application.updater.start_polling()
        
        logger.info("Bot is running! Press Ctrl+C to stop.")
        
        # Keep the bot running
        try:
            await self.application.updater.idle()
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        finally:
            await self.application.stop()
            await self.application.shutdown()

def main():
    """Main function to start the bot"""
    bot = TelegramFileBot()
    
    # Use webhook if WEBHOOK_URL is configured, otherwise use polling
    if config.WEBHOOK_URL:
        asyncio.run(bot.start_webhook())
    else:
        asyncio.run(bot.start_polling())

if __name__ == "__main__":
    main()