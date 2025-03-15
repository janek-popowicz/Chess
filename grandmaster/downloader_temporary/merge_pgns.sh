#!/bin/bash

# Katalog z plikami (zmień, jeśli Selenium zapisało je gdzie indziej)
PGN_DIR="$HOME/Downloads"

# Plik wynikowy
OUTPUT_FILE="next_one_all_games.pgn"

# Sprawdzenie, czy są pliki do połączenia
if ls "$PGN_DIR"/master_games*.pgn 1> /dev/null 2>&1; then
    echo "🔍 Znaleziono pliki PGN. Łączenie w jeden..."

    # Scalanie plików w jeden, zachowując kolejność
    cat "$PGN_DIR"/master_games*.pgn | awk '!seen[$0]++' > "$PGN_DIR/$OUTPUT_FILE"

    echo "✅ Połączono wszystkie pliki w $PGN_DIR/$OUTPUT_FILE"
else
    echo "⚠️ Brak plików PGN do połączenia w $PGN_DIR!"
fi
