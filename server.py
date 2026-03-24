#!/usr/bin/env python3
"""Simple HTTP server that serves static files and provides a shared highscores API.

Highscore data is stored in the data/ folder as JSON files so that all users
connecting to this server share the same leaderboards.

Usage:
    python3 server.py [port]   (default port: 8080)
"""

import http.server
import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
DATA_DIR = SCRIPT_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

# Only allow safe key names: alphanumeric, underscores and hyphens
KEY_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,64}$')


class HighscoreHandler(http.server.SimpleHTTPRequestHandler):
    """Extends SimpleHTTPRequestHandler with a /api/highscores/<key> REST API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SCRIPT_DIR), **kwargs)

    # ── Routing ───────────────────────────────────────────────────────

    def do_GET(self):
        if self.path.startswith('/api/highscores/'):
            self._handle_get_highscores()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/highscores/'):
            self._handle_post_highscores()
        else:
            self.send_error(405, 'Method Not Allowed')

    # ── API helpers ───────────────────────────────────────────────────

    def _parse_key(self):
        """Extract and validate the highscore key from the request path."""
        key = self.path[len('/api/highscores/'):]
        # Strip any query-string that might be appended
        key = key.split('?')[0]
        if not KEY_PATTERN.match(key):
            return None
        return key

    def _handle_get_highscores(self):
        """Return the stored highscore list for the given key as JSON."""
        key = self._parse_key()
        if not key:
            self.send_error(400, 'Invalid key')
            return

        filepath = DATA_DIR / f'{key}.json'
        if filepath.exists():
            data = filepath.read_bytes()
        else:
            data = b'[]'

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _handle_post_highscores(self):
        """Receive a JSON array of scores and persist it to disk."""
        key = self._parse_key()
        if not key:
            self.send_error(400, 'Invalid key')
            return

        raw_length = self.headers.get('Content-Length')
        if raw_length is None:
            self.send_error(411, 'Content-Length required')
            return
        try:
            length = int(raw_length)
            if length < 0:
                raise ValueError
        except ValueError:
            self.send_error(400, 'Invalid Content-Length')
            return

        body = self.rfile.read(length)

        try:
            scores = json.loads(body)
            if not isinstance(scores, list):
                raise ValueError('Payload must be a JSON array')
        except (json.JSONDecodeError, ValueError) as exc:
            self.send_error(400, str(exc))
            return

        # Write atomically: write to a temp file then rename to avoid
        # partial reads by concurrent GET requests.
        filepath = DATA_DIR / f'{key}.json'
        tmp_path = DATA_DIR / f'{key}.json.tmp'
        tmp_path.write_text(
            json.dumps(scores, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )
        tmp_path.replace(filepath)

        response = b'{"ok":true}'
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, fmt, *args):
        print(f'[server] {self.address_string()} - {fmt % args}')


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f'Open http://localhost:{port}/index.html in your browser')
    with http.server.HTTPServer(('', port), HighscoreHandler) as httpd:
        httpd.serve_forever()
