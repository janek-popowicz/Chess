import engine.figures as figures
import engine.board_and_fields as board_and_fields
def fen_to_board(fen:str, board):
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
                c += 1
        board_row.reverse()
        board_state.append(board_row)
    board_state.reverse()
    board.board_state = board_state
    char = -1
    for i in [0,1]:
        while fen[char] != " ":     
            char += -1
        char += -1
    if fen[char] != "-":
        passed_over_tile = (int(fen[char])-1,104 - ord(fen[char-1])) 
        char += -1
    else:
        passed_over_tile = (-1,-1)
    char += -2
    castling_str = ""
    while fen[char] != " ":
        castling_str = fen[char] + castling_str
        char += -1
    turn = fen[char - 1]
    rook_positions = {(0,0):"K", (0,7):"Q",(7,0):"k",(7,7):"q"}
    for cord in board.piece_cords:
        field = board.board_state[cord[0]][cord[1]]
        if field.figure:
            if field.figure.type == "R":
                if (cord[0],cord[1]) in rook_positions:
                    color = "w" if rook_positions[(cord[0],cord[1])].isupper() else "b"
                    if rook_positions[(cord[0],cord[1])] not in castling_str or field.figure.color != color:
                        field.figure.has_moved = True
            elif field.figure.type == "K":
                if field.figure.color == "w" and ("K" not in castling_str and "Q" not in castling_str):
                    field.figure.has_moved = True
                elif ("k" not in castling_str and "k" not in castling_str):
                    field.figure.has_moved = True
            elif field.figure.type == "p":
                if field.figure.color == turn:
                    direction = 1 if turn == "w" else -1
                    if passed_over_tile[0] - cord[0] == direction:
                        field.figure.can_enpassant = passed_over_tile[1] - (cord[1])
                if field.figure.color == "w" and field.y != 1:
                    field.figure.has_moved = True
                elif field.figure.color == "b" and field.y != 6:
                    field.figure.has_moved = True
    board.piece_cords = []
    for row in range(0,8):
        for col in range(0,8):
            if board.board_state[row][col].figure:
                board.piece_cords.append((row, col))

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


def board_to_fen_inverted(board, turn:str, halfmove_reset:bool=0,passed_over_tile:tuple=(-1,-1)) -> str:
    """Z listy obiektów zwraca FEN, uwzględniając odwrócenie planszy.
    Stosować dla trybów gry, gdzie plansza jest odwrócona,
    czyli wszystkich poza custom board makerem.

    Args:
        board_state (list): board state
        turn (str): 'w' or 'b'
        y1 (int): współrzędna y pola startowego 
        x1 (int): współrzędna x pola startowego 
        y2 (int): współrzędna y pola docelowego 
        x2 (int): współrzędna x pola docelowego 

    Returns:
        str: FEN
    """
    fen = ""
    castling = []
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
    fen += " " + turn + " " # Dodajemy informację o ruchu
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
                                    castling.append(letters[i])  
                        i +=1
        castling_color = "b"    
    if len(castling) != 0:
        for letter in castling:
            fen += letter # Dodajemy informację o roszadzie 
    else:
        fen += " - "
    #Informacja o en passant
    if passed_over_tile != (-1,-1):
        passed_over_tile = chr(104 - passed_over_tile[1]) + str(int(passed_over_tile[0]+1)) 
    else:
        passed_over_tile = "-"
    fen += " " + passed_over_tile
    # Informacja o zegarze połówek ruchów
    if halfmove_reset: 
        board.halfmove_clock = 0
    else:    
        board.halfmove_clock += 1
    fen += " " + str(board.halfmove_clock)
    fen += " " + str((len(board.moves_algebraic) //2))
    return fen