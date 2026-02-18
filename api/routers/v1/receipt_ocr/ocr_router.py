from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from api.routers.v1.authentication.auth_outh2 import get_current_user
from api import service
from api.routers.v1.receipt_ocr import ocr_repository as repo

router = APIRouter(prefix="/api/v1/receipt_ocr", tags=["Receipt OCR"])


@router.post("/", status_code=status.HTTP_200_OK)
async def ocr_image(
    file: UploadFile = File(...), current_user: service.User = Depends(get_current_user)
):
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported image type",
        )

    image_bytes = await file.read()

    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Empty image file"
        )

    return repo.process_image(image_bytes)
