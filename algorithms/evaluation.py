import sys 
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'engine')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'board')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'figures')))

import engine.engine as engine
import engine.board_and_fields as board_and_fields
import engine.figures as figures

player_color = "white"
def rotate_pst(white_pst):
   #obraca szachownice o 180 stopni zeby anazlizowac ją również dla czarnych      
    return white_pst[::-1]

# PST dla białych (wartości przeskalowane – oryginalne liczby dzielone przez 100)
PAWN_DOWN = [
    [0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0,  0.0],
    [0.2, 0.20, 0.20, 0.20, 0.20, 0.20, 0.20, 0.20],
    [0.5, -0.05, -0.10, 0.0,   0.0,  -0.10, -0.05, 0.05],
    [0.10,  0.10,  0.10,  0.20,  0.20,  0.10,   0.1,  0.10],
    [0.1, 0.1, 0.10, 0.25,  0.25,  0.10,  0.1, 0.1],
    [0.10, 0.10, 0.20, 0.30,  0.30,  0.20,  0.10, 0.10],
    [0.2, 0.25, 0.25, 0.15,  0.15,  0.25,  0.25, 0.2],
    [0.0,  0.0,  0.0,  0.0,   0.0,   0.0,   0.0,  0.0]
] 

KNIGHT = [
    [-0.50, -0.40, -0.30, -0.30, -0.30, -0.30, -0.40, -0.50],
    [-0.40, -0.20,  0.00,  0.05,  0.05,  0.00, -0.20, -0.40],
    [-0.30,  0.05,  0.10,  0.15,  0.15,  0.10,  0.05, -0.30],
    [-0.30,  0.00,  0.15,  0.20,  0.20,  0.15,  0.00, -0.30],
    [-0.30,  0.05,  0.15,  0.20,  0.20,  0.15,  0.05, -0.30],
    [-0.30,  0.00,  0.10,  0.15,  0.15,  0.10,  0.00, -0.30],
    [-0.40, -0.20,  0.00,  0.00,  0.00,  0.00, -0.20, -0.40],
    [-0.50, -0.40, -0.30, -0.30, -0.30, -0.30, -0.40, -0.50]
]

BISHOP = [ #mnożnik razy 3 
    [-0.20, -0.10, -0.10, -0.10, -0.10, -0.10, -0.10, -0.20],
    [-0.10,  0.05,  0.00,  0.00,  0.00,  0.00,  0.05, -0.10],
    [-0.10,  0.10,  0.10,  0.10,  0.10,  0.10,  0.10, -0.10],
    [-0.10,  0.00,  0.10,  0.10,  0.10,  0.10,  0.00, -0.10],
    [-0.10,  0.05,  0.05,  0.10,  0.10,  0.05,  0.05, -0.10],
    [-0.10,  0.00,  0.05,  0.10,  0.10,  0.05,  0.00, -0.10],
    [-0.10,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.10],
    [-0.20, -0.10, -0.10, -0.10, -0.10, -0.10, -0.10, -0.20]
]

ROOK = [ #mnożnik razy 4
    [ 0.00,  0.00,  0.05,  0.10,  0.10,  0.05,  0.00,  0.00],
    [-0.05,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.05],
    [-0.05,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.05],
    [-0.05,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.05],
    [-0.05,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.05],
    [-0.05,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.05],
    [ 0.05,  0.10,  0.10,  0.10,  0.10,  0.10,  0.10,  0.05],
    [ 0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00]
]

QUEEN = [ #mnożnik razyy 10
    [-0.20, -0.10, -0.10, -0.05, -0.05, -0.10, -0.10, -0.20],
    [-0.10,  0.00,  0.05,  0.00,  0.00,  0.00,  0.00, -0.10],
    [-0.10,  0.05,  0.05,  0.05,  0.05,  0.05,  0.00, -0.10],
    [ 0.00,  0.00,  0.05,  0.05,  0.05,  0.05,  0.00, -0.05],
    [-0.05,  0.00,  0.05,  0.05,  0.05,  0.05,  0.00, -0.05],
    [-0.10,  0.00,  0.05,  0.05,  0.05,  0.05,  0.00, -0.10],
    [-0.10,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.10],
    [-0.20, -0.10, -0.10, -0.05, -0.05, -0.10, -0.10, -0.20]
]

KING_UP = [ #razy 20 
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
PAWN_UP = rotate_pst(PAWN_DOWN)
KING_DOWN = rotate_pst(KING_UP)

class Evaluation:
    def __init__(self, main_board):
        self.main_board = main_board
        self.palyer_color = player_color
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
            'K': 0
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
    
    def bonus_squares(self): #dla białych
        for i in range(8):
            for j in range(8):
                piece  = self.main_board.board_state[i][j]
                if piece.figure is None:
                    continue
                    
                color = piece.figure.color
                piece_type = piece.figure.type
                
                if player_color == 'white':
                    if color == 'w':
                        if piece_type == 'p':
                            self.bonus_białych += PAWN_DOWN[i][j]
                        elif piece_type == 'N':
                            self.bonus_białych += KNIGHT[i][j]
                        elif piece_type == 'B':
                            self.bonus_białych += (BISHOP[i][j] * 3)
                        elif piece_type == 'R':
                            self.bonus_białych += ROOK[i][j] * 4
                        elif piece_type == 'Q':
                            self.bonus_białych += QUEEN[i][j] * 10
                        elif piece_type == 'K':
                            self.bonus_białych += KING_DOWN[i][j] * 20
                    else:
                        if color == 'b':
                            if piece_type == 'p':
                                self.bonus_czarnych += PAWN_UP[i][j]
                            elif piece_type == 'N':
                                self.bonus_czarnych += KNIGHT[i][j] 
                            elif piece_type == 'B':
                                self.bonus_czarnych += BISHOP[i][j] * 3
                            elif piece_type == 'R':
                                self.bonus_czarnych += ROOK[i][j] * 4
                            elif piece_type == 'Q':
                                self.bonus_czarnych += QUEEN[i][j] * 10
                            elif piece_type == 'K':
                                self.bonus_czarnych += KING_UP[i][j] * 20
                else:
                    if color == 'b':
                        if piece_type == 'p':
                            self.bonus_białych += PAWN_DOWN[i][j]
                        elif piece_type == 'N':
                            self.bonus_białych += KNIGHT[i][j]
                        elif piece_type == 'B':
                            self.bonus_białych += BISHOP[i][j] * 3
                        elif piece_type == 'R': 
                            self.bonus_białych += ROOK[i][j] * 4
                        elif piece_type == 'Q':
                            self.bonus_białych += QUEEN[i][j] * 10
                        elif piece_type == 'K':
                            self.bonus_białych += KING_DOWN[i][j] * 20
                    else:
                        if color == 'w':
                            if piece_type == 'p':
                                self.bonus_czarnych += PAWN_UP[i][j]
                            elif piece_type == 'N':
                                self.bonus_czarnych += KNIGHT[i][j]
                            elif piece_type == 'B':
                                self.bonus_czarnych += BISHOP[i][j] * 3
                            elif piece_type == 'R':
                                self.bonus_czarnych += ROOK[i][j] * 4
                            elif piece_type == 'Q':
                                self.bonus_czarnych += QUEEN[i][j] * 10
                            elif piece_type == 'K':
                                self.bonus_czarnych += KING_UP[i][j] * 20
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
    def king_to_edge(board):

        evaluation_white = 0
        evaluation_black = 0

        # Znajdź pozycję króla białego i czarnego
        white_king_position = None
        black_king_position = None
        for i in range(8):
            for j in range(8):
                piece = board.board_state[i][j]
                if piece.figure is not None and piece.figure.type == 'K':
                    if piece.figure.color == 'w':
                        white_king_position = (i, j)
                    else:
                        black_king_position = (i, j)

        if white_king_position is not None:
            white_king_rank, white_king_file = white_king_position
            # Oblicz dystans króla białego od krawędzi
            white_king_dst_to_edge = min(white_king_rank, 7 - white_king_rank) + min(white_king_file, 7 - white_king_file)
            evaluation_black += white_king_dst_to_edge

        if black_king_position is not None:
            black_king_rank, black_king_file = black_king_position
            # Oblicz dystans króla czarnego od krawędzi
            black_king_dst_to_edge = min(black_king_rank, 7 - black_king_rank) + min(black_king_file, 7 - black_king_file)
            evaluation_white += black_king_dst_to_edge
        return [evaluation_white, evaluation_black]
        #return ale z wagą ze to zacyna barsziej działac kiedy jest mniej pozycji 
    def get_evaluation(self):
        material = self.ocena_materiału()
        bonus = self.bonus_squares()
        king_bonus = self.king_to_edge(self.main_board)

        wasd = 1
        wasd += (32 - self.count_pieces()) / 100
        wasd *=2
        king_bonus_white = king_bonus[0] * wasd
        king_bonus_black = king_bonus[1] * wasd

        #zakładanie wag tyko do king_bonus  waga 1.(32 - pieces)  

        #białe , czarne
        return [material[0] + bonus[0] + king_bonus_white, material[1] + bonus[1] + king_bonus_black]

