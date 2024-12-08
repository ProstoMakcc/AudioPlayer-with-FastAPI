from fastapi import FastAPI, UploadFile, HTTPException, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from typing import List
from database import engine
from sqlalchemy.orm import sessionmaker, Session
import schemas
import shutil
import models

models.Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

tracks = []

app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=Request)
def read_root(request: Request, db: Session = Depends(get_db)):
    all_tracks = db.query(models.Track).all()
    return templates.TemplateResponse("index.html", {"request": request, "tracks": all_tracks})

@app.get("/tracks", response_model=List[schemas.Track])
def get_tracks(db: Session = Depends(get_db)):
    return db.query(models.Track).all()

@app.get("/tracks/{track_id}", response_class=Request)
def get_track_by_id(request: Request, track_id: int, db: Session = Depends(get_db)):
    track_by_id = db.query(models.Track).filter(models.Track.id == track_id).first()

    if not track_by_id:
        raise HTTPException(status_code=404, detail="Track not found")
    
    return templates.TemplateResponse("track.html", {"request": request, "track_title": track_by_id.title, "path": track_by_id.path})

@app.get("/search/{track_name}", response_class=Request)
def get_track_by_name(request: Request, track_name: str, db: Session = Depends(get_db)):
    results = db.query(models.Track).filter(models.Track.name == track_name).all()

    if not results:
        raise HTTPException(status_code=404, detail="No tracks found")

    return templates.TemplateResponse("index.html", {"request": request, "tracks": results})

@app.post("/tracks", response_model=schemas.Track)
def add_track(track: schemas.TrackCreate, db: Session = Depends(get_db)):
    db_track = models.Track(**track.dict())
    db.add(db_track)
    db.commit()
    db.refresh(db_track)
    return db_track

@app.delete("/tracks/{track_id}")
def delete_track(track_id: int, db: Session = Depends(get_db)):
    track = db.query(models.Track).filter(models.Track.id == track_id).first()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    db.delete(track)
    db.commit()

    return {"message": "Track deleted"}

@app.put("/tracks/{track_id}")
def update_track(track_id: int, new_track: schemas.TrackUpdate, db: Session = Depends(get_db)):
    track = db.query(models.Track).filter(models.Track.id == track_id).first()

    if not track:
        raise HTTPException(status_code=404, detail="No track found")

    for var, value in vars(new_track).items():
        setattr(track, var, value) if value else None

    db.commit()
    return {"message": "Track updated"}

@app.post("/tracks/upload")
def upload_file(file: UploadFile = Form(...), db: Session = Depends(get_db)):
    upload_path = f"static/uploads/{file.filename}"

    with open(upload_path, "wb") as folder:
        shutil.copyfileobj(file.file, folder)

    web_path = f"/static/uploads/{file.filename}"
    new_track = models.Track(title=file.filename, artist="Unknown", path=web_path)
    db.add(new_track)
    db.commit()

    return RedirectResponse(url="/", status_code=303)
