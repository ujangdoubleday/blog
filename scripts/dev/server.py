"""
Development server for local testing
"""

import os
import http.server
import socketserver
import webbrowser
import threading
from typing import Dict, Any


class DevServer:
    """Local development server"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.host = config.get('dev', {}).get('host', 'localhost')
        self.port = config.get('dev', {}).get('port', 8000)
    
    def serve(self, port: int = None):
        """Start the development server"""
        if port:
            self.port = port
            
        # Change to output directory
        output_dir = self.config['build']['output_dir']
        os.chdir(output_dir)
        
        # Create server
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer((self.host, self.port), Handler) as httpd:
            print(f"Serving at http://{self.host}:{self.port}")
            
            # Open browser in a separate thread
            def open_browser():
                import time
                time.sleep(1)
                webbrowser.open(f'http://{self.host}:{self.port}')
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped.")
    
    def build_and_serve(self, generator):
        """Build the site and then serve it"""
        generator.build()
        self.serve()
