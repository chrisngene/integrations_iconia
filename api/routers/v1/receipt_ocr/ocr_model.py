import os
import base64
import json
import logging
from typing import Dict, List, Any
from dotenv import dotenv_values
from openai import OpenAI, OpenAIError

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s:%(message)s")
file_handler = logging.FileHandler(filename="logs/line_clearance.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

config = dotenv_values(".env")
OPENAI_API_KEY = config.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    logger.critical("OPENAI_API_KEY not found in .env file")
    raise ValueError("Missing OPENAI_API_KEY in environment")

client = OpenAI(api_key=OPENAI_API_KEY)

# Optional: if you want to keep preprocessing (requires opencv-python-headless)
# import cv2
# import numpy as np
# def preprocess_image(image_bytes: bytes) -> bytes:
#     ... (your previous OpenCV code here)
#     return processed_bytes


def run_ocr(image_bytes: bytes) -> Dict[str, Any]:
    logger.info("Starting GPT-4o vision OCR request")

    # Optional preprocessing (uncomment if desired)
    # try:
    #     processed_bytes = preprocess_image(image_bytes)
    # except Exception as e:
    #     logger.warning(f"Preprocessing failed, using raw image: {e}")
    #     processed_bytes = image_bytes
    processed_bytes = image_bytes  # using raw for now

    base64_image = base64.b64encode(processed_bytes).decode("utf-8")

    prompt = """
You are an expert at extracting line items from handwritten or photographed Kenyan sales orders, local purchase orders, or agrovet order sheets.

The image shows a sales/purchase order that may contain:
- Messy handwriting or OCR errors
- Broken lines or merged text
- Packaging like 50g, 100g, 1kg, 500ml, x24 x500G, ctn, pkt, bag, pcs
- Common agrovet brands (e.g. Skana, Oshothane, Aquawet, Duma, Alpha, etc.)

Your task is to extract ONLY the order line items as a list.
Completely IGNORE:
- Company names, supplier/customer, addresses, P.O. Box, phone numbers
- Order number, dates, order sheet title
- Totals, subtotals, VAT, grand total, payments
- Signatures, prepared by, delivery notes, footers/headers

For each line item, return:
- from_ocr_product_name (string): the product description exactly as inferred from the text (cleaned of obvious noise, but keep original wording/style as much as possible — do NOT fully normalize or invent names)
- qty (number): the quantity (infer as integer if unclear)

EXTRACTION RULES:
1. Identify lines that contain a product name + quantity/packaging.
2. The FIRST clear number before or near packaging is usually the quantity.
3. Packaging/size details (50g, 250g, 1KG, 100ml, x 10 x 500G, etc.) belong in from_ocr_product_name — NOT in qty.
4. If a product is broken across lines due to OCR/layout, reconstruct it logically into one item.
5. Correct only very obvious OCR/handwriting errors in the product name:
   - "Svana", "Scans", "Schns", "Sctns" → "Skana"
   - "509", "S09", "sorg" → "50g"
   - "IKS", "loctric", "IRG" → "1kg"
   - "AJuaWit", "Aguawpt" → "Aquawet"
   - "O" → "0" and "l" → "1" when part of numbers
   - "SL" → "5L" (or similar common patterns)
6. If quantity is missing/unreadable, use the most reasonable inference from context (or 1 if no clue).
7. Return each appearance of the same product as separate items — do NOT merge duplicates.
8. If no valid line items are found, return an empty array [].

Output ONLY valid JSON — a RAW ARRAY of objects.
- Start with [ and end with ]
- Use DOUBLE QUOTES only
- No explanations, no markdown, no extra text
- No trailing commas
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # or "gpt-4o-mini"
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1500,
            temperature=0.0,
        )

        raw_content = response.choices[0].message.content.strip()

        # Handle common markdown wrapping
        if raw_content.startswith("```json"):
            raw_content = raw_content.split("```json", 1)[1].split("```", 1)[0].strip()
        elif raw_content.startswith("```"):
            raw_content = raw_content.split("```", 2)[1].strip()

        # Parse JSON array
        try:
            items: List[Dict[str, Any]] = json.loads(raw_content)
            if not isinstance(items, list):
                raise ValueError("Response is not a JSON array")
        except json.JSONDecodeError as je:
            logger.error(f"JSON parse error: {je} | raw: {raw_content[:200]}...")
            raise ValueError("Invalid JSON format from model")

        logger.info(f"GPT-4o OCR successful | items_count={len(items)}")

        return {
            "items": items,
            "source": "gpt-4o-vision",
            "count": len(items),
            "raw_response_preview": raw_content[:300] + "..."
            if len(raw_content) > 300
            else raw_content,
        }

    except OpenAIError as oe:
        logger.exception("OpenAI API error")
        raise
    except Exception as e:
        logger.exception("Unexpected error in GPT-4o OCR")
        raise
