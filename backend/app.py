from flask import Flask, request, jsonify
from flask_cors import CORS
from zxcvbn import zxcvbn

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from the frontend


@app.route("/analyse", methods=["POST"])
def analyse_password():
    data = request.get_json()

    if not data or "password" not in data:
        return jsonify({"error": "No password provided"}), 400

    password = data["password"]

    if not isinstance(password, str):
        return jsonify({"error": "Password must be a string"}), 400

    # Analyse using zxcvbn
    result = zxcvbn(password)

    score = result["score"]  # 0 (very weak) to 4 (very strong)

    # Map score to human-readable label and color
    score_labels = {
        0: {"label": "Very Weak",  "color": "#e74c3c"},
        1: {"label": "Weak",       "color": "#e67e22"},
        2: {"label": "Fair",       "color": "#f1c40f"},
        3: {"label": "Strong",     "color": "#2ecc71"},
        4: {"label": "Very Strong","color": "#27ae60"},
    }

    feedback_warnings = result["feedback"].get("warning", "")
    feedback_suggestions = result["feedback"].get("suggestions", [])

    crack_time = result["crack_times_display"]["offline_slow_hashing_1e4_per_second"]

    raw_calc_time = result["calc_time"]
    try:
        # timedelta path (Python 3.14 + zxcvbn)
        calc_time_ms = raw_calc_time.total_seconds() * 1000
    except AttributeError:
        # numeric path (older environments) — already a float/int
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

    return jsonify(response), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=8888)