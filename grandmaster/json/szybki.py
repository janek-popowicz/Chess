import json

# Konfiguracja
INPUT_FILE = "super arcymistrz.json"
OUTPUT_FILE = "trimmed.json"
ENTRIES_TO_REMOVE = int(input("Ile usunąć: "))  # Liczba usuwanych wpisów

# Wczytaj JSON
with open(INPUT_FILE, "r") as f:
    data = json.load(f)

# Usuń ostatnie wpisy
keys = list(data.keys())
for key in keys[-ENTRIES_TO_REMOVE:]:
    del data[key]

# Zapisz mniejszy JSON
with open(OUTPUT_FILE, "w") as f:
    json.dump(data, f, separators=(',', ':'))

print(f"Usunięto {ENTRIES_TO_REMOVE} wpisów. Zapisano jako {OUTPUT_FILE}")
