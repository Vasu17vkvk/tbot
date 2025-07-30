import os
from dotenv import load_dotenv
from typing import Dict, Optional
import json

# Load environment variables
load_dotenv()

class Config:
    def __init__(self):
        self.BOT_TOKEN = os.getenv('BOT_TOKEN')
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN environment variable is required")
        
        self.WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
        self.PORT = int(os.getenv('PORT', 8443))
        self.FILES_DIR = os.getenv('FILES_DIR', 'files')
        self.MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50 * 1024 * 1024))  # 50MB default
        
        # File mappings - maps file IDs to actual file paths
        self.file_mappings = self._load_file_mappings()
        
        # Create files directory if it doesn't exist
        os.makedirs(self.FILES_DIR, exist_ok=True)
    
    def _load_file_mappings(self) -> Dict[str, str]:
        """Load file mappings from JSON file or environment variable"""
        mappings_file = os.getenv('FILE_MAPPINGS_PATH', 'file_mappings.json')
        
        if os.path.exists(mappings_file):
            with open(mappings_file, 'r') as f:
                return json.load(f)
        
        # Default mappings - you can modify these
        default_mappings = {
            'document1': 'sample_document.pdf',
            'image1': 'sample_image.jpg',
            'video1': 'sample_video.mp4'
        }
        
        # Save default mappings
        with open(mappings_file, 'w') as f:
            json.dump(default_mappings, f, indent=2)
        
        return default_mappings
    
    def get_file_path(self, file_id: str) -> Optional[str]:
        """Get the actual file path for a given file ID"""
        filename = self.file_mappings.get(file_id)
        if filename:
            return os.path.join(self.FILES_DIR, filename)
        return None
    
    def add_file_mapping(self, file_id: str, filename: str):
        """Add a new file mapping"""
        self.file_mappings[file_id] = filename
        self._save_file_mappings()
    
    def _save_file_mappings(self):
        """Save current file mappings to JSON file"""
        mappings_file = os.getenv('FILE_MAPPINGS_PATH', 'file_mappings.json')
        with open(mappings_file, 'w') as f:
            json.dump(self.file_mappings, f, indent=2)

# Global config instance
config = Config()