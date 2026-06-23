from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.material import Material
from app.services.storage_service import upload_file
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/upload", tags=["Upload"])

ALLOWED_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "video/mp4", "video/webm",
    "application/pdf",
    "text/plain",
}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


@router.post("")
async def upload_material(
    file: UploadFile = File(...),
    game_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a file (image/video/document) to MinIO."""
    # Validate file type
    if file.content_type and file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"File type '{file.content_type}' not allowed")

    # Validate file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 20MB)")
    # Reset file pointer
    await file.seek(0)

    # Upload to MinIO
    file_url = await upload_file(file, folder="materials")

    # Save to DB if game_id provided
    if game_id:
        material = Material(
            game_id=game_id,
            file_name=file.filename or "unnamed",
            file_url=file_url,
            file_type=file.content_type or "",
        )
        db.add(material)
        db.commit()

    return {
        "file_url": file_url,
        "file_name": file.filename,
        "file_type": file.content_type,
    }
