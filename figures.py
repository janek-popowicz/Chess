

"""
color: 'w' or 'b'
"""

class Pawn():
    def __init__(self, color):
        self.color = color
        self.first_move = True
    def print_figure(self):
        print(self.color + 'p',end="")
        return None
class Rook():
    def __init__(self, color):
        self.color = color
    def print_figure(self):
        print(self.color + 'R',end="")
        return None
class Knight():
    def __init__(self, color):
        self.color = color
    def print_figure(self):
        print(self.color + 'N',end="")
        return None
class Bishop():
    def __init__(self, color):
        self.color = color
    def print_figure(self):
        print(self.color + 'B',end="")
        return None
class Queen():
    def __init__(self, color):
        self.color = color
    def print_figure(self):
        print(self.color + 'Q',end="")
        return None
class King():
    def __init__(self, color):
        self.color = color
    def print_figure(self):
        print(self.color + 'K',end="")
        return None