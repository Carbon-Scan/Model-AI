import os
import pandas as pd

BASE_DIR = os.path.dirname(__file__)
DATASET_PATH = os.path.join(BASE_DIR, "data", "datasets", "merged.csv")

df = pd.read_csv(DATASET_PATH)

def calculate_total(items):
    detail = []
    total = 0.0

    for item in items:
        row = df[df["Produk"].str.lower() == item["produk"].lower()]
        if row.empty:
            continue

        karbon_per_kg = float(row.iloc[0]["Karbon_kg_per_kg"])
        karbon = item["berat_kg"] * karbon_per_kg

        detail.append({
            "produk": item["produk"],
            "berat_kg": item["berat_kg"],
            "karbon": round(karbon, 2)
        })

        total += karbon

    return {
        "detail": detail,
        "total_karbon": round(total, 2)
    }
