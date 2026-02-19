# 🔐 Password Strength Analyser

A full-stack demo app that checks the strength of your password in real time.  
**Backend:** Python (Flask) + [zxcvbn](https://github.com/dropbox/zxcvbn)  
**Frontend:** Vanilla HTML/CSS/JS

---

## 📸 Features

- Real-time password strength checker powered by **zxcvbn** (same engine used by Dropbox & major sites)
- Visual bar + colour-coded strength feedback
- Crack time estimates, guess count, and practical suggestions
- Simple, attractive, self-contained frontend (1 file)
- Python Flask backend — easy to run anywhere

---

## 🏗 Project Structure

```
password-analyser/
├── backend/
│   ├── app.py
│   └── requirements.txt
└── frontend/
    └── index.html
```

---

## 🚀 Quickstart

### 1. Clone the Repo

```bash
git clone https://github.com/<your-username>/Password-Strenght-Analyser.git
cd Password-Strenght-Analyser
```

### 2. Backend Setup (Python 3.8+)

```bash
cd backend

# Create a virtual environment
python -m venv venv          # or: python3 -m venv venv

# Activate it
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate.bat    # Windows (Command Prompt)
venv\Scripts\Activate.ps1    # Windows (PowerShell)

# Install dependencies
pip install -r requirements.txt

# Start the Flask server
python app.py
# → Running on http://127.0.0.1:5000
```

Test that the backend is alive:

```bash
curl http://localhost:5000/health
# → {"status": "ok"}

curl -X POST http://localhost:5000/analyse \
  -H "Content-Type: application/json" \
  -d '{"password": "MyP@ssw0rd!"}'
```

### 3. Frontend

Open `frontend/index.html` directly in your browser — no server required.

> The page calls `http://localhost:5000/analyse`. Make sure Flask is running before clicking **Analyse Password**.

---

## 🧑‍💻 API Reference

### `POST /analyse`

**Request body**
```json
{ "password": "your-password-here" }
```

**Response**
```json
{
  "score":       3,
  "label":       "Strong",
  "color":       "#2ecc71",
  "crack_time":  "centuries",
  "warning":     "",
  "suggestions": [],
  "guesses":     8735128,
  "calc_time":   0.412
}
```

| Field | Type | Description |
|---|---|---|
| `score` | `int` | `0` (very weak) – `4` (very strong) |
| `label` | `string` | Human-readable strength label |
| `color` | `string` | Hex colour matching the score |
| `crack_time` | `string` | Estimated offline crack time |
| `warning` | `string` | Single warning message (may be empty) |
| `suggestions` | `string[]` | List of improvement tips |
| `guesses` | `int` | Estimated number of guesses needed |
| `calc_time` | `float` | Analysis duration in milliseconds |

### `GET /health`

Returns `{"status": "ok"}` — useful for confirming the server is up.

---

## 🌈 Frontend Features

Everything lives in a single file: `frontend/index.html`

| Feature | Details |
|---|---|
| Colour-coded strength bar | Red → Orange → Yellow → Green |
| Crack time | Shown in human-readable form |
| Guess count | Formatted with thousands separators |
| Calc time | Milliseconds |
| Warning | Displayed if the password matches common patterns |
| Suggestions | Actionable tips from zxcvbn |
| Show/hide toggle | Eye icon to reveal or mask the password |
| Enter key support | Press Enter to trigger analysis |

---

## 🐍 Troubleshooting

### 404 Not Found
- Check the URL spelling: the route is `/analyse` (British spelling), **not** `/analyze`
- Confirm the frontend is sending a `POST` request, not `GET`
- Restart Flask after any code changes: `Ctrl+C` → `python app.py`

### `TypeError: Object of type timedelta is not JSON serializable`
This occurs on **Python 3.14+** where `zxcvbn` returns `calc_time` as a `datetime.timedelta`.  
The fix is already applied in `app.py`:
```python
try:
    calc_time_ms = raw_calc_time.total_seconds() * 1000  # timedelta → ms
except AttributeError:
    calc_time_ms = float(raw_calc_time)                  # already a number
```

### CORS Errors in Browser
`flask-cors` is enabled by default for all origins. If you still see CORS errors, confirm `flask-cors` installed correctly:
```bash
pip install flask-cors
```

### `Address already in use` (Port 5000)
```bash
# macOS/Linux
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

### Module Not Found
Always activate your virtual environment before running Flask:
```bash
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate.bat  # Windows
pip install -r requirements.txt
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `flask` | latest | Web framework / REST API |
| `flask-cors` | latest | Cross-origin request support |
| `zxcvbn` | latest | Password strength estimation engine |

---

## 📖 References

- [zxcvbn — Dropbox password strength estimator](https://github.com/dropbox/zxcvbn)
- [Flask documentation](https://flask.palletsprojects.com/)
- [Flask-CORS documentation](https://flask-cors.readthedocs.io/)

---

## 📜 License

MIT — see [LICENSE](LICENSE) for details.
