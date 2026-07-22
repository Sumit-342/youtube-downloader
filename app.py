from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import yt_dlp
import os
import uuid

app = FastAPI(title="YouTube Downloader")

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Temporary folder for downloads
TEMP_FOLDER = "/tmp" if os.name != 'nt' else os.path.join(os.getcwd(), "temp_downloads")
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Request models
class InfoRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    format_id: str

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
                
                # Skip formats without video
                if not height:
                    continue
                
                # Skip formats that aren't mp4 (for better compatibility)
                if ext not in ['mp4', 'webm']:
                    continue
                
                quality_label = f"{height}p"
                
                # Skip duplicates (keep best quality per resolution)
                if quality_label in seen_qualities:
                    continue
                    
                seen_qualities.add(quality_label)
                
                # Check if this format has audio
                has_audio = acodec != 'none'
                
                # Format note (like 720p, 1080p, etc.)
                format_note = f.get('format_note', '')
                
                formats.append({
                    'quality': quality_label,
                    'format_id': format_id,
                    'ext': ext,
                    'filesize': filesize,
                    'has_audio': has_audio,
                    'format_note': format_note
                })
            
            # Sort by quality (highest first)
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
        
        # Generate unique filename
        filename = f"{uuid.uuid4().hex}.mp4"
        filepath = os.path.join(TEMP_FOLDER, filename)
        
        ydl_opts = {
            'format': f'{format_id}+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': filepath,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'video')
        
        # Clean the title for filename
        safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        # Return the file and delete it after sending
        return FileResponse(
            path=filepath,
            filename=f"{safe_title}.mp4",
            media_type="video/mp4",
            background=lambda: os.remove(filepath) if os.path.exists(filepath) else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "alive"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)