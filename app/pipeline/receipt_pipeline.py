from app.ocr.ocr_space import ocr_image
from app.nlp.matcher import match_products_from_text

def run_pipeline(file):
    image_bytes = file.file.read()

    raw_text = ocr_image(image_bytes)

    detected_products = match_products_from_text(raw_text)

    return {
        "raw_text": raw_text,
        "detected_products": detected_products
    }
