from nlp.matcher import match_product

tests = [
    "beras putih",
    "daging sapi segar",
    "telur ayam",
    "minyak goreng"
]

for t in tests:
    print(t, "→", match_product(t))
