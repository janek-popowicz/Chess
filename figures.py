
'''
color: 'w' or 'b'
'''
class Pawn():
    def __init__(self, color):
        self.color = color
        self.first_move = True
    def print_figure(self):
        print(color + 'p')
class Rook():
    def __init__(self, color):
        self.color = color
        self
    def print_figure(self):
        print(color + 'R')
class Knight():
    def __init__(self, color):
        self.color = color
    def print_figure(self):
        print(color + 'N')
class Bishop():
    def __init__(self, color):
        self.color = color
    def print_figure(self):
        print(color + 'B')
class Queen():
    def __init__(self, color):
        self.color = color
    def print_figure(self):
        print(color + 'Q')
class King():
    def __init__(self, color):
        self.color = color
    def print_figure(self):
        print(color + 'K')