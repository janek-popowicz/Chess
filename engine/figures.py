"""
This module contains classes representing chess pieces.

Each piece has unique properties such as type, color, movement scheme, 
and additional attributes (e.g., castling rights or en passant capability).
"""

class Pawn:
    """
    Represents a pawn in chess.
    """
    def __init__(self, color):
        """
        Initializes a pawn.

        Args:
            color (str): The color of the pawn ('w' for white, 'b' for black).
        """
        self.type = 'p'
        self.color = color
        self.has_moved = False
        self.can_enpassant = 0  # Direction of possible en passant on the x-axis; 0 means no en passant possible.
        if color == 'w': 
            self.move_scheme = [(0, 1, 1)]
            self.attack_scheme = [(1, 1, 1), (-1, 1, 1)]
        elif color == 'b':
            self.move_scheme = [(0, -1, 1)]
            self.attack_scheme = [(-1, -1, 1), (1, -1, 1)]

    def return_figure(self):
        """
        Returns the string representation of the pawn.

        Returns:
            str: Representation of the pawn (e.g., "wp" for a white pawn).
        """
        return self.color + self.type

    def print_figure(self):
        """
        Prints the string representation of the pawn to the terminal.
        """
        print(self.color + self.type, end="")


class Rook:
    """
    Represents a rook in chess.
    """
    def __init__(self, color):
        """
        Initializes a rook.

        Args:
            color (str): The color of the rook ('w' for white, 'b' for black).
        """
        self.has_moved = False  
        self.type = 'R'
        self.color = color
        self.move_scheme = [(0, 1, 8), (0, -1, 8), (1, 0, 8), (-1, 0, 8)]

    def return_figure(self):
        """
        Returns the string representation of the rook.

        Returns:
            str: Representation of the rook (e.g., "wR" for a white rook).
        """
        return self.color + self.type

    def print_figure(self):
        """
        Prints the string representation of the rook to the terminal.
        """
        print(self.color + self.type, end="")


class Knight:
    """
    Represents a knight in chess.
    """
    def __init__(self, color):
        """
        Initializes a knight.

        Args:
            color (str): The color of the knight ('w' for white, 'b' for black).
        """
        self.type = 'N'
        self.color = color
        self.move_scheme = [
            (2, 1, 1), (-2, 1, 1), (2, -1, 1), (-2, -1, 1),
            (1, 2, 1), (1, -2, 1), (-1, 2, 1), (-1, -2, 1)
        ]

    def return_figure(self):
        """
        Returns the string representation of the knight.

        Returns:
            str: Representation of the knight (e.g., "wN" for a white knight).
        """
        return self.color + self.type

    def print_figure(self):
        """
        Prints the string representation of the knight to the terminal.
        """
        print(self.color + self.type, end="")


class Bishop:
    """
    Represents a bishop in chess.
    """
    def __init__(self, color):
        """
        Initializes a bishop.

        Args:
            color (str): The color of the bishop ('w' for white, 'b' for black).
        """
        self.type = 'B'
        self.color = color
        self.move_scheme = [(1, 1, 8), (1, -1, 8), (-1, 1, 8), (-1, -1, 8)]

    def return_figure(self):
        """
        Returns the string representation of the bishop.

        Returns:
            str: Representation of the bishop (e.g., "wB" for a white bishop).
        """
        return self.color + self.type

    def print_figure(self):
        """
        Prints the string representation of the bishop to the terminal.
        """
        print(self.color + self.type, end="")


class Queen:
    """
    Represents a queen in chess.
    """
    def __init__(self, color):
        """
        Initializes a queen.

        Args:
            color (str): The color of the queen ('w' for white, 'b' for black).
        """
        self.type = 'Q'
        self.color = color
        self.move_scheme = [
            (1, 1, 8), (1, -1, 8), (-1, 1, 8), (-1, -1, 8),
            (0, 1, 8), (0, -1, 8), (1, 0, 8), (-1, 0, 8)
        ]

    def return_figure(self):
        """
        Returns the string representation of the queen.

        Returns:
            str: Representation of the queen (e.g., "wQ" for a white queen).
        """
        return self.color + self.type

    def print_figure(self):
        """
        Prints the string representation of the queen to the terminal.
        """
        print(self.color + self.type, end="")


class King:
    """
    Represents a king in chess.
    """
    def __init__(self, color):
        """
        Initializes a king.

        Args:
            color (str): The color of the king ('w' for white, 'b' for black).
        """
        self.has_moved = False
        self.type = 'K'
        self.color = color
        self.move_scheme = [
            (1, 1, 1), (1, -1, 1), (-1, 1, 1), (-1, -1, 1),
            (0, 1, 1), (0, -1, 1), (1, 0, 1), (-1, 0, 1)
        ]

    def return_figure(self):
        """
        Returns the string representation of the king.

        Returns:
            str: Representation of the king (e.g., "wK" for a white king).
        """
        return self.color + self.type

    def print_figure(self):
        """
        Prints the string representation of the king to the terminal.
        """
        print(self.color + self.type, end="")