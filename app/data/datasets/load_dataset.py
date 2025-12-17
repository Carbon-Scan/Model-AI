import csv
import os

DATASET_PATH = os.path.join(
    os.path.dirname(__file__),
    "merged.csv"
)

def load_dataset():
    data = []

    with open(DATASET_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                "name": row["Produk"].lower().strip(),
                "carbon": float(row["Karbon_kg_per_kg"]),
                "category": row["Kategori"]
            })

    return data
