import http.server
import socketserver
import threading
from src.config import logger
from src.web_dashboard import DASHBOARD_HTML

class HealthCheckHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "healthy"}')
        elif self.path in ('/', '/dashboard', '/index.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Override to suppress default HTTP logging in stdout/stderr
        pass

def start_health_server(port: int = 8000) -> threading.Thread:
    def run_server():
        socketserver.TCPServer.allow_reuse_address = True
        try:
            with socketserver.TCPServer(("", port), HealthCheckHandler) as httpd:
                logger.info(f"HTTP health & dashboard server started on port {port} at / and /health")
                httpd.serve_forever()
        except Exception as e:
            logger.critical(f"Failed to start HTTP server on port {port}: {str(e)}")
            
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    return thread
