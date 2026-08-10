import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.bot.bot import create_bot
from app.database.database import init_db


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

    print(f"Starting health server on port {port}", flush=True)

    server = HTTPServer(
        ("0.0.0.0", port),
        HealthHandler
    )

    print(
        f"Health server running on port {port}",
        flush=True
    )

    server.serve_forever()


print("========== ATLAS AI STARTING ==========", flush=True)

threading.Thread(
    target=start_health_server,
    daemon=True
).start()

print("Initializing database...", flush=True)
init_db()

print("Creating Telegram application...", flush=True)

app = create_bot()

print("Telegram application created!", flush=True)
print("Atlas AI Bot Started!", flush=True)
print("Starting Telegram polling...", flush=True)

app.run_polling(
    drop_pending_updates=False
)

print("Telegram polling stopped!", flush=True)