import json
import cloudscraper
from datetime import datetime

def fetch_chess_games(username, year, month):
    scraper = cloudscraper.create_scraper()
    url = f"https://api.chess.com/pub/player/{username}/games/{year}/{month:02d}"
    response = scraper.get(url)
    
    if response.status_code == 200:
        return response.json().get("games", [])
    else:
        print(f"Błąd {response.status_code}: {response.text}")
        return []

def save_games(games, username, year, month):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pgn_filename = f"{username}_games_{year}_{month}_{timestamp}.pgn"
    
    
    # Zapis do PGN
    with open(pgn_filename, "w", encoding="utf-8") as pgn_file:
        for game in games:
            pgn_file.write(game["pgn"] + "\n\n")
    
    print(f"Zapisano partie w: {pgn_filename}")

if __name__ == "__main__":
    username = "MagnusCarlsen"  # Możesz podmienić na dowolnego gracza
    for year in range(2000, 2026):
        for month in range(1, 13):
            games = fetch_chess_games(username, year, month)
            if games:
                save_games(games, username, year, month)
            else:
                print("Brak partii do zapisania.", year, month)
