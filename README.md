# Weekly Tracker Monorepo
This repository is split into two separate apps:

- `time-tracker/`: static weekly tracker (HTML/CSS/JS, localStorage)
- `sign-detector/`: dynamic Flask app with login/register and SQLite-backed data

## Why login/register was failing before
The server needed database initialization in deployed environments.  
`sign-detector/app.py` now runs `init_db()` at startup, so required tables are created automatically from `sign-detector/schema.sql`.

## Deployment
### 1) Static app (`time-tracker`) → GitHub Pages
- A workflow is included at `.github/workflows/deploy-time-tracker.yml`.
- On push to `main` (changes under `time-tracker/`), it deploys the static app to GitHub Pages.

### 2) Dynamic app (`sign-detector`) → Vercel
- Entry point is explicit: `sign-detector/api/index.py` (imports Flask `app`).
- You can deploy either:
  - Repo root (uses root `vercel.json`), or
  - `sign-detector` as Root Directory (uses `sign-detector/vercel.json`)
- Add environment variables:
  - `SECRET_KEY` = strong random secret
  - `DATABASE_PATH` = `/tmp/studysystem.db` (works, but ephemeral on serverless)

## Important database note
Vercel serverless filesystem is ephemeral.  
SQLite at `/tmp` allows login/register to function, but data can reset between deployments/instances.  
For persistent production data, use an external managed SQL database.
