import json
from http.server import BaseHTTPRequestHandler

from zxcvbn import zxcvbn


def _cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        for k, v in _cors_headers().items():
            self.send_header(k, v)
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            content_length = 0

        raw = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            self._send_json(400, {"error": "Invalid JSON"})
            return

        if "password" not in data:
            self._send_json(400, {"error": "No password provided"})
            return

        password = data["password"]
        if not isinstance(password, str):
            self._send_json(400, {"error": "Password must be a string"})
            return

        result = zxcvbn(password)
        score = result["score"]

        score_labels = {
            0: {"label": "Very Weak", "color": "#e74c3c"},
            1: {"label": "Weak", "color": "#e67e22"},
            2: {"label": "Fair", "color": "#f1c40f"},
            3: {"label": "Strong", "color": "#2ecc71"},
            4: {"label": "Very Strong", "color": "#27ae60"},
        }

        feedback_warnings = result["feedback"].get("warning", "")
        feedback_suggestions = result["feedback"].get("suggestions", [])
        crack_time = result["crack_times_display"]["offline_slow_hashing_1e4_per_second"]

        raw_calc_time = result["calc_time"]
        try:
            calc_time_ms = raw_calc_time.total_seconds() * 1000
        except AttributeError:
            calc_time_ms = float(raw_calc_time)

        response = {
            "score": score,
            "label": score_labels[score]["label"],
            "color": score_labels[score]["color"],
            "crack_time": crack_time,
            "warning": feedback_warnings,
            "suggestions": feedback_suggestions,
            "guesses": result["guesses"],
            "calc_time": round(calc_time_ms, 3),
        }

        self._send_json(200, response)

    def _send_json(self, status_code: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        for k, v in _cors_headers().items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)