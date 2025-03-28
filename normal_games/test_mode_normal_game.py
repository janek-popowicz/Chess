import sys
import os
import time

#wygląda dziwnie ale musi działać
from engine.board_and_fields import *
from engine.engine import *
from engine.figures import *
from algorithms.evaluation import *
from engine.fen_operations import *

def main():
    running = True
    main_board = board_and_fields.Board()
    print(main_board.piece_cords)
    turn = 'b'
    start_time = time.time()
    white_time = 0
    black_time = 0

    while running:
        turn = 'w' if turn == 'b' else 'b'
        main_board.print_board()
        main_board.is_in_check(turn)
        if main_board.incheck:
            print("Szach!", end=" ")
        moving = True
        while moving:
            print(get_evaluation(main_board))
            y1 = int(input("Wprowadź rząd figury, którą chcesz przesunąć: "))
            x1 = int(input("Wprowadź kolumnę figury, którą chcesz przesunąć: "))
            y2 = int(input("Wprowadź rząd, na który chcesz przesunąć figurę: "))
            x2 = int(input("Wprowadź kolumnę, na którą chcesz przesunąć figurę: "))
            moving = not tryMove(turn, main_board, y1, x1, y2, x2)
        print(main_board.moves_algebraic)
        print(board_to_fen(main_board.board_state))
        print(afterMove(turn, main_board, y1, x1, y2, x2))
        print(main_board.piece_cords)
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
            # Aktualizacja czasu gracza na żywo
            current_time = time.time()
            if turn == 'w':
                current_white_time = max(0, 10 * 60 - (current_time - start_time + white_time))  # Odliczanie od 10 minut
                current_black_time = max(0, 10 * 60 - black_time)  # Zachowaj czas czarnego
            else:
                current_black_time = max(0, 10 * 60 - (current_time - start_time + black_time))  # Odliczanie od 10 minut
                current_white_time = max(0, 10 * 60 - white_time)  # Zachowaj czas białego

            # Sprawdzenie, czy czas się skończył
            if current_white_time <= 0 or current_black_time <= 0:
                running = False
                result = "Czas się skończył!"
                winner = "Czarny" if current_white_time <= 0 else "Biały"
                print(result)
                print(f"Zwycięzca: {winner}")
                break
            continue
    return
if __name__ == "__main__":
    main()