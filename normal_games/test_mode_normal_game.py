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
            y1 = int(input("Wprowadź rząd figury, którą chcesz przesunąć: "))
            x1 = int(input("Wprowadź kolumnę figury, którą chcesz przesunąć: "))
            y2 = int(input("Wprowadź rząd, na który chcesz przesunąć figurę: "))
            x2 = int(input("Wprowadź kolumnę, na którą chcesz przesunąć figurę: "))
            moving = not tryMove(turn, main_board, y1, x1, y2, x2)
        print(afterMove(turn, main_board, y1, x1, y2, x2))
        print(board_to_fen(main_board.board_state))
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