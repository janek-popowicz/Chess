"""
This is gonna be chess game. Here are gonna be classes for figures and board."""
import figures
class Board:
    board = [
        [figures.Rook("black"), figures.Knight("black"), figures.Bishop("black"), figures.Queen("black"), figures.King("black"), figures.Bishop("black"), figures.Knight("black"), figures.Rook("black")],
        [figures.Pawn("black") for i in range(8)],
        [None for i in range(8)],
        [None for i in range(8)],
        [None for i in range(8)],
        [None for i in range(8)],
        [figures.Pawn("white") for i in range(8)],
        [figures.Rook("white"), figures.Knight("white"), figures.Bishop("white"), figures.Queen("white"), figures.King("white"), figures.Bishop("white"), figures.Knight("white"), figures.Rook("white")]
    ]

    def checkIfMoveIsPossible(self, figure, x, y):
        return figure.checkIfMoveIsPossible(x, y)


class Field:
    def __init__(self, x, y, figure=None):
        self.x = x
        self.y = y
        self.figure = None

    def set_figure(self, figure):
        self.figure = figure

    def what_figure(self):
        return self.figure

    def remove_figure(self):
        self.figure = None