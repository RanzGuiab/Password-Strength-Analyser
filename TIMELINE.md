# Project Timeline — Vercel Migration to Serverless

_Last updated: 2026-03-31_

This document captures the iterative deployment/debugging timeline for migrating **Password-Strenght-Analyser** from a local Flask app to a **Vercel-hosted serverless + static** architecture.

## Goals

- Host the **frontend** and **backend** on **Vercel under one domain**.
- Serve the UI at `/`.
- Expose the password analysis API at `POST /api/analyse`.

## Starting Point (Local Flask)

- Repo originally shipped as:
  - Flask API in `backend/app.py` (`POST /analyse`, `GET /health`)
  - Static UI in `frontend/index.html`
  - Frontend called the local backend (localhost).

## Migration Timeline (What changed, and why)

### 1) First Vercel deploy attempts (routing/runtime mismatch)

**Symptom(s)**
- Vercel errors such as:
  - “Function Runtimes must have a valid version…”
  - “No flask entrypoint found…”
  - 404 at `/`
  - 405 on API POSTs (rewrite/routing sending requests somewhere unexpected)

**Key insight**
- Vercel needs a clear separation between:
  - **static output** (served from `public/` or an `outputDirectory`)
  - **serverless functions** (Python files under `api/`)

**Commits (high level)**
- `a681ed9` Fix vercel runtime format
- `40b2deb` Convert to Vercel serverless Python
- `6bfcc54` Rename to api/index.py for Vercel
- `0ff1872` Restore Flask for Vercel (attempted framework-based deploy)
- `22aca08` Configure static files and rewrites


### 2) Move backend to `/api/*` serverless functions

**Change**
- Switched from “deploy Flask as a framework” to “deploy Python as serverless functions”:
  - Added serverless endpoints under `api/`.
  - Frontend updated to call `"/api/analyse"` instead of localhost.

**Why**
- This avoids Flask framework auto-detection problems and matches Vercel’s most reliable Python path: **serverless functions per file**.

**Commits (high level)**
- `81579da` Refactor to use JSON for request handling and remove Flask dependencies
- `d54d5c9` Remove backend folder, use serverless API
- `1b2cd8b` Use Vercel Python serverless handlers


### 3) Fight framework auto-detection (Flask entrypoint errors)

**Symptom(s)**
- Vercel repeatedly trying to treat the repo as a Flask “framework project” and complaining about missing entrypoints.

**Fixes applied**
- Reduced signals that trigger framework detection (kept runtime “Other” style).
- Added ignores to reduce which files Vercel inspects/packages.

**Commits (high level)**
- `6205581` Add pyproject.toml for serverless Python (attempt to influence build)
- `fa0cac7` Remove pyproject.toml to disable Flask detection
- `33af975` Add .vercelignore to prevent Flask detection
- `cf930af` Force Vercel framework Other


### 4) Final architecture: static UI + serverless API

**Static frontend**
- The UI is served from `public/index.html`.

**Serverless backend**
- `api/index.py` (GET) returns a small JSON health/info payload.
- `api/analyse.py` (POST/OPTIONS) performs password scoring via `zxcvbn` and returns JSON.

**Core configuration**
- `vercel.json` forces a non-framework deployment and SPA-friendly rewrites.
- Root `requirements.txt` contains Python dependencies for serverless functions.


## Production Break/Fix Log (Most recent debugging)

### A) `/` returned 404 (NOT_FOUND)

**Cause**
- Vercel wasn’t treating `public/` as the output directory, so nothing was mapped to `/`.

**Fix**
- Updated `vercel.json` to set:
  - `"outputDirectory": "public"`

**Result**
- `GET /` started returning `200` and serving the HTML.


### B) `POST /api/analyse` returned 500 (FUNCTION_INVOCATION_FAILED)

**Observed behavior**
- Some code paths worked (e.g., `POST {}` returned a JSON 400), but requests that reached the `zxcvbn` call crashed the function hard.

**Root cause (practical)**
- Serverless functions can fail *before* you can return JSON if any unhandled exception occurs during response construction/serialization.
- `zxcvbn` can return values that aren’t always JSON-friendly (or shapes that differ across versions), and any such error can cause a platform-level invocation failure.

**Fixes applied (in `api/analyse.py`)**
- Import `zxcvbn` inside the request handler and wrap it with `try/except`.
- Use safe `dict.get()` extraction for nested fields.
- Make response sending robust:
  - `json.dumps(payload, default=str)`
  - guard `wfile.write()` so even unexpected IO issues don’t kill the runtime
- Normalize `guesses` to an integer when possible.

**Result**
- `POST /api/analyse` now returns `200` JSON responses successfully.


## Current Deployment State (Verified 2026-03-31)

- Production alias: `https://password-strength-analyser-two.vercel.app`
- `GET /` → `200` (static UI)
- `GET /api` → `200` JSON
- `POST /api/analyse` → `200` JSON


## Notes About Git vs Deployed State

As of 2026-03-31, these files have **local changes** that were deployed via `vercel --prod` but are not yet committed to git:

- `vercel.json`
- `api/analyse.py`

To make the repo match production, commit them:

```bash
git add vercel.json api/analyse.py
git commit -m "Fix Vercel static output and stabilise analyse API"
```


## Final Serverless Architecture Summary

- Static: `public/index.html` served at `/`.
- Serverless:
  - `api/index.py` → `/api`
  - `api/analyse.py` → `/api/analyse`
- Python runtime: Vercel deploy metadata shows `python3.12` for the serverless lambdas.
- Dependencies: root `requirements.txt` (at minimum `zxcvbn`).
