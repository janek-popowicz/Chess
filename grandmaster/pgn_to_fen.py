import re
import engine.engine as engine
def parse_pgn(pgn_text):
    games = pgn_text.strip().split("\n\n")  # Podział na gry
    extracted_games = []
    
    for game in games:
        headers = {}
        moves = []
        
        split_result = re.split(r'\n\d+\.', game, maxsplit=1)
        if len(split_result) < 2:
            continue  # Pomijamy, jeśli nie ma części z ruchami
        
        header_lines, move_section = split_result
        
        for line in header_lines.split("\n"):
            match = re.match(r'\[(\w+)\s+"([^"]+)"\]', line)
            if match:
                headers[match[1]] = match[2]
        
        # Określenie, kto jest arcymistrzem
        white_elo = int(headers.get("WhiteElo", 0))
        black_elo = int(headers.get("BlackElo", 0))
        grandmaster_color = "White" if white_elo > black_elo else "Black"
        
        # Pobranie ruchów w oryginalnym formacie
        moves = re.findall(r'\d+\.\s*([^\s]+)\s*([^\s]+)?', move_section)
        move_list = [move for pair in moves for move in pair if move]
        
    
    return grandmaster_color, move_list

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

1.c4 c6 2.d4 d5 3.Nf3 Nf6 4.e3 a6 5.Qc2 Bg4 6.Ne5 Bh5 7.Qb3 Qc7
8.cxd5 cxd5 9.Nc3 e6 10.Bd2 Bd6 11.Rc1 Nc6 12.Na4 O-O 13.Nxc6
bxc6 14.Qb6 Qe7 15.Bd3 Bg6 16.Bxg6 fxg6 17.f3 Ne4 18.fxe4 Qh4+
19.g3 Qxe4 20.Ke2 Qg2+ 21.Kd3 Rf2 22.Qa5 Rb8 23.a3 Bc7 24.Qxc7
Rxd2+ 25.Kc3 Rdxb2 0-1
"""

color, list = parse_pgn(pgn_data)


import sys
import os

#wygląda dziwnie ale musi działać
from engine.board_and_fields import *
from engine.engine import *
from engine.figures import *
from algorithms import evaluation
from engine.fen_operations import *

def main():
    running = True
    main_board = board_and_fields.Board()
    turn = 'b'
    while running:
        turn = 'w' if turn == 'b' else 'b'
        main_board.print_board()
        main_board.is_in_check(turn)
        if main_board.incheck:
            print("Szach!", end=" ")
        moving = True
        while moving:
            print(evaluation.Evaluation(main_board).ocena_materiału())
            try:
                cords=engine.notation_to_cords(main_board, input("ruch: "), turn)
                y1,x1,y2,x2 = cords
                moving = not tryMove(turn, main_board, y1, x1, y2, x2)
            except ValueError:
                print("Niepoprawny ruch, ",cords)
            # except IndexError:
            #     print("Brak notacji")
        print(afterMove(turn, main_board, y1, x1, y2, x2))
        print(board_to_fen(main_board.board_state))
        print(main_board.moves_algebraic)
        whatAfter, yForPromotion, xForPromotion = afterMove(turn, main_board, y1, x1, y2, x2)
        if whatAfter == "promotion":
            main_board.print_board()
            choiceOfPromotion = input(f"""Pionek w kolumnie {xForPromotion} dotarł do końca planszy. Wpisz:
    1 - Aby zmienić go w Skoczka
    2 - Aby zmienić go w Gońca
    3 - Aby zmienić go w Wieżę
    4 - Aby zmienić go w Królową
                    """)
            promotion(turn, yForPromotion, xForPromotion, main_board, choiceOfPromotion)
        if whatAfter == "checkmate":
            print("Szach Mat!")
            break
        elif whatAfter == "stalemate":
            print("Pat")
            break
        else:
            continue
    return
if __name__ == "__main__":
    main()