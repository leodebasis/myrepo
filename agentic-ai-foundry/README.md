Agentic AI Foundry
===================

This repository contains a minimal full‑stack implementation of the wireframed UI for listing AI agents and running a selected agent with real‑time logs, file uploads, and generated file downloads.

Structure
---------

- frontend: React + Vite + TypeScript app with two pages (Agents grid and Agent detail)
- backend: FastAPI service exposing endpoints to run an agent, stream logs, upload files, and list/download artifacts

Quick start
-----------

Backend

1. Create a Python virtual environment and install dependencies:

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy `backend/agent/config.sample.json` to `backend/agent/config.json` and fill in values as needed (Azure OpenAI, SMTP, etc.). Defaults allow dry‑run without credentials.

3. Run the API server:

   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

Frontend

1. Install Node dependencies and start the dev server:

   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

2. Open the printed URL (typically http://localhost:5173). The frontend expects the backend at http://localhost:8000.

Notes
-----

- The sample "Email Communicator Agent" is implemented in `backend/agent/Agent.py` and `backend/agent/tool.py`, configured entirely by `backend/agent/config.json`. No credentials or templates are hard‑coded in Python.
- Additional agents and workflows can be added by extending the config and endpoints. The UI dynamically lists agents returned by the backend.

