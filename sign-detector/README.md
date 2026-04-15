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
- Root directory: `sign-detector`
- Config file: `vercel.json`
- Required environment variable:
  - `SECRET_KEY`
- Optional:
  - `DATABASE_PATH=/tmp/studysystem.db`

## Notes
- DB schema is created automatically on startup.
- SQLite on Vercel is ephemeral; use external SQL for persistent production data.
