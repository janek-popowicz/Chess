"""
Moduł zawiera klasy reprezentujące figury szachowe.

Każda figura posiada swoje unikalne właściwości, takie jak typ, kolor, schemat ruchu oraz dodatkowe atrybuty (np. możliwość wykonania roszady lub bicia w przelocie).
"""

class Pawn():
    """
    Klasa reprezentująca pionka.
    """
    def __init__(self, color):
        """
        Inicjalizuje pionka.

        Args:
            color (str): Kolor pionka ('w' dla białych, 'b' dla czarnych).
        """
        self.type = 'p'
        self.color = color
        self.has_moved = False
        self.can_enpassant = 0 # Zmienna can_enpassant przechowuje kierunek możliwego enpassant na osi x dla danego pionka, 0 oznacza brak takiej możliwości
        if color == 'w': 
            self.move_scheme = [(0, 1, 1)]
            self.attack_scheme = [(1, 1, 1), (-1, 1, 1)]
        if color == 'b':
            self.move_scheme = [(0, -1, 1)]
            self.attack_scheme = [(-1, -1, 1), (1, -1, 1)]

    def return_figure(self):
        """
        Zwraca reprezentację pionka jako ciąg znaków.

        Returns:
            str: Reprezentacja pionka (np. "wp" dla białego pionka).
        """
        return (self.color + self.type)

    def print_figure(self):
        """
        Wyświetla reprezentację pionka w terminalu.
        """
        print(self.color + self.type, end="")


class Rook():
    """
    Klasa reprezentująca wieżę.
    """
    def __init__(self, color):
        """
        Inicjalizuje wieżę.

        Args:
            color (str): Kolor wieży ('w' dla białych, 'b' dla czarnych).
        """
        self.has_moved = False  
        self.type = 'R'
        self.color = color
        self.move_scheme = [(0, 1, 8), (0, -1, 8), (1, 0, 8), (-1, 0, 8)]

    def return_figure(self):
        """
        Zwraca reprezentację wieży jako ciąg znaków.

        Returns:
            str: Reprezentacja wieży (np. "wR" dla białej wieży).
        """
        return (self.color + self.type)

    def print_figure(self):
        """
        Wyświetla reprezentację wieży w terminalu.
        """
        print(self.color + self.type, end="")


class Knight():
    """
    Klasa reprezentująca skoczka.
    """
    def __init__(self, color):
        """
        Inicjalizuje skoczka.

        Args:
            color (str): Kolor skoczka ('w' dla białych, 'b' dla czarnych).
        """
        self.type = 'N'
        self.color = color
        self.move_scheme = [(2, 1, 1), (-2, 1, 1), (2, -1, 1), (-2, -1, 1), (1, 2, 1), (1, -2, 1), (-1, 2, 1), (-1, -2, 1)]

    def return_figure(self):
        """
        Zwraca reprezentację skoczka jako ciąg znaków.

        Returns:
            str: Reprezentacja skoczka (np. "wN" dla białego skoczka).
        """
        return (self.color + self.type)

    def print_figure(self):
        """
        Wyświetla reprezentację skoczka w terminalu.
        """
        print(self.color + self.type, end="")


class Bishop():
    """
    Klasa reprezentująca gońca.
    """
    def __init__(self, color):
        """
        Inicjalizuje gońca.

        Args:
            color (str): Kolor gońca ('w' dla białych, 'b' dla czarnych).
        """
        self.type = 'B'
        self.color = color
        self.move_scheme = [(1, 1, 8), (1, -1, 8), (-1, 1, 8), (-1, -1, 8)]

    def return_figure(self):
        """
        Zwraca reprezentację gońca jako ciąg znaków.

        Returns:
            str: Reprezentacja gońca (np. "wB" dla białego gońca).
        """
        return (self.color + self.type)

    def print_figure(self):
        """
        Wyświetla reprezentację gońca w terminalu.
        """
        print(self.color + self.type, end="")


class Queen():
    """
    Klasa reprezentująca królową.
    """
    def __init__(self, color):
        """
        Inicjalizuje królową.

        Args:
            color (str): Kolor królowej ('w' dla białych, 'b' dla czarnych).
        """
        self.type = 'Q'
        self.color = color
        self.move_scheme = [(1, 1, 8), (1, -1, 8), (-1, 1, 8), (-1, -1, 8), (0, 1, 8), (0, -1, 8), (1, 0, 8), (-1, 0, 8)]

    def return_figure(self):
        """
        Zwraca reprezentację królowej jako ciąg znaków.

        Returns:
            str: Reprezentacja królowej (np. "wQ" dla białej królowej).
        """
        return (self.color + self.type)

    def print_figure(self):
        """
        Wyświetla reprezentację królowej w terminalu.
        """
        print(self.color + self.type, end="")


class King():
    """
    Klasa reprezentująca króla.
    """
    def __init__(self, color):
        """
        Inicjalizuje króla.

        Args:
            color (str): Kolor króla ('w' dla białych, 'b' dla czarnych).
        """
        self.has_moved = False
        self.type = 'K'
        self.color = color
        self.move_scheme = [(1, 1, 1), (1, -1, 1), (-1, 1, 1), (-1, -1, 1), (0, 1, 1), (0, -1, 1), (1, 0, 1), (-1, 0, 1)]

    def return_figure(self):
        """
        Zwraca reprezentację króla jako ciąg znaków.

        Returns:
            str: Reprezentacja króla (np. "wK" dla białego króla).
        """
        return (self.color + self.type)

    def print_figure(self):
        """
        Wyświetla reprezentację króla w terminalu.
        """
        print(self.color + self.type, end="")