import requests

API_KEY = "K89972963188957"

def ocr_image(image_bytes: bytes):
    url = "https://api.ocr.space/parse/image"

    files = {
        "file": ("image.png", image_bytes, "image/png")  # kiye sepele tapi penting
    }

    data = {
        "apikey": API_KEY,
        "language": "eng",
        "isOverlayRequired": False
    }

    response = requests.post(url, files=files, data=data)
    result = response.json()

    if result.get("IsErroredOnProcessing"):
        raise Exception(result.get("ErrorMessage"))

    return result["ParsedResults"][0]["ParsedText"]
