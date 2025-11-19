import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Album, Photo

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Album Share API"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Helper to validate ObjectId strings

def to_object_id(id_str: str) -> ObjectId:
    if not ObjectId.is_valid(id_str):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    return ObjectId(id_str)

# Albums Endpoints

@app.post("/api/albums", status_code=201)
async def create_album(payload: Album):
    slug = payload.slug
    # ensure slug unique if provided
    if slug:
        existing = db["album"].find_one({"slug": slug})
        if existing:
            raise HTTPException(status_code=400, detail="Slug already in use")
    album_id = create_document("album", payload)
    return {"id": album_id}

@app.get("/api/albums")
async def list_albums():
    albums = get_documents("album", {}, limit=None)
    # convert ObjectId to string
    for a in albums:
        a["id"] = str(a.pop("_id"))
    return {"items": albums}

@app.get("/api/albums/{album_id}")
async def get_album(album_id: str):
    doc = db["album"].find_one({"_id": to_object_id(album_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Album not found")
    doc["id"] = str(doc.pop("_id"))
    return doc

# Photos Endpoints

@app.post("/api/albums/{album_id}/photos", status_code=201)
async def add_photo(album_id: str, payload: Photo):
    # enforce album_id consistency
    if payload.album_id != album_id:
        raise HTTPException(status_code=400, detail="album_id mismatch")
    # check album exists
    if not db["album"].find_one({"_id": to_object_id(album_id)}):
        raise HTTPException(status_code=404, detail="Album not found")
    photo_id = create_document("photo", payload)
    return {"id": photo_id}

@app.get("/api/albums/{album_id}/photos")
async def list_photos(album_id: str):
    # verify album exists
    if not db["album"].find_one({"_id": to_object_id(album_id)}):
        raise HTTPException(status_code=404, detail="Album not found")
    photos = get_documents("photo", {"album_id": album_id})
    for p in photos:
        p["id"] = str(p.pop("_id"))
    return {"items": photos}

# Public album by slug
@app.get("/api/public/{slug}")
async def get_public_album(slug: str):
    album = db["album"].find_one({"slug": slug})
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    album_id = str(album.pop("_id"))
    photos = get_documents("photo", {"album_id": album_id})
    for p in photos:
        p["id"] = str(p.pop("_id"))
    album["id"] = album_id
    album["photos"] = photos
    return album

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
