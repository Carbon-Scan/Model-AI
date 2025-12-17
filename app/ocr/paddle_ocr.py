from paddleocr import PaddleOCR
import cv2
import numpy as np
import tempfile

ocr = PaddleOCR(lang="id", use_angle_cls=True)

def extract_text(upload_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(upload_file.file.read())
        path = tmp.name

    img = cv2.imread(path)
    result = ocr.ocr(img)

    texts = []
    for block in result:
        for line in block:
            texts.append(line[1][0])

    return " ".join(texts).lower()
