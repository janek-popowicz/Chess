import engine.figures as figures
import engine.board_and_fields as board_and_fields
def fen_to_board(fen:str):
    """Z fena zwraca listę obiektów. Należy zastosować tak:

board_state = fen_to_board_state(fen)
main_board = board_and_fields.Board(board_state)

    Args:
        fen (str): string w takiej formie: 8/8/4K3/8/8/7k/8/8 w - - 0 1

    Returns:
        list: lista obiektów figur, zobacz Board.__init__ aby się dowiedzieć więcej.
    """
    board = board_and_fields.Board()
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
                c += 1
        board_row.reverse()
        board_state.append(board_row)
    board_state.reverse()
    char = fen[-5]
    castling_str = ""
    while char != " ":
        castling_str += char
    cords = []
    if "K" in castling_str:
        cords += [(0,3),(0,0)]
    if "Q" in castling_str:
        cords += [(0,3),(0,7)]
    if "k" in castling_str:
        cords += [(7,3),(7,0)]
    if "q" in castling_str:
        cords += [(0,3),(7,7)]
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


def board_to_fen_inverted(board, turn:str, y1:int,x1:int,y2:int,x2:int) -> str:
    """Z listy obiektów zwraca FEN, uwzględniając odwrócenie planszy.
    Stosować dla trybów gry, gdzie plansza jest odwrócona,
    czyli wszystkich poza custom board makerem.

    Args:
        board_state (list): board state
        turn (str): 'w' or 'b'
        halfmove_reset (bool): czy resetować zegar połówek ruchów
        y1 (int): współrzędna y pola startowego 
        x1 (int): współrzędna x pola startowego 
        y2 (int): współrzędna y pola docelowego 
        x2 (int): współrzędna x pola docelowego 

    Returns:
        str: FEN
    """
    start_field = board.board_state[y1][x1]
    destination_field = board.board_state[y2][x2]
    fen = ""
    castling_str = "    " # Ustawiamy 4 spacje w informacji o roszadzie, aby zachować spójność indeksów
    for row in reversed(board.board_state):  # Odwracamy kolejność wierszy
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
    fen += " " + turn  # Dodajemy informację o ruchu
    #Informacje o roszadie
    i =0                
    castling_color = "w"
    letters = ["K","Q","k","q",]
    for row in [0,7]:
        if board.board_state[row][3].figure:
            if board.board_state[row][3].figure.type == "K" and board.board_state[row][3].figure.color == castling_color:
                if not board.board_state[row][3].figure.has_moved:
                    for col in [0,7]:
                        if board.board_state[row][col].figure:
                            if board.board_state[row][col].figure.type == "R" and board.board_state[row][col].figure.color == castling_color:
                                if not board.board_state[row][col].figure.has_moved:
                                    castling_str[i] == letters[i]  
                        i +=1
        castling_color = "b"               
    fen += " " + castling_str.strip() # Dodajemy informację o roszadzie (bez spacji)
    if start_field.figure.type == "p":
        if start_field.y - destination_field.y in [2,-2]:
            fen += " " + chr(104 - start_field.x) + str(destination_field.y + ((start_field.y - destination_field.y)/2)) #Dodajemy współrzędne pola, które "przeskoczył" pionek
        else:
            fen += " -"
        board.halfmove_clock = "0"
    elif destination_field.figure:
        board.halfmove_clock = "0"
    else:
        board.halfmove_clock = str(int(board.halfmove_clock) +1)
    fen += " " + board.halfmove_clock
    fen += " " + str((len(board.moves_algebraic) //2))
    return fen