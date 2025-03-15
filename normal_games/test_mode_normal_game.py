import sys
import os

# Dodajemy ścieżki do sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'engine')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'board')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'algorithms')))

import engine
import board_and_fields
import evaluation

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
            y1 = input("Wprowadź rząd figury, którą chcesz przesunąć: ")
            x1 = input("Wprowadź kolumnę figury, którą chcesz przesunąć: ")
            y2 = input("Wprowadź rząd, na który chcesz przesunąć figurę: ")
            x2 = input("Wprowadź kolumnę, na którą chcesz przesunąć figurę: ")
            y1 = int(y1)
            x1 = int(x1)
            y2 = int(y2)
            x2 = int(x2)
            moving = not engine.tryMove(turn, main_board, y1, x1, y2, x2)
        print(engine.afterMove(turn, main_board, y1, x1, y2, x2))
        whatAfter, yForPromotion, xForPromotion = engine.afterMove(turn, main_board, y1, x1, y2, x2)
        if whatAfter == "promotion":
            main_board.print_board()
            choiceOfPromotion = input(f"""Pionek w kolumnie {xForPromotion} dotarł do końca planszy. Wpisz:
    1 - Aby zmienić go w Skoczka
    2 - Aby zmienić go w Gońca
    3 - Aby zmienić go w Wieżę
    4 - Aby zmienić go w Królową
                    """)
            engine.promotion(turn, yForPromotion, xForPromotion, main_board, choiceOfPromotion)
        if whatAfter == "checkmate":
            print("Szach Mat!")
            break
        elif whatAfter == "stalemate":
            print("Pat")
            break
        else:
            continue

if __name__ == "__main__":
    main()