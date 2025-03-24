import engine.figures as figures
import engine.board_and_fields as board_and_fields
def fen_to_board_state(fen:str)->list:
    """Z fena zwraca listę obiektów. Należy zastosować tak:

board_state = fen_to_board_state(fen)
main_board = board_and_fields.Board(board_state)

    Args:
        fen (str): string w takiej formie: 8/8/4K3/8/8/7k/8/8 w - - 0 1

    Returns:
        list: lista obiektów figur, zobacz Board.__init__ aby się dowiedzieć więcej.
    """
    rows = fen.split(" ")[0].split("/")
    board_state = []
    for r, row in enumerate(rows):
        board_row = []
        c = 0
        for char in row:
            if char.isdigit():
                for _ in range(int(char)):
                    board_row.append(board_and_fields.Field(7-c,7-r))
                    c += 1
            else:
                color = 'w' if char.isupper() else 'b'
                piece_type = char.lower()
                piece_class = {
                    'r': figures.Rook,
                    'n': figures.Knight,
                    'b': figures.Bishop,
                    'q': figures.Queen,
                    'k': figures.King,
                    'p': figures.Pawn
                }[piece_type]
                board_row.append(board_and_fields.Field(7-c, 7-r, piece_class(color)))
                #Do linii 49 włącznie jest do zamienienia
                if piece_type == 'p':
                    if board_row[-1].figure.color == "w" and 7-r != 1:
                        board_row[-1].figure.has_moved = True
                    if board_row[-1].figure.color == "b" and 7-r != 6:
                        board_row[-1].figure.has_moved = True
                if piece_type == 'k' and 7-r != 3:
                    if board_row[-1].figure.color == "w" and 7-r != 0:
                        board_row[-1].figure.has_moved = True
                    if board_row[-1].figure.color == "b" and 7-r != 7:
                        board_row[-1].figure.has_moved = True
                if piece_type == "r" and board_row[-1].x not in [0,7] and board_row[-1].x not in [0,7]:
                    board_row[-1].figure.has_moved = True
                c += 1
        board_row.reverse()
        board_state.append(board_row)
    board_state.reverse()
    return board_state

def board_to_fen(board_state:list)->str:
    """Z listy obiektów zwraca fena. Zastosowanie: tylko dla board_makera, nie dla czegokolwiek innego, bo:
    jest normalnie, a w normalnych trybach gry board jest odwrócony

    Args:
        board_state (list): board state

    Returns:
        str: fen
    """
    fen = ""
    for row in board_state:
        empty_count = 0
        for field in row:
            if field.figure is None:
                empty_count += 1
            else:
                if empty_count > 0:
                    fen += str(empty_count)
                    empty_count = 0
                piece = field.figure
                piece_char = piece.type[0].upper() if piece.type != 'pawn' else 'P'
                if piece.color == 'b':
                    piece_char = piece_char.lower()
                fen += piece_char
        if empty_count > 0:
            fen += str(empty_count)
        fen += "/"
    fen = fen[:-1]  # Remove the trailing slash
    fen += " w - - 0 1"  # Add default FEN suffix
    return fen


def board_to_fen_inverted(board_state: list) -> str:
    """Z listy obiektów zwraca FEN, uwzględniając odwrócenie planszy.
    Stosować dla trybów gry, gdzie plansza jest odwrócona,
    czyli wszystkich poza custom board makerem.

    Args:
        board_state (list): board state

    Returns:
        str: FEN
    """
    fen = ""
    for row in reversed(board_state):  # Odwracamy kolejność wierszy
        empty_count = 0
        for field in reversed(row):  # Odwracamy kolejność pól w wierszu
            if field.figure is None:
                empty_count += 1
            else:
                if empty_count > 0:
                    fen += str(empty_count)
                    empty_count = 0
                piece = field.figure
                piece_char = piece.type[0].upper() if piece.type != 'pawn' else 'P'
                if piece.color == 'b':
                    piece_char = piece_char.lower()
                fen += piece_char
        if empty_count > 0:
            fen += str(empty_count)
        fen += "/"
    fen = fen[:-1]  # Usuwamy końcowy ukośnik
    fen += " w - - 0 1"  # Dodajemy domyślny FEN suffix
    return fen