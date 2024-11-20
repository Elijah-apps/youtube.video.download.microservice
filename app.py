from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from typing import Optional
import youtube_dl  # YouTube download library

# Initialize FastAPI app
app = FastAPI()

class VideoInfo(BaseModel):
    title: str
    duration: str
    resolutions: list
    video_url: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the YouTube Video Download Microservice!"}

@app.get("/api/video/info")
def get_video_info(url: str):
    try:
        # Fetch video info using youtube-dl
        video_data = fetch_video_info(url)
        if video_data:
            return video_data
        else:
            raise HTTPException(status_code=404, detail="Video not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/video/download")
def download_video(url: str, resolution: Optional[str] = None):
    try:
        # Start downloading the video
        download_url = fetch_video_download_url(url, resolution)
        if download_url:
            return {"message": "Download started.", "file_url": download_url}
        else:
            raise HTTPException(status_code=404, detail="Video not found or resolution unavailable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Simulated functions to fetch video info and download URLs
def fetch_video_info(url: str) -> VideoInfo:
    try:
        ydl_opts = {
            'quiet': True,
            'format': 'best',
            'extractor_args': {'youtube': {'skip_download': True}},  # Skip the actual download, just extract info
        }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', 'Unknown Title')
            duration = str(info_dict.get('duration', '0'))  # Duration in seconds
            resolutions = [format['format_note'] for format in info_dict['formats']]
            return VideoInfo(title=title, duration=duration, resolutions=resolutions, video_url=url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def fetch_video_download_url(url: str, resolution: Optional[str] = None) -> str:
    try:
        ydl_opts = {
            'quiet': True,
            'format': resolution if resolution else 'best',
        }
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            download_url = info_dict['formats'][0]['url']  # Returning the first available download URL
            return download_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
