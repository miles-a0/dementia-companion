import os
import logging
import httpx
import requests
from fastapi import APIRouter, Query, UploadFile, File, Form
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["media"])

IMMICH_URL = os.environ.get("IMMICH_URL", "http://immich-server:3001")
IMMICH_API_KEY = os.environ.get("IMMICH_API_KEY")
MUSIC_DIR = os.environ.get("MUSIC_DIR", "/app/music")

logger.info("=== MEDIA ROUTER INITIALIZED ===")
logger.info("IMMICH_URL: {}".format(IMMICH_URL))
logger.info("IMMICH_API_KEY set: {}".format(bool(IMMICH_API_KEY)))
logger.info("MUSIC_DIR: {}".format(MUSIC_DIR))


def get_immich_headers():
    return {"x-api-key": IMMICH_API_KEY} if IMMICH_API_KEY else {}


@router.get("/media/photos")
async def get_photos(album: str = Query(default=""), user_id: int = Query(default=1)):
    logger.info("=== get_photos START ===")
    logger.info("IMMICH_URL: {}".format(IMMICH_URL))
    logger.info("IMMICH_API_KEY set: {}".format(bool(IMMICH_API_KEY)))
    logger.info("Album param: {}".format(album))
    
    try:
        headers = get_immich_headers()
        
        # Get all albums
        response = requests.get(
            "{}/api/albums".format(IMMICH_URL),
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        albums = response.json()
        logger.info("Found {} albums".format(len(albums)))
        
        # Log all album names for debugging
        album_names = [a.get("albumName") for a in albums]
        logger.info("Album names: {}".format(album_names))
        
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
        
        # Get album details
        logger.info("Fetching album details for: {}".format(album_id))
        album_response = requests.get(
            "{}/api/albums/{}".format(IMMICH_URL, album_id),
            headers=headers,
            timeout=30
        )
        album_response.raise_for_status()
        album_data = album_response.json()
        logger.info("Album data keys: {}".format(album_data.keys()))
        logger.info("Album has assets: {}".format("assets" in album_data))
        
        # Get assets
        assets = album_data.get("assets", [])
        logger.info("Found {} assets".format(len(assets)))
        
        if assets:
            logger.info("First asset: {}".format(assets[0]))
        
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
                "thumbnail_url": "/api/media/proxy/asset/{}?size=thumbnail".format(asset_id),
                "full_url": "/api/media/proxy/asset/{}?size=original".format(asset_id),
                "description": exif_info.get("description") or "",
                "date_taken": exif_info.get("dateTimeOriginal") or asset.get("fileCreatedAt") or ""
            }
            photos.append(photo)
        
        logger.info("Returning {} photos".format(len(photos)))
        logger.info("Photos data: {}".format(photos))
        return {"photos": photos, "album_name": album_name, "count": len(photos)}
    
    except Exception as e:
        logger.error("Error fetching photos: {}".format(e))
        import traceback
        logger.error("Traceback: {}".format(traceback.format_exc()))
        return {"photos": [], "error": str(e)}


@router.get("/media/albums")
async def get_albums():
    logger.info("=== get_albums called")
    logger.info("IMMICH_URL: {}".format(IMMICH_URL))
    logger.info("IMMICH_API_KEY set: {}".format(bool(IMMICH_API_KEY)))
    
    if not IMMICH_API_KEY:
        return {"albums": [], "error": "IMMICH_API_KEY not configured"}
    
    try:
        headers = get_immich_headers()
        
        logger.info("Fetching albums from: {}/api/albums".format(IMMICH_URL))
        
        response = requests.get(
            "{}/api/albums".format(IMMICH_URL),
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        albums = response.json()
        logger.info("Found {} albums".format(len(albums)))
        
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


@router.get("/media/proxy/asset/{asset_id}")
async def proxy_asset(asset_id: str, size: str = "original"):
    if not IMMICH_API_KEY:
        return {"error": "IMMICH_API_KEY not configured"}, 500
    
    try:
        headers = get_immich_headers()
        
        if size == "thumbnail":
            url = "{}/api/assets/{}/thumbnail?size=preview".format(IMMICH_URL, asset_id)
        else:
            url = "{}/api/assets/{}/original".format(IMMICH_URL, asset_id)
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        content_type = response.headers.get("content-type", "image/jpeg")
        
        from fastapi.responses import Response
        return Response(content=response.content, media_type=content_type)
    
    except Exception as e:
        logger.error("Error proxying asset: {}".format(e))
        return {"error": str(e)}, 500


@router.post("/media/upload/photo")
async def upload_photo(
    file: UploadFile = File(...),
    album_id: str = Form(None),
    album_name: str = Form(None)
):
    if not IMMICH_API_KEY:
        return {"error": "IMMICH_API_KEY not configured"}, 500
    
    try:
        headers = get_immich_headers()
        
        target_album_id = album_id
        
        if not target_album_id and album_name:
            response = requests.get(
                "{}/api/albums".format(IMMICH_URL),
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            albums = response.json()
            
            for a in albums:
                if a.get("albumName", "").lower() == album_name.lower():
                    target_album_id = a.get("id")
                    break
        
        if not target_album_id:
            return {"error": "Album not found. Create an album in Immich first."}, 400
        
        upload_url = "{}/api/upload".format(IMMICH_URL)
        logger.info("Uploading to: {}".format(upload_url))
        logger.info("Album ID: {}".format(target_album_id))
        
        file_content = await file.read()
        logger.info("File size: {} bytes, filename: {}".format(len(file_content), file.filename))
        
        files = {"file": (file.filename, file_content, file.content_type)}
        data = {"albumId": target_album_id} if target_album_id else {}
        logger.info("Uploading with files: {}, data: {}".format(files.keys(), data))
        
        upload_response = requests.post(
            upload_url,
            headers=headers,
            files=files,
            data=data,
            timeout=60
        )
        
        logger.info("Upload response status: {}".format(upload_response.status_code))
        logger.info("Upload response body: {}".format(upload_response.text[:500] if upload_response.text else "empty"))
        
        if upload_response.status_code == 200:
            return {"message": "Photo uploaded successfully"}
        else:
            return {"error": upload_response.text}, upload_response.status_code
    
    except Exception as e:
        logger.error("Error uploading photo: {}".format(e))
        return {"error": str(e)}, 500


@router.post("/media/upload/music")
async def upload_music(file: UploadFile = File(...)):
    try:
        import aiofiles
        
        upload_dir = os.path.join(MUSIC_DIR, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        filepath = os.path.join(upload_dir, file.filename)
        
        content = await file.read()
        
        with open(filepath, "wb") as f:
            f.write(content)
        
        return {"message": "Music uploaded successfully", "filename": file.filename}
    
    except Exception as e:
        logger.error("Error uploading music: {}".format(e))
        return {"error": str(e)}, 500