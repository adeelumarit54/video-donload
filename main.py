from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import yt_dlp
import os
import uuid

app = FastAPI(title="Adeel Video Downloader")

# ✅ CORS setup
origins = [
    "http://localhost:5173",
    "https://video-downloader-production.up.railway.app",
    "https://prodownloadfrontend.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Serve frontend if built
# frontend_dir = os.path.join(os.path.dirname(__file__), "../frontend/dist")
# if os.path.exists(frontend_dir):
#     app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
def home():
    return {"message": "Adeel Video Downloader API is running 🚀"}


# ✅ Request body
class VideoRequest(BaseModel):
    url: str


@app.post("/download")
def download_video(request: VideoRequest):
    url = request.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="No URL provided")

    # Create downloads folder
    os.makedirs("downloads", exist_ok=True)

    # Unique filename
    output_filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join("downloads", output_filename)

    # ✅ yt_dlp options
    ydl_opts = {
        "outtmpl": output_path,
        "format": "best[ext=mp4]/best",  # Safe for YouTube without ffmpeg
        "quiet": True,
        "noplaylist": True,  # Avoid downloading playlists accidentally
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print("YT_DLP ERROR:", str(e))  # Log for debugging
        raise HTTPException(status_code=400, detail=f"Download failed: {str(e)}")

    if not os.path.exists(output_path):
        raise HTTPException(status_code=400, detail="Video download failed")

    return FileResponse(
        path=output_path,
        filename="video.mp4",
        media_type="video/mp4",
    )


# # Serve frontend for other routes
# @app.get("/{full_path:path}")
# def serve_react_app(full_path: str):
#     index_path = os.path.join(frontend_dir, "index.html")
#     if os.path.exists(index_path):
#         return FileResponse(index_path)
#     else:
#         return {"message": "Frontend not built yet"}
