#!/usr/bin/env python3
"""
File Manager utility for Telegram File Bot
Helps manage files and file mappings
"""

import os
import json
import argparse
import shutil
from pathlib import Path
from config import config

class FileManager:
    def __init__(self):
        self.files_dir = config.FILES_DIR
        self.mappings_file = os.getenv('FILE_MAPPINGS_PATH', 'file_mappings.json')
        
        # Ensure files directory exists
        os.makedirs(self.files_dir, exist_ok=True)
    
    def add_file(self, file_path: str, file_id: str = None, filename: str = None):
        """Add a file to the bot's file system"""
        if not os.path.exists(file_path):
            print(f"❌ Error: File '{file_path}' does not exist")
            return False
        
        # Generate file_id if not provided
        if not file_id:
            file_id = Path(file_path).stem.lower().replace(' ', '_')
        
        # Use original filename if not provided
        if not filename:
            filename = os.path.basename(file_path)
        
        # Copy file to files directory
        destination = os.path.join(self.files_dir, filename)
        
        try:
            shutil.copy2(file_path, destination)
            
            # Update file mappings
            config.add_file_mapping(file_id, filename)
            
            print(f"✅ File added successfully!")
            print(f"   File ID: {file_id}")
            print(f"   Filename: {filename}")
            print(f"   Location: {destination}")
            print(f"   Link: https://t.me/YOUR_BOT_USERNAME?start={file_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error copying file: {e}")
            return False
    
    def remove_file(self, file_id: str):
        """Remove a file from the bot's file system"""
        if file_id not in config.file_mappings:
            print(f"❌ Error: File ID '{file_id}' not found")
            return False
        
        filename = config.file_mappings[file_id]
        file_path = os.path.join(self.files_dir, filename)
        
        try:
            # Remove physical file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Remove from mappings
            del config.file_mappings[file_id]
            config._save_file_mappings()
            
            print(f"✅ File '{file_id}' ({filename}) removed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error removing file: {e}")
            return False
    
    def list_files(self):
        """List all files in the bot's file system"""
        if not config.file_mappings:
            print("📭 No files are currently available.")
            return
        
        print("📁 Available Files:")
        print("-" * 60)
        
        for file_id, filename in config.file_mappings.items():
            file_path = os.path.join(self.files_dir, filename)
            
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                size_str = self._format_file_size(size)
                status = "✅ Available"
            else:
                size_str = "N/A"
                status = "❌ Missing"
            
            print(f"ID: {file_id}")
            print(f"   File: {filename}")
            print(f"   Size: {size_str}")
            print(f"   Status: {status}")
            print(f"   Link: https://t.me/YOUR_BOT_USERNAME?start={file_id}")
            print()
    
    def check_files(self):
        """Check for missing or orphaned files"""
        print("🔍 Checking file integrity...")
        
        missing_files = []
        orphaned_files = []
        
        # Check for missing files (in mappings but not on disk)
        for file_id, filename in config.file_mappings.items():
            file_path = os.path.join(self.files_dir, filename)
            if not os.path.exists(file_path):
                missing_files.append((file_id, filename))
        
        # Check for orphaned files (on disk but not in mappings)
        if os.path.exists(self.files_dir):
            for filename in os.listdir(self.files_dir):
                file_path = os.path.join(self.files_dir, filename)
                if os.path.isfile(file_path):
                    if filename not in config.file_mappings.values():
                        orphaned_files.append(filename)
        
        # Report results
        if missing_files:
            print(f"❌ Missing files ({len(missing_files)}):")
            for file_id, filename in missing_files:
                print(f"   {file_id}: {filename}")
        
        if orphaned_files:
            print(f"⚠️  Orphaned files ({len(orphaned_files)}):")
            for filename in orphaned_files:
                print(f"   {filename}")
        
        if not missing_files and not orphaned_files:
            print("✅ All files are in sync!")
    
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

def main():
    parser = argparse.ArgumentParser(description="Telegram File Bot - File Manager")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add file command
    add_parser = subparsers.add_parser('add', help='Add a file to the bot')
    add_parser.add_argument('file_path', help='Path to the file to add')
    add_parser.add_argument('--id', help='Custom file ID')
    add_parser.add_argument('--name', help='Custom filename')
    
    # Remove file command
    remove_parser = subparsers.add_parser('remove', help='Remove a file from the bot')
    remove_parser.add_argument('file_id', help='File ID to remove')
    
    # List files command
    list_parser = subparsers.add_parser('list', help='List all files')
    
    # Check files command
    check_parser = subparsers.add_parser('check', help='Check file integrity')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    file_manager = FileManager()
    
    if args.command == 'add':
        file_manager.add_file(args.file_path, args.id, args.name)
    elif args.command == 'remove':
        file_manager.remove_file(args.file_id)
    elif args.command == 'list':
        file_manager.list_files()
    elif args.command == 'check':
        file_manager.check_files()

if __name__ == "__main__":
    main()