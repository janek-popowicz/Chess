"""
    BEZ SENSU
"""

import os

PIECE_SYMBOLS = {
    'K': 'K', 'Q': 'Q', 'R': 'R', 'B': 'B', 'N': 'N', 'P': 'P',
    'k': 'k', 'q': 'q', 'r': 'r', 'b': 'b', 'n': 'n', 'p': 'p'
}

def parse_pgn(pgn_file):
    with open(pgn_file, "r") as file:
        lines = file.readlines()
    
    moves = []
    for line in lines:
        if line.startswith("1."):
            moves.extend(line.strip().split())
    
    moves = [move for move in moves if not move[0].isdigit()]
    return moves

def apply_move(board, move):
    # Implementacja uproszczonego ruchu na szachownicy
    # To jest uproszczona wersja, która nie obsługuje wszystkich reguł szachowych
    # Należy zaimplementować pełną logikę ruchów szachowych
    pass

def board_to_fen(board):
    fen = ""
    for row in board:
        empty_count = 0
        for cell in row:
            if cell == ".":
                empty_count += 1
            else:
                if empty_count > 0:
                    fen += str(empty_count)
                    empty_count = 0
                fen += cell
        if empty_count > 0:
            fen += str(empty_count)
        fen += "/"
    fen = fen[:-1]  # Remove the trailing slash
    fen += " w - - 0 1"  # Add default FEN suffix
    return fen

def pgn_to_fen(pgn_file):
    moves = parse_pgn(pgn_file)
    board = [
        ["r", "n", "b", "q", "k", "b", "n", "r"],
        ["p", "p", "p", "p", "p", "p", "p", "p"],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        ["P", "P", "P", "P", "P", "P", "P", "P"],
        ["R", "N", "B", "Q", "K", "B", "N", "R"]
    ]
    fens = [board_to_fen(board)]
    
    for move in moves:
        apply_move(board, move)
        fens.append(board_to_fen(board))
    
    return fens

def save_fens(fens, output_file):
    with open(output_file, "w") as file:
        for fen in fens:
            file.write(fen + "\n")

def main():
    pgn_file = "/home/janek/Projects/Chess/grandmaster/kasparov_all_games.pgn"  # Zmień na ścieżkę do swojego pliku PGN
    output_file_white = "arcymistrz_białe.fen"
    output_file_black = "arcymistrz_czarne.fen"
    
    fens = pgn_to_fen(pgn_file)
    
    fens_white = fens[::2]  # FENy dla białych
    fens_black = fens[1::2]  # FENy dla czarnych
    
    save_fens(fens_white, output_file_white)
    save_fens(fens_black, output_file_black)

if __name__ == "__main__":
    main()