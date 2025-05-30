"""
Moduł zawiera klasy reprezentujące pola i planszę szachową.
"""
import engine.figures as figures
import engine.fen_operations as fen_operations
import copy
class Field:
    """
    Klasa reprezentująca pojedyncze pole na planszy szachowej.
    """
    def __init__(self, x: int, y: int, figure=None):
        """
        Inicjalizuje pole na planszy.

        Args:
            x (int): Współrzędna kolumny pola.
            y (int): Współrzędna wiersza pola.
            figure (Figure, opcjonalnie): Figura znajdująca się na polu (domyślnie None).
        """
        self.x = x
        self.y = y
        self.figure = figure

    def remove_figure(self) -> None:
        """
        Usuwa figurę z pola.

        Returns:
            None: Funkcja nie zwraca wartości.
        """
        self.figure = None


class Board:
    """
    Klasa reprezentująca planszę szachową.
    """
    def __init__(self, board_state=None):
        """
        Inicjalizuje planszę szachową z domyślnym ustawieniem figur.

        Args:
            board_state (list, opcjonalnie): Stan planszy jako lista pól (domyślnie ustawienie początkowe).
        """
        if board_state is None:
            board_state = [
                [Field(0, 0, figures.Rook('w')), Field(1, 0, figures.Knight('w')), Field(2, 0, figures.Bishop('w')), Field(3, 0, figures.King('w')), Field(4, 0, figures.Queen('w')), Field(5, 0, figures.Bishop('w')), Field(6, 0, figures.Knight('w')), Field(7, 0, figures.Rook('w'))],
                [Field(0, 1, figures.Pawn('w')), Field(1, 1, figures.Pawn('w')), Field(2, 1, figures.Pawn('w')), Field(3, 1, figures.Pawn('w')), Field(4, 1, figures.Pawn('w')), Field(5, 1, figures.Pawn('w')), Field(6, 1, figures.Pawn('w')), Field(7, 1, figures.Pawn('w'))],
                [Field(0, 2), Field(1, 2), Field(2, 2), Field(3, 2), Field(4, 2), Field(5, 2), Field(6, 2), Field(7, 2)],
                [Field(0, 3), Field(1, 3), Field(2, 3), Field(3, 3), Field(4, 3), Field(5, 3), Field(6, 3), Field(7, 3)],
                [Field(0, 4), Field(1, 4), Field(2, 4), Field(3, 4), Field(4, 4), Field(5, 4), Field(6, 4), Field(7, 4)],
                [Field(0, 5), Field(1, 5), Field(2, 5), Field(3, 5), Field(4, 5), Field(5, 5), Field(6, 5), Field(7, 5)],
                [Field(0, 6, figures.Pawn('b')), Field(1, 6, figures.Pawn('b')), Field(2, 6, figures.Pawn('b')), Field(3, 6, figures.Pawn('b')), Field(4, 6, figures.Pawn('b')), Field(5, 6, figures.Pawn('b')), Field(6, 6, figures.Pawn('b')), Field(7, 6, figures.Pawn('b'))],
                [Field(0, 7, figures.Rook('b')), Field(1, 7, figures.Knight('b')), Field(2, 7, figures.Bishop('b')), Field(3, 7, figures.King('b')), Field(4, 7, figures.Queen('b')), Field(5, 7, figures.Bishop('b')), Field(6, 7, figures.Knight('b')), Field(7, 7, figures.Rook('b'))]
            ]
        self.board_state = board_state
        self.incheck = False
        self.moves_numeric = []
        self.moves_algebraic = []
        self.moves_algebraic_long = []
        self.halfmove_clock = 0
        self.fen_history = [fen_operations.board_to_fen_inverted(self,"w")]
        self.piece_cords = []
        for row in range(0,8):
            for col in range(0,8):
                if self.board_state[row][col].figure:
                    self.piece_cords.append((row, col))

    def make_move(self, y1: int, x1: int, y2: int, x2: int) -> None:
        """
        Wykonuje ruch na planszy.

        Args:
            y1 (int): Współrzędna wiersza początkowego.
            x1 (int): Współrzędna kolumny początkowej.
            y2 (int): Współrzędna wiersza docelowego.
            x2 (int): Współrzędna kolumny docelowej.

        Returns:
            None: Funkcja nie zwraca wartości.

        Raises:
            ValueError: Jeśli współrzędne są poza zakresem planszy.
        """
        if not (0 <= y1 < 8 and 0 <= x1 < 8 and 0 <= y2 < 8 and 0 <= x2 < 8):
            raise ValueError("Współrzędne muszą być w zakresie od 0 do 7.")
        self.board_state[y2][x2].figure = self.board_state[y1][x1].figure
        self.board_state[y1][x1].figure = None
        
    def get_regular_moves(self, field: Field) -> list[tuple[int, int]]:
        """
        Generuje możliwe ruchy dla figury na danym polu (bez uwzględnienia ataków).

        Args:
            field (Field): Pole, dla którego generowane są ruchy.

        Returns:
            list[tuple[int, int]]: Lista możliwych współrzędnych ruchów.
        """
        if not isinstance(field, Field):
            return []
        possible_cords = [] 
        if field.figure == None:
            print("Na tym polu nie ma figury!",end=" ")
            return []
        movescheme =copy.deepcopy(field.figure.move_scheme)
        if field.figure.type == 'p':
            if field.figure.has_moved == False:
                if field.figure.color == 'w':
                    movescheme.append((0,1,2))
                else:
                    movescheme.append((0,-1,2))            
        for direction in movescheme:
            for distance in range(1,direction[2]+1):
                field_to_check_x = field.x + direction[0] * distance
                field_to_check_y= field.y + direction[1] * distance
                #Sprawdzanie, czy koordynaty pola nie wyszły poza szachownicę
                if field_to_check_x not in range(0,8) or field_to_check_y not in range(0,8):
                    break
                field_to_check = self.board_state[field_to_check_y][field_to_check_x]
                #Sprawdzanie, czy na danym polu jest jakaś figura
                if field_to_check.figure:
                    break    
                possible_cords.append((field_to_check.y,field_to_check.x))

        return possible_cords   

    def get_attack_moves(self, field: Field) -> list[tuple[int, int]]:
        """
        Generuje możliwe ruchy ataku dla figury na danym polu.

        Args:
            field (Field): Pole, dla którego generowane są ruchy ataku.

        Returns:
            list[tuple[int, int]]: Lista możliwych współrzędnych ataków.
        """
        if not isinstance(field, Field):
            return []
        possible_cords = [] 
        try:
            attackscheme = field.figure.attack_scheme 
        except AttributeError:
            attackscheme = field.figure.move_scheme
        for direction in attackscheme:
            for distance in range(1,direction[2]+1):
                field_to_check_x = field.x + direction[0] * distance
                field_to_check_y= field.y + direction[1] * distance
                #Sprawdzanie, czy koordynaty pola nie wyszły poza szachownicę
                if field_to_check_y > 7 or field_to_check_y < 0 or field_to_check_x > 7 or field_to_check_x < 0:
                    break 
                field_to_check = self.board_state[field_to_check_y][field_to_check_x]
                #Uwzględnienie enpassant
                if field.figure.type == 'p':
                        if field.figure.can_enpassant:
                                possible_cords.append(((field.y+direction[1],field.x + field.figure.can_enpassant)))
                #Sprawdzanie, czy na polu do zbicia jest król
                if field_to_check.figure: 
                    if field_to_check.figure.color != field.figure.color:
                            possible_cords.append((field_to_check.y,field_to_check.x)) 
                    break
        return possible_cords

    def is_attacked(self, field: Field, color: str = None) -> bool:
        """
        Sprawdza, czy dane pole jest atakowane przez przeciwnika.

        Args:
            field (Field): Pole do sprawdzenia.
            color (str, opcjonalnie): Kolor gracza, który atakuje (domyślnie przeciwnik).

        Returns:
            bool: True, jeśli pole jest atakowane, False w przeciwnym razie.
        """
        if not isinstance(field, Field) or (color not in {'w', 'b', None}):
            return False
        if color==None:
            color = field.figure.color
        attackschemes = {
            'N':[(2,1,1),(-2,1,1),(2,-1,1),(-2,-1,1),(1,2,1),(1,-2,1),(-1,2,1),(-1,-2,1)],
            'B':[(1,1,8),(1,-1,8),(-1,1,8),(-1,-1,8),],
            'R':[(0, 1 ,8), (0, -1 ,8), (1, 0 ,8), (-1, 0 ,8)],
            'Q':[(1,1,8),(1,-1,8),(-1,1,8),(-1,-1,8),(0, 1 ,8), (0, -1 ,8), (1, 0 ,8), (-1, 0 ,8)],
            'K':[(1,1,1),(1,-1,1),(-1,1,1),(-1,-1,1),(0, 1 ,1), (0, -1 ,1), (1, 0 ,1), (-1, 0 ,1)],
        }
        if color == 'w':
            attackschemes['p'] = [(-1, 1, 1),(1, 1, 1)]
        else:
            attackschemes['p'] = [(-1, -1, 1),(1, -1, 1)]
        for figure_type in attackschemes:
            attackscheme = attackschemes[figure_type]
            for direction in attackscheme:
                for distance in range(1,direction[2]+1):
                    field_to_check_x = field.x + direction[0] * distance
                    field_to_check_y= field.y + direction[1] * distance
                    #Sprawdzanie, czy koordynaty pola nie wyszły poza szachownicę
                    if field_to_check_y > 7 or field_to_check_y < 0 or field_to_check_x > 7 or field_to_check_x < 0:
                        break 
                    field_to_check = self.board_state[field_to_check_y][field_to_check_x]
                    if field_to_check.figure:
                        if field_to_check.figure.color == color:
                            break
                        else:
                            if field_to_check.figure.type == figure_type:
                                return True
                            break
        return False

    def is_in_check(self, color: str) -> None:
        """
        Sprawdza, czy król danego koloru jest szachowany.

        Args:
            color (str): Kolor króla do sprawdzenia ('w' lub 'b').

        Returns:
            None: Funkcja nie zwraca wartości.
        """
        if color not in {'w', 'b'}:
            return
        for cord in self.piece_cords:
            tile = self.board_state[cord[0]][cord[1]]
            if tile.figure.type == 'K' and tile.figure.color == color:
                    king_position = tile
        if self.is_attacked(king_position):
            if self.incheck == False:
                self.incheck = True
        else:
            self.incheck = False  
    def is_in_check_minimax(self, color: str) -> bool:
        """
        Sprawdza, czy król danego koloru jest szachowany (wersja do minimaxu).

        Args:
            color (str): Kolor króla do sprawdzenia ('w' lub 'b').

        Returns:
            bool: True, jeśli król jest szachowany, False w przeciwnym razie.
        """
        for i in range(8):
            for j in range(8):
                tile = self.board_state[i][j]
                if tile.figure and tile.figure.type == 'K' and tile.figure.color == color:
                    king_position = tile
        return self.is_attacked(king_position)
    def get_all_moves(self, turn: str) -> dict[tuple[int, int], list[tuple[int, int]]]:
        """
        Generuje wszystkie możliwe ruchy dla danego koloru.

        Args:
            turn (str): Aktualna tura ('w' lub 'b').

        Returns:
            dict[tuple[int, int], list[tuple[int, int]]]: Słownik z możliwymi ruchami.
        """
        if turn not in {'w', 'b'}:
            return {}
        all_moves = {}
        for i in range(len(self.piece_cords)):
                cord = self.piece_cords[i]
                field = self.board_state[cord[0]][cord[1]]
                # self.print_board()
                if field.figure.color == turn:
                        all_moves[(cord[0],cord[1])] = self.get_legal_moves(field,turn)
                self.piece_cords.sort() 
        return {k: v for k, v in all_moves.items() if v}
    def get_legal_moves(self, field: Field, turn: str) -> list[tuple[int, int]]:
        """
        Generuje legalne ruchy dla figury na danym polu.

        Args:
            field (Field): Pole figury, dla której generowane są ruchy.
            turn (str): Aktualna tura ('w' lub 'b').

        Returns:
            list[tuple[int, int]]: Lista legalnych ruchów.
        """
        if not isinstance(field, Field) or turn not in {'w', 'b'}:
            return []
        if field.figure == None:
            print("Na tym polu nie ma figury!",end=" ")
            return []
        elif field.figure.color != turn:
            print("To nie twój ruch!", end=" ")
            return []
        else:
            possible_moves = set(self.get_regular_moves(field) + self.get_attack_moves(field))
            legal_cords = []
            for move in possible_moves:
                        figure1 = self.board_state[field.y][field.x].figure
                        figure2 = self.board_state[move[0]][move[1]].figure
                        if figure2:
                            if figure2.type == 'K':
                                self.incheck = True
                                continue
                        self.piece_cords.remove((field.y,field.x))
                        self.piece_cords.append((move[0],move[1]))
                        self.make_move(field.y,field.x,move[0],move[1])
                        self.is_in_check(turn)
                        if not self.incheck:
                            legal_cords.append(move)
                        self.board_state[field.y][field.x].figure = figure1
                        self.board_state[move[0]][move[1]].figure = figure2
                        self.piece_cords.remove((move[0],move[1]))
                        self.piece_cords.append((field.y,field.x))
            # Sprawdzanie roszady
            if field.figure.type == "K":
                self.is_in_check(turn)
                if not self.incheck:
                    j =-1
                    for x_to_check in [0,7]:
                        if self.board_state[field.y][x_to_check].figure:
                            if self.board_state[field.y][x_to_check].figure.type == 'R' and self.board_state[field.y][x_to_check].figure.color == field.figure.color:
                                if field.figure.has_moved == False and self.board_state[field.y][x_to_check].figure.has_moved == False:
                                    space_free = True
                                    tile_to_check_y = field.y
                                    for i in range(1,(field.x - x_to_check)*(-j)):
                                        tile_to_check_x = field.x + i * j
                                        if self.board_state[tile_to_check_y][tile_to_check_x].figure or self.is_attacked(self.board_state[tile_to_check_y][tile_to_check_x],turn):
                                            space_free = False
                                    if space_free:
                                        legal_cords.append((field.y,x_to_check))
                        j = 1 
            return legal_cords
        
    def print_board(self) -> None:
        """
        Wyświetla aktualny stan planszy w terminalu.

        Returns:
            None: Funkcja nie zwraca wartości.
        """
        print("+" + "----+" *8 )
        for x in range(7,-1,-1):
            print( "| ",end="")
            for y in range(7,-1,-1):
                if self.board_state[x][y].figure == None:
                    print("  ",end="")
                else:
                    self.board_state[x][y].figure.print_figure()
                print(" | ",end="")
            print(x)
            print("+" + "----+" *8 )
        print("  7    6    5    4    3    2    1    0")

    def get_piece(self, row: int, col: int) -> str:
        """
        Zwraca figurę znajdującą się na danym polu.

        Args:
            row (int): Wiersz pola.
            col (int): Kolumna pola.

        Returns:
            str: Reprezentacja figury lub "--", jeśli pole jest puste.
        """
        if not (0 <= row < 8 and 0 <= col < 8):
            return "--"
        if self.board_state[row][col].figure == None:
            return "--"
        else:
            return self.board_state[row][col].figure.return_figure()
