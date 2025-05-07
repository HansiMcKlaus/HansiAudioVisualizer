from fastapi import FastAPI, File, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading
import webbrowser
import os
from datetime import datetime

import yt_dlp

from scripts.entrypoint import get_video_file, get_preview_image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/video", StaticFiles(directory="video"), name="video")

def get_base_url(request: Request):
    return str(request.base_url).rstrip("/")

# Example endpoint
@app.get("/random-number")
def get_random_number():
    import random
    return {"random_number": random.randint(1, 100)}

@app.post("/get-yt-meta-data")
async def get_youtube_metadata(request: Request):
    data = await request.json()
    video_url = data.get("videoURL")

    if not video_url:
        return JSONResponse(content={"error": "videoURL is required"}, status_code=400)

    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)

            if 'entries' in info_dict:
                video = info_dict['entries'][0]
            else:
                video = info_dict

            metadata = {
                "title": video.get("title"),
                "uploader": video.get("uploader"),
                "duration": video.get("duration"),
                "url": video.get("original_url"),
                "thumbnail": video.get("thumbnail"),
                "id": video.get("id"),
            }

            return metadata
    except Exception as e:
        return JSONResponse(content={"error": f"Failed to fetch metadata: {str(e)}"}, status_code=500)

@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    upload_directory = "upload"
    os.makedirs(upload_directory, exist_ok=True)
    file_path = os.path.join(upload_directory, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return { "message": "Audio uploaded successfully!" }

@app.post("/upload-audio-from-url")
async def upload_audio_from_url(request: Request):
    data = await request.json()
    audio_url_id = data.get("audioURLId")

    if not audio_url_id:
        return {"error": "No YouTube video ID provided"}

    upload_directory = "upload"
    os.makedirs(upload_directory, exist_ok=True)

    file_path = os.path.join(upload_directory, f"{audio_url_id}")

    if os.path.exists(file_path + ".mp3"):
        return { "message": "Audio already exists!" }

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': file_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(audio_url_id, download=True)
            filename = ydl.prepare_filename(info_dict)

        return { "message": "Audio uploaded successfully!" }

    except Exception as e:
        return { "error": f"Failed to download audio: {str(e)}" }

@app.post("/generate-preview-image")
async def generate_preview_image(request: Request):
    data = await request.json()
    settings = data.get("settings")

    if not settings:
        return {"error": "Settings are required"}

    filename = get_preview_image(settings)

    image_path = os.path.join("scripts", filename)
    if not os.path.exists(image_path):
        return {"error": "Preview image not found"}

    file = open(image_path, "rb")
    return StreamingResponse(file, media_type="image/png")

@app.post("/generate-video")
async def generate_video(request: Request):
    data = await request.json()
    filename = data.get("filename") 
    settings = data.get("settings")

    if not filename or not settings:
        return {"error": "Filename and settings required"}

    filename = get_video_file(filename, settings)

    video_path = os.path.join("video", filename)
    if not os.path.exists(video_path):
        return {"error": "Video file not found"}
    
    timestamp = int(datetime.utcnow().timestamp())
    video_url = f"{get_base_url(request)}/video/{filename}?t={timestamp}"
    return { "video_url": video_url }

@app.get("/download-video/{filename}")
async def download_video(filename: str):
    video_path = os.path.join("video", filename)

    if not os.path.exists(video_path):
        return {"error": "Video file not found"}

    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

if __name__ == "__main__":
    def open_browser():
        webbrowser.open_new_tab("http://localhost:5173")

    # threading.Timer(0.5, open_browser).start()
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)