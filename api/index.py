from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def api_root():
    return jsonify({"status": "ok", "endpoints": ["/api/analyse"]}), 200
