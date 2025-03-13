import board_and_fields
import figures
import engine

PAWN_W_PST = [
    # Ranga 1 (indeks 0) – dolny rząd, białe pole startowe (choć pionki nie występują na ranga 1)
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    # Ranga 2 (indeks 1) – miejsce startowe białych pionków, bonus = 0
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    # Ranga 3 (indeks 2)
    [0.05, 0.10, 0.10, 0.10, 0.10, 0.10, 0.10, 0.05],
    # Ranga 4 (indeks 3)
    [0.10, 0.15, 0.20, 0.20, 0.20, 0.20, 0.15, 0.10],
    # Ranga 5 (indeks 4) – maksymalny bonus, do 0.35 na centralnych polach
    [0.15, 0.20, 0.30, 0.35, 0.35, 0.30, 0.20, 0.15],
    # Ranga 6 (indeks 5)
    [0.10, 0.15, 0.25, 0.30, 0.30, 0.25, 0.15, 0.10],
    # Ranga 7 (indeks 6)
    [0.05, 0.10, 0.15, 0.20, 0.20, 0.15, 0.10, 0.05],
    # Ranga 8 (indeks 7) – góra, pion do promocji, bonus = 0
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
]

KNIGHT_W_PST = [
    [-0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5],
    [-0.4, -0.2, 0, 0.05, 0.05, 0, -0.2, -0.4],
    [-0.3, 0.05, 0.1, 0.15, 0.15, 0.1, 0.05, -0.3],
    [-0.3, 0, 0.15, 0.2, 0.2, 0.15, 0, -0.3],
    [-0.3, 0.05, 0.15, 0.2, 0.2, 0.15, 0.05, -0.3],
    [-0.3, 0, 0.1, 0.15, 0.15, 0.1, 0, -0.3],
    [-0.4, -0.2, 0, 0, 0, 0, -0.2, -0.4],
    [-0.5, -0.4, -0.3, -0.3, -0.3, -0.3, -0.4, -0.5]
]

BISHOP_W_PST = [
    [-0.2, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.2],
    [-0.1, 0.05, 0, 0, 0, 0, 0.05, -0.1],
    [-0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, -0.1],
    [-0.1, 0, 0.1, 0.1, 0.1, 0.1, 0, -0.1],
    [-0.1, 0.05, 0.05, 0.1, 0.1, 0.05, 0.05, -0.1],
    [-0.1, 0, 0.05, 0.1, 0.1, 0.05, 0, -0.1],
    [-0.1, 0, 0, 0, 0, 0, 0, -0.1],
    [-0.2, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.2]
]

ROOK_W_PST = [
    [0, 0, 0.05, 0.1, 0.1, 0.05, 0, 0],
    [-0.05, 0, 0, 0, 0, 0, 0, -0.05],
    [-0.05, 0, 0, 0, 0, 0, 0, -0.05],
    [-0.05, 0, 0, 0, 0, 0, 0, -0.05],
    [-0.05, 0, 0, 0, 0, 0, 0, -0.05],
    [-0.05, 0, 0, 0, 0, 0, 0, -0.05],
    [0.05, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

QUEEN_W_PST = [
    [-0.2, -0.1, -0.1, -0.05, -0.05, -0.1, -0.1, -0.2],
    [-0.1, 0, 0.05, 0, 0, 0, 0, -0.1],
    [-0.1, 0.05, 0.05, 0.05, 0.05, 0.05, 0, -0.1],
    [0, 0, 0.05, 0.05, 0.05, 0.05, 0, -0.05],
    [-0.05, 0, 0.05, 0.05, 0.05, 0.05, 0, -0.05],
    [-0.1, 0, 0.05, 0.05, 0.05, 0.05, 0, -0.1],
    [-0.1, 0, 0, 0, 0, 0, 0, -0.1],
    [-0.2, -0.1, -0.1, -0.05, -0.05, -0.1, -0.1, -0.2]
]

KING_B = [
    [0.2, 0.3, 0.1, 0, 0, 0.1, 0.3, 0.2],
    [0.2, 0.2, 0, 0, 0, 0, 0.2, 0.2],
    [-0.1, -0.2, -0.2, -0.2, -0.2, -0.2, -0.2, -0.1],
    [-0.2, -0.3, -0.3, -0.4, -0.4, -0.3, -0.3, -0.2],
    [-0.3, -0.4, -0.4, -0.5, -0.5, -0.4, -0.4, -0.3],
    [-0.3, -0.4, -0.4, -0.5, -0.5, -0.4, -0.4, -0.3],
    [-0.3, -0.4, -0.4, -0.5, -0.5, -0.4, -0.4, -0.3],
    [-0.3, -0.4, -0.4, -0.5, -0.5, -0.4, -0.4, -0.3]
]

class Evaluation:
    def __init__(self, main_board):
        self.main_board = main_board
        self.waga_czarnych = 0
        self.waga_białych = 0
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

        print(f"Final weights - White: {self.waga_białych}, Black: {self.waga_czarnych}")  # Debugging print statement
        return [self.waga_białych, self.waga_czarnych]

