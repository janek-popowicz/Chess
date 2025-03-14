
#NIE DZIAŁA



import requests
import time

# Lista arcymistrzów i ich zakresy lat aktywności
players = {
    "Magnus Carlsen": (2005, 2025),
    "Hikaru Nakamura": (2000, 2025),
    "Fabiano Caruana": (2005, 2025),
    "Viswanathan Anand": (1985, 2025),
    "Garry Kasparov": (1975, 2005),
    "Bobby Fischer": (1955, 1975),
    "Jose Raul Capablanca": (1900, 1942),
    "Paul Morphy": (1850, 1869),
    "Mikhail Tal": (1950, 1992),
    "Mikhail Botvinnik": (1930, 1970),
    "Alexander Alekhine": (1910, 1946),
    "Judit Polgar": (1985, 2014)
}

# Mapping prawdziwych nazwisk do Chess.com username'ów (do uzupełnienia)
usernames = {
    "Magnus Carlsen": "MagnusCarlsen",
    "Hikaru Nakamura": "Hikaru",
    "Fabiano Caruana": "FabianoCaruana",
    "Viswanathan Anand": "vishyanand",
    "Garry Kasparov": None,  # Brak aktywnego konta
    "Bobby Fischer": None,  # Brak aktywnego konta
    "Jose Raul Capablanca": None,
    "Paul Morphy": None,
    "Mikhail Tal": None,
    "Mikhail Botvinnik": None,
    "Alexander Alekhine": None,
    "Judit Polgar": "JuditPolgar"
}

def fetch_games(username, start_year, end_year):
    """ Pobiera partie z Chess.com dla danego użytkownika w podanym zakresie lat. """
    all_games = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            url = f"https://api.chess.com/pub/player/{username}/games/{year}/{str(month).zfill(2)}"
            response = requests.get(url)
            print(response.text)
            if response.status_code == 200:
                data = response.json()
                if "games" in data:
                    all_games.extend(data["games"])
            time.sleep(1)  # Uniknięcie blokady API
    return all_games

def save_games_to_pgn(games, filename):
    """ Zapisuje partie w formacie PGN. """
    with open(filename, "w", encoding="utf-8") as f:
        for game in games:
            if "pgn" in game:
                f.write(game["pgn"] + "\n\n")

def main():
    for player, (start_year, end_year) in players.items():
        username = usernames.get(player)
        if username:
            print(f"Pobieranie partii dla {player} ({start_year}-{end_year})...")
            games = fetch_games(username, start_year, end_year)
            if games:
                filename = f"{player.replace(' ', '_')}.pgn"
                save_games_to_pgn(games, filename)
                print(f"Zapisano {len(games)} partii dla {player} w {filename}")
            else:
                print(f"Brak dostępnych partii dla {player}")
        else:
            print(f"Brak konta Chess.com dla {player}, pominięto.")

if __name__ == "__main__":
    main()
