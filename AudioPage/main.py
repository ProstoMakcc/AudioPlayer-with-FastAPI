from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import shutil
from typing import List

app = FastAPI()

class Track(BaseModel):
    id: int
    title: str
    artist: str
    path: str

tracks = []

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root():
    tracks_list = ""
    for track in tracks:
        tracks_list += f"<li>{track.title} - {track.artist} <a href='/tracks/{track.id}'>Play</a></li>"

    with open("templates/index.html", "r") as file:
        html_content = file.read()
    file.close()

    return HTMLResponse(content=html_content.replace("<!-- TRACKS_LIST -->", tracks_list), status_code=200)

@app.get("/tracks", response_model=List[Track])
def get_tracks():
    return tracks

@app.get("/tracks/{track_id}", response_class=HTMLResponse)
def get_track(track_id: int):
    for track in tracks:
        if track.id == track_id:
            track = track
            break
    else:
        raise HTTPException(status_code=404, detail="Track not found")

    with open("templates/track.html", "r") as file:
        html_content = file.read()
    file.close()

    return HTMLResponse(content=html_content.replace("<!-- TRACK_PATH -->", track.path).replace("<!-- TRACK_TITLE -->", track.title), status_code=200)

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
