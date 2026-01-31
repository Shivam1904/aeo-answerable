"""
FastAPI Backend for AEO Scanner.

Provides HTTP endpoints to trigger scans and poll for results.
"""

import uuid
from typing import Dict, Any, Literal
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

from .config import Settings
from .crawler import Crawler
from .rendered_crawler import RenderedCrawler

app = FastAPI(title="AEO Scanner API", version="0.1.0")

# Allow CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage (MVP)
jobs: Dict[str, Dict[str, Any]] = {}


# --- Request/Response Models ---
class ScanRequest(BaseModel):
    url: HttpUrl
    mode: Literal["fast", "rendered"] = "fast"
    max_pages: int = 50


class ScanResponse(BaseModel):
    job_id: str


class JobStatus(BaseModel):
    status: Literal["pending", "running", "complete", "error"]
    progress: Dict[str, Any] | None = None
    result: Dict[str, Any] | None = None
    error: str | None = None


# --- Background Task ---
async def run_scan(job_id: str, url: str, mode: str, max_pages: int):
    """Background task to execute the scan."""
    jobs[job_id]["status"] = "running"
    
    try:
        settings = Settings(
            start_url=url,
            max_pages=max_pages,
            mode=mode
        )
        
        if mode == "rendered":
            crawler = RenderedCrawler(settings)
        else:
            crawler = Crawler(settings)
        
        # Run the scan
        result = await crawler.scan()
        
        jobs[job_id]["status"] = "complete"
        jobs[job_id]["result"] = result
        
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)


# --- Endpoints ---
@app.post("/api/scan", response_model=ScanResponse)
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """
    Start a new AEO scan.
    
    Returns a job_id that can be polled for status.
    """
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "status": "pending",
        "progress": {"pages_scanned": 0},
        "result": None,
        "error": None
    }
    
    # Schedule the scan in background
    background_tasks.add_task(run_scan, job_id, str(request.url), request.mode, request.max_pages)
    
    return ScanResponse(job_id=job_id)


@app.get("/api/scan/{job_id}", response_model=JobStatus)
async def get_scan_status(job_id: str):
    """
    Get the status of a scan job.
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return JobStatus(
        status=job["status"],
        progress=job.get("progress"),
        result=job.get("result"),
        error=job.get("error")
    )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
