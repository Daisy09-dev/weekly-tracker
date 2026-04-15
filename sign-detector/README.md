# Sign Detector (Flask)
Dynamic Flask app with:
- Registration and login
- Study scheduling and progress tracking
- SQLite database auto-initialized from `schema.sql`

## Local run
1. Create venv and install dependencies:
   - `python3 -m venv venv`
   - `source venv/bin/activate`
   - `pip install -r requirements.txt`
2. Run:
   - `python3 app.py`

## Deployment (Vercel)
- App entrypoint: `api/index.py` (loads Flask app from `app.py`)
- Deploy options:
  - Set Root Directory to `sign-detector` (uses `sign-detector/vercel.json`)
  - Or deploy repo root (uses top-level `vercel.json`)
- Required environment variable:
  - `SECRET_KEY`
- Optional:
  - `DATABASE_PATH=/tmp/studysystem.db`

## Notes
- DB schema is created automatically on startup.
- SQLite on Vercel is ephemeral; use external SQL for persistent production data.
