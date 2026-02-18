import logging
from fastapi import HTTPException, status
from .ocr_model import run_ocr

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s:%(message)s")
file_handler = logging.FileHandler("logs/line_clearance.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def process_image(image_bytes: bytes):
    try:
        return run_ocr(image_bytes)
    except ValueError as ve:
        logger.error(f"Value error in OCR: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input or model output: {str(ve)}",
        )
    except OpenAIError as oe:
        logger.error(f"OpenAI service error: {oe}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OpenAI service unavailable or rate-limited",
        )
    except Exception as e:
        logger.exception("OCR processing failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="OCR processing failed – please try again later",
        )
