import re
from app.nlp.matcher import match_product
from nlp.matcher import match_product


def normalize_items(text: str):
    """
    Ambil item + qty + unit dari teks struk
    """
    pattern = r'([a-zA-Z\s]+)\s(\d+\.?\d*)\s?(kg|g|gram|liter)'
    matches = re.findall(pattern, text.lower())

    items = []
    for name, qty, unit in matches:
        matched = match_product(name.strip())

        items.append({
            "raw_name": name.strip(),
            "product": matched["product"],
            "carbon_factor": matched["carbon_kg_per_kg"],
            "similarity": matched["score"],
            "qty": float(qty),
            "unit": unit
        })

    return items
