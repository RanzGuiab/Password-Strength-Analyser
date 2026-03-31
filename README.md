# 🔐 Password Strength Analyser

A full-stack demo app that checks the strength of your password in real time.  
**Backend:** Python (Vercel Serverless Functions) + [zxcvbn](https://github.com/dropbox/zxcvbn)  
**Frontend:** Static HTML/CSS/JS (served from `public/`)

---

## 📸 Features

- Real-time password strength checker powered by **zxcvbn** (same engine used by Dropbox & major sites)
- Visual bar + colour-coded strength feedback
- Crack time estimates, guess count, and practical suggestions
- Simple, attractive, self-contained frontend (1 file)
- Python serverless API (works on Vercel)

---

## 🏗 Project Structure

```
Password-Strenght-Analyser/
├── api/
│   ├── analyse.py        # POST /api/analyse
│   └── index.py          # GET  /api
├── public/
│   └── index.html        # served at /
├── requirements.txt      # python deps for serverless
├── vercel.json           # routing + outputDirectory
├── frontend/             # source copy (kept for reference)
└── backend/              # legacy Flask version (optional)
```

---

## 🚀 Quickstart

### 1. Clone the Repo

```bash
git clone https://github.com/<your-username>/Password-Strenght-Analyser.git
cd Password-Strenght-Analyser
```

### 2. Local Dev (Recommended)

This project is deployed like a typical Vercel app:

- Static site served from `public/`
- Python serverless functions under `api/`

Run it locally the same way:

```bash
# (one-time) install Vercel CLI
npm i -g vercel

# (optional but recommended) create & activate a venv, then install python deps
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# start the local dev server
vercel dev
```

Then open the URL that `vercel dev` prints (commonly `http://localhost:3000`).

---

## 🧑‍💻 API Reference

### `POST /api/analyse`

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

### `GET /api`

- `GET /api` → `{"status":"ok","endpoints":["/api/analyse"]}`

---

## 🌈 Frontend Features

Everything lives in a single file: `public/index.html`

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
- Confirm you’re calling the serverless route: `POST /api/analyse`
- For local dev, run `vercel dev` so `/api/*` routes exist

### `FUNCTION_INVOCATION_FAILED` on Vercel
- Check the function is returning valid JSON (the serverless handler in `api/analyse.py` defensively serializes responses)
- Use `vercel logs <your-deployment-url>` to inspect runtime errors

### CORS Errors in Browser
The serverless endpoint returns permissive CORS headers. If you open the HTML directly from disk (`file://`), prefer using `vercel dev` instead.

### Port already in use
`vercel dev` commonly uses port `3000`. Stop the process using that port, or run `vercel dev -p 3001`.

### Module Not Found
Activate your virtual environment before installing Python dependencies:
```bash
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate.bat  # Windows
pip install -r requirements.txt
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `zxcvbn` | latest | Password strength estimation engine |

---

## 📖 References

- [zxcvbn — Dropbox password strength estimator](https://github.com/dropbox/zxcvbn)

---
