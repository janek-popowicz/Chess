"""
This is gonna be chess game. Here are gonna be classes for figures and board."""
import figures
class Board:
    board = [[Field(0, 0, figures.Rook('b')), Field(1, 0, figures.Knight('b')), Field(2, 0, figures.Bishop('b')), Field(3, 0, figures.Queen('b')), Field(4, 0, figures.King('b')), Field(5, 0, figures.Bishop('b')), Field(6, 0, figures.Knight('b')), Field(7, 0, figures.Rook('b'))],
             [Field(0, 1, figures.Pawn('b')), Field(1, 1, figures.Pawn('b')), Field(2, 1, figures.Pawn('b')), Field(3, 1, figures.Pawn('b')), Field(4, 1, figures.Pawn('b')), Field(5, 1, figures.Pawn('b')), Field(6, 1, figures.Pawn('b')), Field(7, 1, figures.Pawn('b'))],
             [Field(0, 2), Field(1, 2), Field(2, 2), Field(3, 2), Field(4, 2), Field(5, 2), Field(6, 2), Field(7, 2)],
             [Field(0, 3), Field(1, 3), Field(2, 3), Field(3, 3), Field(4, 3), Field(5, 3), Field(6, 3), Field(7, 3)],
             [Field(0, 4), Field(1, 4), Field(2, 4), Field(3, 4), Field(4, 4), Field(5, 4), Field(6, 4), Field(7, 4)],
             [Field(0, 5), Field(1, 5), Field(2, 5), Field(3, 5), Field(4, 5), Field(5, 5), Field(6, 5), Field(7, 5)],
             [Field(0, 6, figures.Pawn('w')), Field(1, 6, figures.Pawn('w')), Field(2, 6, figures.Pawn('w')), Field(3, 6, figures.Pawn('w')), Field(4, 6, figures.Pawn('w')), Field(5, 6, figures.Pawn('w')), Field(6, 6, figures.Pawn('w')), Field(7, 6, figures.Pawn('w'))],
             [Field(0, 7, figures.Rook('w')), Field(1, 7, figures.Knight('w')), Field(2, 7, figures.Bishop('w')), Field(3, 7, figures.Queen('w')), Field(4, 7, figures.King('w')), Field(5, 7, figures.Bishop('w')), Field(6, 7, figures.Knight('w')), Field(7, 7, figures.Rook('w'))]
    ]

    def makeMove(self, x1, y1, x2, y2):
        self.board[y2][x2].figure = self.board[y1][x1].figure
        self.board[y1][x1].figure = None
class Field:
    def __init__(self, x, y, figure=None):
        self.x = x
        self.y = y
        self.figure = None

    

    def what_figure(self):
        return self.figure

    def remove_figure(self):
        self.figure = None