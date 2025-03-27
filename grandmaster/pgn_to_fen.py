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

import re

import re

import tkinter as tk
from tkinter import filedialog
import pygame

def parse_pgn(pgn_text, grandmaster_name_fragment):
    # Podział na gry na podstawie wyników (0-1, 1-0, 1/2-1/2)
    games = re.split(r'(?:1-0|0-1|1/2-1/2)', pgn_text.replace("\n", " ").strip())

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
        
        # Pobranie nazw graczy
        white_player = headers.get("White", "")
        black_player = headers.get("Black", "")
        
        # Pobranie ELO
        white_elo_str = headers.get("WhiteElo", "0")
        black_elo_str = headers.get("BlackElo", "0")
        
        white_elo = int(white_elo_str) if white_elo_str.isdigit() else 0
        black_elo = int(black_elo_str) if black_elo_str.isdigit() else 0
        
        # Ustalenie, kto jest arcymistrzem
        if grandmaster_name_fragment.lower() in white_player.lower():
            last_grandmaster_color = "w"
        elif grandmaster_name_fragment.lower() in black_player.lower():
            last_grandmaster_color = "b"
        elif white_player or black_player:
            # Jeśli nie znaleziono arcymistrza, ale jest drugi gracz, to on NIE jest arcymistrzem
            if white_player: 
                last_grandmaster_color = "b"
            elif black_player:
                last_grandmaster_color = "w"
        elif white_elo or black_elo:
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

def main():
    # Initialize pygame for the dialog
    pygame.init()
    screen = pygame.display.set_mode((1260, 960))
    pygame.display.set_caption("PGN to FEN Converter")

    # Show file dialog
    from graphics import choose_pgn_file_dialog
    grandmaster = choose_pgn_file_dialog(screen, 100)
    
    if not grandmaster:  # User cancelled or error occurred
        pygame.quit()
        return

    # Process the PGN file
    pgn_path = Path(f"grandmaster/pgn/{grandmaster}.pgn")
    try:
        with open(pgn_path, "r") as pgn_file:
            pgn_data = pgn_file.read()
    except FileNotFoundError:
        print(f"Error: File {pgn_path} not found")
        pygame.quit()
        return

    # Process games from PGN file
    games = parse_pgn(pgn_data, grandmaster)

    # Dictionary to store FENs and grandmaster moves
    fen_moves = {}
    
    for game in games:
        grandmaster_color = game['grandmaster']
        moves = game['moves']
        main_board = board_and_fields.Board()
        turn = 'w'  # Biały zawsze zaczyna
        y1, x1, y2, x2 = 0, 0, 0, 0

        for i in range(len(moves)):
            current_move = moves[i]    
            # Zapisujemy FEN i ruch tylko gdy jest ruch arcymistrza
            if (turn == grandmaster_color):
                # Pobierz aktualny FEN (bez liczników ruchów)
                current_fen = board_to_fen_inverted(main_board, turn)
                fen_parts = current_fen.split(' ')
                good_fen = f"{fen_parts[0]}"
                
                
            
            # Wykonaj ruch na planszy
            try:
                print(f"Ruch: {current_move}")
                cords = engine.notation_to_cords(main_board, current_move, turn)
                y1, x1, y2, x2 = cords
                if tryMove(turn, main_board, y1, x1, y2, x2):
                    if turn == grandmaster_color:
                        # Dodaj ruch do listy ruchów dla danego FENa
                        if good_fen in fen_moves:
                            if current_move not in fen_moves[good_fen]:
                                fen_moves[good_fen].append(current_move)
                        else:
                            fen_moves[good_fen] = [current_move]
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
                break
            
            if whatAfter in ["checkmate", "stalemate"]:
                break
                    
            # except (ValueError, IndexError) as e:
            #     print(f"Błąd podczas wykonywania ruchu: {e}")
            
            
    
    # Zapisz wyniki do pliku JSON
    json_path = Path(f"grandmaster/json/{grandmaster}.json")
    with open(json_path, "w") as json_file:
        json.dump(fen_moves, json_file, indent=2)


if __name__ == "__main__":
    main()