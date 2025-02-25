"""
This is gonna be chess game. Here are gonna be classes for figures and board."""

class Board:
    board = []



class Field:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.figure = None

    def set_figure(self, figure):
        self.figure = figure

    def what_figure(self):
        return self.figure

    def remove_figure(self):
        self.figure = None