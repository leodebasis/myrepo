from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import AsyncGenerator, Dict, List

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse

from agent.Agent import ConfiguredAgent


BASE_DIR = Path(__file__).parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
OUTPUTS_DIR = STORAGE_DIR / "outputs"

for d in (STORAGE_DIR, UPLOADS_DIR, OUTPUTS_DIR):
    d.mkdir(parents=True, exist_ok=True)


def load_global_config() -> Dict:
    cfg_path = BASE_DIR / "agent" / "config.json"
    if not cfg_path.exists():
        # Allow running with sample
        cfg_path = BASE_DIR / "agent" / "config.sample.json"
    with cfg_path.open("r", encoding="utf-8") as f:
        return json.load(f)


app = FastAPI(title="Agentic AI Foundry API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/agents")
def list_agents():
    cfg = load_global_config()
    agents = cfg.get("agents", [])
    # Only send safe metadata
    public = [
        {
            "name": a.get("name"),
            "slug": a.get("slug"),
            "description": a.get("description"),
        }
        for a in agents
    ]
    return {"agents": public}


@app.get("/agents/{slug}")
def get_agent(slug: str):
    cfg = load_global_config()
    for a in cfg.get("agents", []):
        if a.get("slug") == slug:
            return {
                "name": a.get("name"),
                "slug": a.get("slug"),
                "description": a.get("description"),
            }
    raise HTTPException(status_code=404, detail="Agent not found")


@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    saved: List[str] = []
    for uf in files:
        target = UPLOADS_DIR / uf.filename
        content = await uf.read()
        target.write_bytes(content)
        saved.append(uf.filename)
    return {"uploaded": saved}


@app.get("/files/uploads")
def list_uploads():
    files = sorted([p.name for p in UPLOADS_DIR.glob("*") if p.is_file()])
    return {"files": files}


@app.get("/files/outputs")
def list_outputs():
    files = sorted([p.name for p in OUTPUTS_DIR.glob("*") if p.is_file()])
    return {"files": files}


@app.get("/download/{kind}/{filename}")
def download_file(kind: str, filename: str):
    if kind not in {"uploads", "outputs"}:
        raise HTTPException(status_code=400, detail="Invalid kind")
    base = UPLOADS_DIR if kind == "uploads" else OUTPUTS_DIR
    target = base / filename
    if not target.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(target)


@app.post("/run/{slug}")
async def run_agent(slug: str, prompt: str = Form("")):
    cfg = load_global_config()
    matched = None
    for a in cfg.get("agents", []):
        if a.get("slug") == slug:
            matched = a
            break
    if matched is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent = ConfiguredAgent(config=cfg, agent_slug=slug, uploads_dir=str(UPLOADS_DIR), outputs_dir=str(OUTPUTS_DIR))

    async def event_stream() -> AsyncGenerator[bytes, None]:
        async for line in agent.run(prompt=prompt):
            yield f"data: {json.dumps(line)}\n\n".encode("utf-8")
        # Signal end of stream
        yield b"event: done\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})

