"""
This is gonna be chess game. Here are gonna be classes for figures and board."""

class Board:






class Figure:
    def __init__(self, color):
        self.color = color
        self.position = None

    def move(self, new_position):
        self.position = new_position

    def __str__(self):
        return f'{self.color} {self.__class__.__name__}'