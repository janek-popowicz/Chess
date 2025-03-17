import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'engine')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'board')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'figures')))

import engine.engine as engine
import engine.board_and_fields as board_and_fields
import engine.figures as figures

def rotate_pst(white_pst):
   #obraca szachownice o 180 stopni zeby anazlizowac ją również dla czarnych      
    return white_pst[::-1]

# PST dla białych (wartości przeskalowane – oryginalne liczby dzielone przez 100)
PAWN_W_PST = [
    [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
    [0.05, 0.10, 0.10, -0.20, -0.20, 0.10, 0.10, 0.05],
    [0.05, -0.05, -0.10, 0.0,   0.0,  -0.10, -0.05, 0.05],
    [0.0,  0.0,  0.0,  0.20,  0.20,  0.0,   0.0,  0.0],
    [0.05, 0.05, 0.10, 0.25,  0.25,  0.10,  0.05, 0.05],
    [0.10, 0.10, 0.20, 0.30,  0.30,  0.20,  0.10, 0.10],
    [0.50, 0.50, 0.50, 0.50,  0.50,  0.50,  0.50, 0.50],
    [0.0,  0.0,  0.0,  0.0,   0.0,   0.0,   0.0,  0.0]
]

KNIGHT_W_PST = [
    [-0.50, -0.40, -0.30, -0.30, -0.30, -0.30, -0.40, -0.50],
    [-0.40, -0.20,  0.00,  0.05,  0.05,  0.00, -0.20, -0.40],
    [-0.30,  0.05,  0.10,  0.15,  0.15,  0.10,  0.05, -0.30],
    [-0.30,  0.00,  0.15,  0.20,  0.20,  0.15,  0.00, -0.30],
    [-0.30,  0.05,  0.15,  0.20,  0.20,  0.15,  0.05, -0.30],
    [-0.30,  0.00,  0.10,  0.15,  0.15,  0.10,  0.00, -0.30],
    [-0.40, -0.20,  0.00,  0.00,  0.00,  0.00, -0.20, -0.40],
    [-0.50, -0.40, -0.30, -0.30, -0.30, -0.30, -0.40, -0.50]
]

BISHOP_W_PST = [
    [-0.20, -0.10, -0.10, -0.10, -0.10, -0.10, -0.10, -0.20],
    [-0.10,  0.05,  0.00,  0.00,  0.00,  0.00,  0.05, -0.10],
    [-0.10,  0.10,  0.10,  0.10,  0.10,  0.10,  0.10, -0.10],
    [-0.10,  0.00,  0.10,  0.10,  0.10,  0.10,  0.00, -0.10],
    [-0.10,  0.05,  0.05,  0.10,  0.10,  0.05,  0.05, -0.10],
    [-0.10,  0.00,  0.05,  0.10,  0.10,  0.05,  0.00, -0.10],
    [-0.10,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.10],
    [-0.20, -0.10, -0.10, -0.10, -0.10, -0.10, -0.10, -0.20]
]

ROOK_W_PST = [
    [ 0.00,  0.00,  0.05,  0.10,  0.10,  0.05,  0.00,  0.00],
    [-0.05,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.05],
    [-0.05,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.05],
    [-0.05,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.05],
    [-0.05,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.05],
    [-0.05,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.05],
    [ 0.05,  0.10,  0.10,  0.10,  0.10,  0.10,  0.10,  0.05],
    [ 0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00]
]

QUEEN_W_PST = [
    [-0.20, -0.10, -0.10, -0.05, -0.05, -0.10, -0.10, -0.20],
    [-0.10,  0.00,  0.05,  0.00,  0.00,  0.00,  0.00, -0.10],
    [-0.10,  0.05,  0.05,  0.05,  0.05,  0.05,  0.00, -0.10],
    [ 0.00,  0.00,  0.05,  0.05,  0.05,  0.05,  0.00, -0.05],
    [-0.05,  0.00,  0.05,  0.05,  0.05,  0.05,  0.00, -0.05],
    [-0.10,  0.00,  0.05,  0.05,  0.05,  0.05,  0.00, -0.10],
    [-0.10,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.10],
    [-0.20, -0.10, -0.10, -0.05, -0.05, -0.10, -0.10, -0.20]
]

KING_W_PST = [
    [ 0.20,  0.30,  0.10,  0.00,  0.00,  0.10,  0.30,  0.20],
    [ 0.20,  0.20,  0.00,  0.00,  0.00,  0.00,  0.20,  0.20],
    [-0.10, -0.20, -0.20, -0.20, -0.20, -0.20, -0.20, -0.10],
    [-0.20, -0.30, -0.30, -0.40, -0.40, -0.30, -0.30, -0.20],
    [-0.30, -0.40, -0.40, -0.50, -0.50, -0.40, -0.40, -0.30],
    [-0.30, -0.40, -0.40, -0.50, -0.50, -0.40, -0.40, -0.30],
    [-0.30, -0.40, -0.40, -0.50, -0.50, -0.40, -0.40, -0.30],
    [-0.30, -0.40, -0.40, -0.50, -0.50, -0.40, -0.40, -0.30]
]

# Generujemy PST dla czarnych przez obrócenie tablic białych:
PAWN_B_PST   = rotate_pst(PAWN_W_PST)
KNIGHT_B_PST = rotate_pst(KNIGHT_W_PST)
BISHOP_B_PST = rotate_pst(BISHOP_W_PST)
ROOK_B_PST   = rotate_pst(ROOK_W_PST)
QUEEN_B_PST  = rotate_pst(QUEEN_W_PST)
KING_B_PST   = rotate_pst(KING_W_PST)

class Evaluation:
    def __init__(self, main_board):
        self.main_board = main_board
        self.waga_czarnych = 0
        self.waga_białych = 0
        self.bonus_białych = 0
        self.bonus_czarnych = 0
        self.figures_values = {
            'p': 1,
            'N': 3,
            'B': 3,
            'R': 5,
            'Q': 9,
            'K': 1000
        }

    def ocena_materiału(self): 
        for i in range(8):
            for j in range(8):
                field = self.main_board.board_state[i][j]
                if field.figure is None:
                    continue  # Skip if the field does not have a piece
                
                figure = field.figure.return_figure()
                #print(figure)
                
                if len(figure) < 2:
                    continue  # Skip if the figure representation is invalid
                
                piece_type = figure[1]
                piece_color = figure[0]
                
                if piece_color == 'w':
                    self.waga_białych += self.figures_values.get(piece_type, 0)
                else:
                    self.waga_czarnych += self.figures_values.get(piece_type, 0)

        #print(f"Final weights - White: {self.waga_białych}, Black: {self.waga_czarnych}")  # Debugging print statement
        return [self.waga_białych, self.waga_czarnych]
    
    def bonus_squares(self):
        for i in range(8):
            for j in range(8):
                piece  = self.main_board.board_state[i][j]
                if piece.figure is None:
                    continue
                    
                color = piece.figure.color
                piece_type = piece.figure.type
                #powiino być że czarne to jest to odgóry mimo to że graja tam białe np
                if color == 'w':
                    if piece_type == 'p':
                        self.bonus_białych += PAWN_W_PST[i][j]
                    elif piece_type == 'N':
                        self.bonus_białych += KNIGHT_W_PST[i][j]
                    elif piece_type == 'B':
                        self.bonus_białych += BISHOP_W_PST[i][j]
                    elif piece_type == 'R':
                        self.bonus_białych += ROOK_W_PST[i][j]
                    elif piece_type == 'Q':
                        self.bonus_białych += QUEEN_W_PST[i][j]
                    elif piece_type == 'K':
                        self.bonus_białych += KING_W_PST[i][j]
                elif color == 'b':
                    if piece_type == 'p':
                        self.bonus_czarnych += PAWN_B_PST[i][j]
                    elif piece_type == 'N':
                        self.bonus_czarnych += KNIGHT_B_PST[i][j]
                    elif piece_type == 'B':
                        self.bonus_czarnych += BISHOP_B_PST[i][j]
                    elif piece_type == 'R':
                        self.bonus_czarnych += ROOK_B_PST[i][j]
                    elif piece_type == 'Q':
                        self.bonus_czarnych += QUEEN_B_PST[i][j]
                    elif piece_type == 'K':
                        self.bonus_czarnych += KING_B_PST[i][j]
        #print(f"Final bonus - White: {self.bonus_białych}, Black: {self.bonus_czarnych}")  # Debugging print statement
        return [self.bonus_białych, self.bonus_czarnych]
    def count_pieces(self): #niezależne od koloru AI)
        white_pieces = 0
        black_pieces = 0
        for i in range(8):
            for j in range(8):
                field = self.main_board.board_state[i][j]
                if field.figure is None:
                    continue
                else:
                    if field.figure.color == 'w':
                        white_pieces += 1
                    else:
                        black_pieces += 1
        return white_pieces+black_pieces
    def king_to_edge(self):
        
        eval_white = 0
        eval_black = 0
        white_king_position = []
        black_king_position = []
        for i in range(8):
            for j in range(8):
                piece = self.main_board.board_state[i][j]
                if piece.figure is not None and piece.figure.type == 'K':
                    if piece.figure.color == 'w':
                        white_king_position = [i, j]
                    else:
                        black_king_position = [i, j]

        if white_king_position is not None:
            kingw_kolumna = white_king_position[0]
            kingw_wiersz = white_king_position[1]
            kingw_to_edge = min(kingw_kolumna, 7-kingw_kolumna) + min(kingw_wiersz, 7-kingw_wiersz)
    def get_evaluation(self):
        material = self.ocena_materiału()
        bonus = self.bonus_squares()
        return [material[0] + bonus[0], material[1] + bonus[1]]

