import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.bot.bot import create_bot


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Atlas AI Financial Assistant is running!")

    def log_message(self, format, *args):
        pass


def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"Health server running on port {port}")
    server.serve_forever()


# Start HTTP health server for Render
threading.Thread(target=start_health_server, daemon=True).start()

# Start Telegram bot
app = create_bot()

print("Atlas AI Bot Started...")

app.run_polling()