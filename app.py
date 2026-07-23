from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import yt_dlp
import os
import uuid
import json
import time
from typing import Dict
import threading

app = FastAPI(title="YouTube Downloader")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Temporary folder for downloads
TEMP_FOLDER = "/tmp" if os.name != 'nt' else os.path.join(os.getcwd(), "temp_downloads")
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Store progress for each download
download_progress: Dict[str, Dict] = {}

# Request models
class InfoRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    format_id: str

# ============ PROGRESS HOOK ============
def progress_hook(d, download_id):
    """Callback function to track download progress"""
    if d['status'] == 'downloading':
        total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
        downloaded = d.get('downloaded_bytes', 0)
        
        if total > 0:
            percent = (downloaded / total) * 100
            download_progress[download_id] = {
                'status': 'downloading',
                'percent': round(percent, 1),
                'downloaded': downloaded,
                'total': total,
                'speed': d.get('speed', 0),
                'eta': d.get('eta', 0)
            }
    elif d['status'] == 'finished':
        download_progress[download_id] = {
            'status': 'finished',
            'percent': 100
        }
    elif d['status'] == 'error':
        download_progress[download_id] = {
            'status': 'error',
            'error': str(d.get('error', 'Unknown error'))
        }

# ============ ROUTES ============

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/info")
async def get_video_info(request: InfoRequest):
    """Get video information and available formats"""
    try:
        url = request.url
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            "impersonate" : "chrome-136",
            'force_generic_extractor': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Get ALL formats
            formats = []
            seen_qualities = set()
            
            for f in info.get('formats', []):
                height = f.get('height')
                ext = f.get('ext', '')
                filesize = f.get('filesize', 0)
                format_id = f['format_id']
                acodec = f.get('acodec', 'none')
                vcodec = f.get('vcodec', 'none')
                
                if not height:
                    continue
                
                if ext not in ['mp4', 'webm']:
                    continue
                
                quality_label = f"{height}p"
                
                if quality_label in seen_qualities:
                    continue
                    
                seen_qualities.add(quality_label)
                
                has_audio = acodec != 'none'
                format_note = f.get('format_note', '')
                
                formats.append({
                    'quality': quality_label,
                    'format_id': format_id,
                    'ext': ext,
                    'filesize': filesize,
                    'has_audio': has_audio,
                    'format_note': format_note
                })
            
            formats.sort(key=lambda x: int(x['quality'].replace('p', '')), reverse=True)
            
            return {
                "title": info.get('title', 'Unknown'),
                "thumbnail": info.get('thumbnail', ''),
                "formats": formats
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/download")
async def download_video(request: DownloadRequest):
    """Download the video with selected quality"""
    try:
        url = request.url
        format_id = request.format_id
        
        # Generate unique download ID
        download_id = str(uuid.uuid4())
        
        # Generate unique filename
        filename = f"{uuid.uuid4().hex}.mp4"
        filepath = os.path.join(TEMP_FOLDER, filename)
        
        # Initialize progress
        download_progress[download_id] = {'status': 'starting', 'percent': 0}
        
        ydl_opts = {
            'format': f'{format_id}+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': filepath,
            'quiet': True,
            'no_warnings': True,
            "impersonate" : "chrome-136",
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
        }
        
        # Start download in a background thread
        def download_thread():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    video_title = info.get('title', 'video')
                    download_progress[download_id]['title'] = video_title
                    download_progress[download_id]['filepath'] = filepath
            except Exception as e:
                download_progress[download_id] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()
        
        return {"download_id": download_id}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/progress/{download_id}")
async def get_progress(download_id: str):
    """Get download progress"""
    progress = download_progress.get(download_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Download not found")
    return progress

@app.get("/api/download-file/{download_id}")
async def download_file(download_id: str):
    """Download the completed file"""
    progress = download_progress.get(download_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Download not found")
    
    if progress.get('status') != 'finished':
        raise HTTPException(status_code=400, detail="Download not finished")
    
    filepath = progress.get('filepath')
    title = progress.get('title', 'video')
    
    if not filepath or not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Clean the title for filename
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    
    # Return the file and delete it after sending
    return FileResponse(
        path=filepath,
        filename=f"{safe_title}.mp4",
        media_type="video/mp4",
        background=lambda: os.remove(filepath) if os.path.exists(filepath) else None
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)