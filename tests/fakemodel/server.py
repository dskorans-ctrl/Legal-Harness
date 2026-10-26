"""Small HTTP adapter for the pure stand-in. Socket tests are opt-in."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json

from .core import FakeModel


def serve(bind="127.0.0.1", port=18434, model=None):
    model = FakeModel() if model is None else model

    class Handler(BaseHTTPRequestHandler):
        def _handle(self):
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length < 0:
                    raise ValueError("negative content length")
            except ValueError:
                status, payload = 400, {"error": "fakemodel: invalid Content-Length"}
            else:
                status, payload = model.handle(self.command, self.path, self.rfile.read(length))
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        do_GET = _handle
        do_POST = _handle

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer((bind, port), Handler)
    print(f"fakemodel: listening on {bind}:{server.server_port}", flush=True)
    return server
