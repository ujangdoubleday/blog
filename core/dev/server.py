"""
Development server for local testing
"""

import http.server
import os
import socket
import socketserver
import threading
import webbrowser
from typing import Any, Dict


class DevServer:
    """Local development server"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # bind to 0.0.0.0 to allow access from local network
        self.host = "0.0.0.0"
        self.port = config.get("dev", {}).get("port", 8000)

    def serve(self, port: int = None):
        """Start the development server"""
        if port:
            self.port = port

        # Change to output directory
        output_dir = self.config["build"]["output_dir"]
        os.chdir(output_dir)

        # Create server
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer((self.host, self.port), Handler) as httpd:
            # get local IP address
            local_ip = self._get_local_ip()

            print("\n🚀 Development server running!")
            print("\n📍 Local access:")
            print("   http://localhost:{self.port}")
            print("   http://127.0.0.1:{self.port}")
            if local_ip:
                print("\n🌐 Network access:")
                print("   http://{local_ip}:{self.port}")
            print("\n✋ Press Ctrl+C to stop\n")

            # Open browser in a separate thread
            def open_browser():
                import time

                time.sleep(1)
                webbrowser.open(f"http://localhost:{self.port}")

            threading.Thread(target=open_browser, daemon=True).start()

            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped.")

    def _get_local_ip(self) -> str:
        """get local IP address for network access"""
        try:
            # create a socket to get the local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return ""

    def build_and_serve(self, generator):
        """Build the site and then serve it"""
        generator.build()
        self.serve()
