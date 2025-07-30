#!/usr/bin/env python3
"""
Simple health check server for Docker health monitoring
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json
import os

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            health_status = {
                "status": "healthy",
                "service": "telegram-file-bot",
                "files_directory": os.path.exists("files"),
                "config_loaded": os.path.exists("file_mappings.json")
            }
            
            self.wfile.write(json.dumps(health_status).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def start_health_server():
    """Start health check server in background"""
    server = HTTPServer(('0.0.0.0', 8443), HealthCheckHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server

if __name__ == "__main__":
    start_health_server()
    print("Health check server running on port 8443")
    
    # Keep the server running
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Health check server stopped")