

"""
color: 'w' or 'b'
"""

class Pawn():
    def __init__(self, color):
        self.type = 'p'
        self.color = color
        self.first_move = True
        self.move_scheme = [(0, 1, 2)]
    def print_figure(self):
        print(self.color + self.type,end="")
class Rook():
    def __init__(self, color):
        self.type = 'R'
        self.color = color
        self.move_scheme = [(0, 1 ,8), (0, -1 ,8), (1, 0 ,8), (-1, 0 ,8)]
    def print_figure(self):
        print(self.color + self.type,end="")
class Knight():
    def __init__(self, color):
        self.type = 'N'
        self.color = color
        self.move_scheme = [(2,3,1),(-2,3,1),(2,-3,1),(-2,-3,1),(3,2,1),(3,-2,1),(-3,2,1),(-3,-2,1)]
    def print_figure(self):
        print(self.color + self.type,end="")
class Bishop():
    def __init__(self, color):
        self.type = 'B'
        self.color = color
        self.move_scheme = [(1,1,8),(1,-1,8),(-1,1,8),(-1,-1,8),]
    def print_figure(self):
        print(self.color + self.type,end="")
class Queen():
    def __init__(self, color):
        self.type = 'Q'
        self.color = color
        self.move_scheme =[(1,1,8),(1,-1,8),(-1,1,8),(-1,-1,8),(0, 1 ,8), (0, -1 ,8), (1, 0 ,8), (-1, 0 ,8)]
    def print_figure(self):
        print(self.color + self.type,end="")
class King():
    def __init__(self, color):
        self.type = 'K'
        self.color = color
        self.move_scheme = [(1,1,1),(1,-1,1),(-1,1,1),(-1,-1,1),(0, 1 ,1), (0, -1 ,1), (1, 0 ,1), (-1, 0 ,1)]
    def print_figure(self):
        print(self.color + self.type,end="")