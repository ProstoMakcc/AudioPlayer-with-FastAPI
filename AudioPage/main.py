from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
import shutil
from typing import List
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

app = FastAPI()
templates = Jinja2Templates(directory="templates")

allowed_extensions = [".mp3", ".ogg", ".wav"]

class Track(BaseModel):
    id: int
    title: str = Field(min_length=5, max_length=50)
    artist: str
    path: str

    @validator("path")
    def validate_path(cls, v):
        ext = v[-4] + v[-3] + v[-2] + v[-1]
        if ext not in allowed_extensions:
            raise ValueError("Unsupported extension")
        return v

tracks = []

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=Request)
def read_root(request:Request):
    tracks_list = []
    for track in tracks:
        tracks_list.append(track)

    return templates.TemplateResponse("index.html", {"request": request, "tracks": tracks_list})

@app.get("/tracks", response_model=List[Track])
def get_tracks():
    return tracks

@app.get("/tracks/{track_id}", response_class=Request)
def get_track_by_id(request:Request, track_id: int):
    for track in tracks:
        if track.id == track_id:
            track = track
            break
    else:
        raise HTTPException(status_code=404, detail="Track not found")

    return templates.TemplateResponse("track.html", {"request": request, "track_title": track.title, "path": track.path})

@app.get("/search/{track_name}", response_class=Request)
def get_track_by_name(request:Request, track_name: str):
    results = [track for track in tracks if track_name.lower() in track.title.lower()]

    if len(results) == 0:
        raise HTTPException(status_code=404, detail="No tracks found")

    return templates.TemplateResponse("index.html", {"request": request, "tracks": results})

@app.post("/tracks", response_model=Track)
def add_track(track: Track):
    tracks.append(track)

    return track

@app.delete("/tracks/{track_id}")
def delete_track(track_id: int):
    global tracks
    tracks = [track for track in tracks if track.id != track_id]

    return {"message": "Track deleted"}

@app.put("/tracks/{track_id}")
def update_track(track_id: int, new_track: Track):
    for index, track in enumerate(tracks):
        if track.id == track_id:
            tracks[index] = new_track
            return {"message": "Track updated"}
        
    raise HTTPException(status_code=404, detail="Track not found")

@app.post("/tracks/upload")
def upload_file(file: UploadFile = Form(...)):
    upload_path = f"static/uploads/{file.filename}"

    with open(upload_path, "wb") as folder:
        shutil.copyfileobj(file.file, folder)
    folder.close()

    web_path = f"/static/uploads/{file.filename}"
    new_track = Track(id=len(tracks) + 1, title=file.filename, artist="Unknown", path=web_path)
    tracks.append(new_track)

    return RedirectResponse(url="/", status_code=303)
