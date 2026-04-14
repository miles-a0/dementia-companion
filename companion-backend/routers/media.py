import os
import logging
import httpx
from fastapi import APIRouter, Query
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["media"])

IMMICH_URL = os.environ.get("IMMICH_URL", "http://immich-server:3001")
IMMICH_API_KEY = os.environ.get("IMMICH_API_KEY")
MUSIC_DIR = os.environ.get("MUSIC_DIR", "/app/music")


def get_immich_headers():
    return {"x-api-key": IMMICH_API_KEY} if IMMICH_API_KEY else {}


@router.get("/media/photos")
async def get_photos(album: str = Query(default=""), user_id: int = Query(default=1)):
    if not IMMICH_API_KEY:
        return {"photos": [], "error": "IMMICH_API_KEY not configured"}
    
    if not album:
        return {"photos": [], "error": "Album name required"}
    
    logger.info("Fetching photos for album: {}".format(album))
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            # Get all albums
            response = await client.get(
                "{}/api/albums".format(IMMICH_URL),
                headers=get_immich_headers()
            )
            response.raise_for_status()
            albums = response.json()
            logger.info("Albums response: {}".format(albums[:2]))  # Log first 2 albums
            
            album_id = None
            album_name = None
            for a in albums:
                if a.get("albumName", "").lower() == album.lower():
                    album_id = a.get("id")
                    album_name = a.get("albumName")
                    break
            
            if not album_id:
                logger.info("Album not found: {}".format(album))
                return {"photos": [], "error": "Album not found"}
            
            # Get album details - Immich might have assets nested differently
            album_response = await client.get(
                "{}/api/albums/{}".format(IMMICH_URL, album_id),
                headers=get_immich_headers()
            )
            album_response.raise_for_status()
            album_data = album_response.json()
            logger.info("Album data keys: {}".format(album_data.keys()))
            
            # Try different possible locations for assets
            assets = []
            if "assets" in album_data:
                assets = album_data.get("assets", [])
            elif "assets" in album_data.get("album", {}):
                assets = album_data.get("album", {}).get("assets", [])
            elif "items" in album_data:
                assets = album_data.get("items", [])
                
            logger.info("Found {} assets".format(len(assets)))
            
            photos = []
            for asset in assets:
                asset_type = asset.get("type", "")
                logger.info("Asset type: {}".format(asset_type))
                
                if asset_type != "image":
                    continue
                
                asset_id = asset.get("id")
                exif_info = asset.get("exifInfo", {})
                
                photo = {
                    "id": asset_id,
                    "thumbnail_url": "{}/api/assets/{}/thumbnail?size=preview".format(IMMICH_URL, asset_id),
                    "full_url": "{}/api/assets/{}/original".format(IMMICH_URL, asset_id),
                    "description": exif_info.get("description") or "",
                    "date_taken": exif_info.get("dateTimeOriginal") or asset.get("fileCreatedAt") or ""
                }
                photos.append(photo)
            
            logger.info("Returning {} photos".format(len(photos)))
            return {"photos": photos, "album_name": album_name, "count": len(photos)}
    
        except Exception as e:
            logger.error("Error fetching photos: {}".format(e))
            return {"photos": [], "error": str(e)}


@router.get("/media/albums")
async def get_albums():
    if not IMMICH_API_KEY:
        return {"albums": [], "error": "IMMICH_API_KEY not configured"}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                "{}/api/albums".format(IMMICH_URL),
                headers=get_immich_headers()
            )
            response.raise_for_status()
            albums = response.json()
        
        album_list = []
        for a in albums:
            album_list.append({
                "id": a.get("id"),
                "name": a.get("albumName"),
                "asset_count": a.get("assetCount", 0)
            })
        
        return {"albums": album_list}
    
    except Exception as e:
        logger.error("Error fetching albums: {}".format(e))
        return {"albums": [], "error": str(e)}


@router.get("/media/music")
async def get_music():
    tracks = []
    
    try:
        if not os.path.isdir(MUSIC_DIR):
            return {"tracks": [], "error": "Music directory not found"}
        
        music_extensions = [".mp3", ".m4a", ".ogg", ".wav"]
        
        for filename in os.listdir(MUSIC_DIR):
            ext = os.path.splitext(filename)[1].lower()
            if ext in music_extensions:
                title = os.path.splitext(filename)[0]
                tracks.append({
                    "title": title,
                    "artist": "",
                    "url": "/api/media/stream/{}".format(filename)
                })
        
        return {"tracks": tracks}
    
    except Exception as e:
        logger.error("Error fetching music: {}".format(e))
        return {"tracks": [], "error": str(e)}


@router.get("/media/stream/{filename}")
async def stream_music(filename: str):
    filepath = os.path.join(MUSIC_DIR, filename)
    
    if not os.path.isfile(filepath):
        return {"error": "File not found"}, 404
    
    return FileResponse(filepath, media_type="audio/mpeg")