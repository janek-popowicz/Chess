import engine.engine as engine
import json
import re
from pathlib import Path

import sys
import os
import re

#wygląda dziwnie ale musi działać
from engine.board_and_fields import *
from engine.engine import *
from engine.figures import *
from algorithms import evaluation
from engine.fen_operations import *

def parse_pgn(pgn_text):
    games = re.split(r'(?m)^1\.', pgn_text.strip())  # Podział na gry tylko gdy "1." jest na początku linii
    extracted_games = []
    last_grandmaster_color = None
    
    for game in games:
        headers = {}
        moves = []
        
        # Usuń zawartość nawiasów {} (np. {[%clk 0:02:58]})
        game = re.sub(r'\{.*?\}', '', game)
        
        # Pobranie nagłówków PGN
        header_lines = re.findall(r'\[(\w+) "([^"]+)"\]', game)
        for key, value in header_lines:
            headers[key] = value
        
        # Określenie, kto jest arcymistrzem, jeśli dostępne
        white_elo = int(headers.get("WhiteElo", 0))
        black_elo = int(headers.get("BlackElo", 0))
        if white_elo or black_elo:
            last_grandmaster_color = "w" if white_elo > black_elo else "b"
        
        # Usunięcie nagłówków
        game = re.sub(r'\[.*?\]', '', game).strip()
        
        # Pobranie ruchów w oryginalnym formacie
        move_list = re.findall(r'\d+\.\s*([^\s]+)\s*([^\s]+)?', game)
        moves = [move for pair in move_list for move in pair if move]
        
        extracted_games.append({
            "grandmaster": last_grandmaster_color,
            "moves": moves
        })
    
    return extracted_games

# Przykładowe użycie
pgn_data = """[Event "Match (active)"]
[Site "Creta (Greece)"]
[Date "2003.??.??"]
[Round "2"]
[White "Azmaiparashvili Zurab (GEO)"]
[Black "Kasparov Garry (RUS)"]
[Result "0-1"]
[ECO "D11"]
[WhiteElo "2672"]
[BlackElo "2813"]
[Annotator ""]
[Source ""]
[Remark "IX"]

1.c4 c6 2.d4 d5 3.Nf3 Nf6 4.e3 a6 5.Qc2 Bg4 6.Ne5 Bh5 7.Qb3 Qc7
8.cxd5 cxd5 9.Nc3 e6 10.Bd2 Bd6 11.Rc1 Nc6 12.Na4 O-O 13.Nxc6
bxc6 14.Qb6 Qe7 15.Bd3 Bg6 16.Bxg6 fxg6 17.f3 Ne4 18.fxe4 Qh4+
19.g3 Qxe4 20.Ke2 Qg2+ 21.Kd3 Rf2 22.Qa5 Rb8 23.a3 Bc7 24.Qxc7
Rxd2+ 25.Kc3 Rdxb2 0-1
[Event "Match (blitz)"]
[ECO "A07"]
1.Nf3 d5 2.g3 Bg4 3.Bg2 Nd7 4.O-O c6 5.Nc3 e5 6.e4 d4 7.Ne2 g5
8.d3 h6 9.Nd2 Bd6 10.c3 c5 11.Nc4 Bc7 12.a4 Ne7 13.Bd2 Nc6 14.cxd4
Nxd4 15.f3 Be6 16.Rc1 Nxe2+ 17.Qxe2 Qe7 18.Ne3 O-O-O 19.Nd5 Bxd5
20.exd5 Kb8 21.f4 gxf4 22.gxf4 Bd6 23.Bc3 Rhg8 24.Kh1 Rde8 25.Rce1
Qh4 26.Qe4 Nf6 27.Qf3 exf4 28.Bd2 Nh5 29.Qh3 Qxh3 30.Bxh3 Rxe1
31.Rxe1 Nf6 32.Bg2 Ng4 33.Rf1 Ne3 34.Bxe3 fxe3 35.Bf3 f5 36.Rg1
Re8 37.Kg2 Rg8+ 38.Kf1 Rxg1+ 39.Kxg1 Kc7 40.Kg2 Kb6 41.Bd1 Ka5
42.Kf3 Bxh2 43.Kxe3 Kb4 44.Bc2 Be5 45.b3 h5 46.Kf3 Kc3 47.d4
cxd4 48.Bxf5 d3 49.Bg6 h4 50.Bh5 h3 51.Kf2 h2 52.Kg2 Kd4 0-1"""
result = parse_pgn(pgn_data)
for game in result:
    print(f"Arcymistrz grał kolorem: {game['grandmaster']}")
    print("Ruchy:", game["moves"])



def main():
    # Wczytanie pliku PGN
    pgn_path = Path("grandmaster/games.pgn")
    with open(pgn_path, "r") as pgn_file:
        pgn_data = pgn_file.read()

    # Przetworzenie gier z pliku PGN
    games = parse_pgn(pgn_data)
    
    # Słownik do przechowywania FENów i ruchów arcymistrza
    fen_moves = {}
    
    for game in games:
        grandmaster_color = game['grandmaster']
        moves = game['moves']
        main_board = board_and_fields.Board()
        turn = 'w'  # Biały zawsze zaczyna
        
        for i in range(len(moves)):
            current_move = moves[i]
            
            # Zapisujemy FEN i ruch tylko gdy jest ruch arcymistrza
            if (turn == grandmaster_color):
                # Pobierz aktualny FEN (bez liczników ruchów)
                current_fen = board_to_fen_inverted(main_board, turn, y1, x1, y2, x2)
                fen_parts = current_fen.split(' ')
                position_fen = f"{fen_parts[0]} {fen_parts[1]} {fen_parts[2]} {fen_parts[3]}"
                
                # Dodaj ruch do listy ruchów dla danego FENa
                if position_fen in fen_moves:
                    if current_move not in fen_moves[position_fen]:
                        fen_moves[position_fen].append(current_move)
                else:
                    fen_moves[position_fen] = [current_move]
            
            # Wykonaj ruch na planszy
            try:
                print(f"Ruch: {current_move}")
                cords = engine.notation_to_cords(main_board, current_move, turn)
                y1, x1, y2, x2 = cords
                if tryMove(turn, main_board, y1, x1, y2, x2):
                    turn = 'b' if turn == 'w' else 'w'
                    whatAfter, yForPromotion, xForPromotion = afterMove(turn, main_board, y1, x1, y2, x2)
                    if whatAfter == "promotion":
                        choiceOfPromotion = current_move[-1]
                        promotion_letter_to_number = {
                            "Q": "4", "R": "3", "B": "2", "N": "1"
                        }
                        promotion(turn, yForPromotion, xForPromotion, main_board, 
                                promotion_letter_to_number[choiceOfPromotion])
            except:
                pass
            
            if whatAfter in ["checkmate", "stalemate"]:
                break
                    
            # except (ValueError, IndexError) as e:
            #     print(f"Błąd podczas wykonywania ruchu: {e}")
            
            
    
    # Zapisz wyniki do pliku JSON
    json_path = Path("grandmaster/grandmaster_moves.json")
    with open(json_path, "w") as json_file:
        json.dump(fen_moves, json_file, indent=2)


if __name__ == "__main__":
    main()