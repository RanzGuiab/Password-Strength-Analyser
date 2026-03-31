import json
from zxcvbn import zxcvbn

def handler(request):
    """Vercel serverless function handler"""
    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Method not allowed"})
        }

    try:
        data = json.loads(request.body) if isinstance(request.body, str) else request.body
    except:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON"})
        }

    if not data or "password" not in data:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "No password provided"})
        }

    password = data["password"]

    if not isinstance(password, str):
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Password must be a string"})
        }

    result = zxcvbn(password)
    score = result["score"]

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

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(response)
    }
