import os
import pandas as pd
from rapidfuzz import process, fuzz

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "data", "datasets", "merged.csv")

df = pd.read_csv(DATASET_PATH)
df["Produk_lower"] = df["Produk"].str.lower()

products = df["Produk_lower"].tolist()


def match_products_from_text(text: str, threshold: int = 70):
    results = []

    # 1. normalize OCR text
    lines = [
        line.strip().lower()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines:
        match = process.extractOne(
            line,
            products,
            scorer=fuzz.token_set_ratio
        )

        if match and match[1] >= threshold:
            row = df[df["Produk_lower"] == match[0]].iloc[0]

            results.append({
                "produk": row["Produk"],
                "karbon_kg_per_kg": float(row["Karbon_kg_per_kg"]),
                "kategori": row["Kategori"],
                "confidence": match[1]
            })

    return results
