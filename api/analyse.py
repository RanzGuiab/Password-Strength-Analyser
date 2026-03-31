import json
from http.server import BaseHTTPRequestHandler


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

        try:
            from zxcvbn import zxcvbn as _zxcvbn

            result = _zxcvbn(password)
        except Exception as e:
            self._send_json(
                500,
                {
                    "error": "Password analysis failed",
                    "detail": f"{type(e).__name__}: {e}",
                },
            )
            return

        try:
            score_labels = {
                0: {"label": "Very Weak", "color": "#e74c3c"},
                1: {"label": "Weak", "color": "#e67e22"},
                2: {"label": "Fair", "color": "#f1c40f"},
                3: {"label": "Strong", "color": "#2ecc71"},
                4: {"label": "Very Strong", "color": "#27ae60"},
            }

            score = int(result.get("score", 0))
            score_meta = score_labels.get(score, score_labels[0])

            feedback = result.get("feedback") or {}
            feedback_warnings = feedback.get("warning", "")
            feedback_suggestions = feedback.get("suggestions", [])

            crack_times_display = result.get("crack_times_display") or {}
            crack_time = (
                crack_times_display.get("offline_slow_hashing_1e4_per_second")
                or crack_times_display.get("offline_fast_hashing_1e10_per_second")
                or ""
            )

            raw_calc_time = result.get("calc_time", 0)
            try:
                calc_time_ms = raw_calc_time.total_seconds() * 1000
            except AttributeError:
                calc_time_ms = float(raw_calc_time)

            response = {
                "score": score,
                "label": score_meta["label"],
                "color": score_meta["color"],
                "crack_time": crack_time,
                "warning": feedback_warnings,
                "suggestions": feedback_suggestions,
                "guesses": self._coerce_int(result.get("guesses")),
                "calc_time": round(calc_time_ms, 3),
            }
        except Exception as e:
            self._send_json(
                500,
                {
                    "error": "Unexpected analysis result",
                    "detail": f"{type(e).__name__}: {e}",
                },
            )
            return

        self._send_json(200, response)

    @staticmethod
    def _coerce_int(value):
        if value is None:
            return None
        try:
            return int(value)
        except Exception:
            return value

    def _send_json(self, status_code: int, payload: dict):
        try:
            body_str = json.dumps(payload, default=str)
        except Exception as e:
            body_str = json.dumps(
                {
                    "error": "Response serialization failed",
                    "detail": f"{type(e).__name__}: {e}",
                },
                default=str,
            )

        body = body_str.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        for k, v in _cors_headers().items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except Exception:
            pass