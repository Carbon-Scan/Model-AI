from carbon.calculator import calculate_total

items = [
    {
        "produk": "Beras Putih",
        "berat_kg": 2.0,
        "karbon_kg_per_kg": 4.0
    },
    {
        "produk": "Daging Sapi",
        "berat_kg": 0.3,
        "karbon_kg_per_kg": 27.0
    }
]

result = calculate_total(items)
print(result)
