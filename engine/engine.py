import engine.figures as figures
import engine.board_and_fields as board_and_fields
import engine.fen_operations as fen_operations
import copy
def notation_to_cords(board, notation: str, turn: str):
    """
    Konwertuje notację szachową na współrzędne na planszy.

    Args:
        board (Board): Obiekt planszy szachowej.
        notation (str): Ruch w standardowej notacji szachowej (np. "e4", "Nf3").
        turn (str): Tura gracza ('w' dla białych, 'b' dla czarnych).

    Returns:
        tuple: Krotka współrzędnych (start_y, start_x, target_y, target_x), jeśli ruch jest poprawny.
        str: Komunikat o błędzie, jeśli ruch nie może zostać określony.
    """
    moveschemes = {
            'N':[(2,1,1),(-2,1,1),(2,-1,1),(-2,-1,1),(1,2,1),(1,-2,1),(-1,2,1),(-1,-2,1)],
            'B':[(1,1,8),(1,-1,8),(-1,1,8),(-1,-1,8),],
            'R':[(0, 1 ,8), (0, -1 ,8), (1, 0 ,8), (-1, 0 ,8)],
            'Q':[(1,1,8),(1,-1,8),(-1,1,8),(-1,-1,8),(0, 1 ,8), (0, -1 ,8), (1, 0 ,8), (-1, 0 ,8)],
            'K':[(1,1,1),(1,-1,1),(-1,1,1),(-1,-1,1),(0, 1 ,1), (0, -1 ,1), (1, 0 ,1), (-1, 0 ,1)],
        }
    if notation[0].isupper():
        #Wykonanie roszady
        if notation[0] == 'O':
            if turn == 'w':
                king_pos = (0,3)
            else:
                king_pos = (7,3)
            if len(notation) == 3:
                rook_x = 0
            else:
                rook_x = 7                
            return (king_pos[0],king_pos[1],king_pos[0],rook_x)
        #Ruch dla pozostałych figur
        else:
            movescheme = moveschemes[notation[0]]    
    #Ruch dla pionków
    else:
        notation = "p" + notation
        if turn == 'w':
            movescheme = [(1,0,1), (2,0,1),(1,1,1), (1,-1,1)]
        else:
            movescheme = [(-1,0,1), (-2,0,1),(-1,1,1), (-1,-1,1)]
    #Dekodowanie koordynatów
    for i in range(len(notation)):
        if notation[i].isdigit():
            target_field = board.board_state[(int(notation[i])-1)][7-(ord(notation[i-1]) - 97)]
            break
    #Szukanie figur określonych w notacji
    candidate_figures = []
    for cord in board.piece_cords:
                figure = board.board_state[cord[0]][cord[1]].figure 
                if figure.color == turn and figure.type == notation[0]:
                    #Dostosowanie pól do sprawdzenia dla pionków
                    directions_to_check = copy.copy(movescheme)
                    if notation[0] == 'p':
                        if figure.has_moved:
                            directions_to_check[1] = (0,0,0) #zamiast usuwać ten kierunek, ustawiamy go na (0,0,0), aby zachować spójność indeksów
                        if "x" in notation:
                            directions_to_check[0] = (0,0,0)
                            directions_to_check[1] = (0,0,0)
                        elif not figure.can_enpassant:
                            directions_to_check[2] = (0,0,0)
                            directions_to_check[3] = (0,0,0)
                    #Sprawdzanie, czy pole docelowe jest w ruchach danej figury
                    for direction in directions_to_check:
                        for distance in range(1,direction[2]+1):
                            field_to_check_x = cord[1] + direction[1] * distance
                            field_to_check_y= cord[0] + direction[0] * distance
                            #Sprawdzanie, czy koordynaty pola nie wyszły poza szachownicę
                            if field_to_check_y > 7 or field_to_check_y < 0 or field_to_check_x > 7 or field_to_check_x < 0:
                                break
                            field_to_check = board.board_state[field_to_check_y][field_to_check_x]
                            #Sprawdzanie czy na docelowym polu jest jakaś figura i czy zgadza się z notacją
                            if field_to_check == target_field:
                                if notation[2] == "x" and notation[0] == "p":
                                    #sprawdzamy specjalny przypadek - en passant
                                    if not target_field.figure and figure.can_enpassant:
                                        candidate_figures.append((cord[0],cord[1]))
                                if field_to_check.figure and "x" in notation:
                                    candidate_figures.append((cord[0],cord[1]))
                                elif field_to_check.figure == None and "x" not in notation:
                                    candidate_figures.append((cord[0],cord[1]))
                            if field_to_check.figure:
                                break
    if len(candidate_figures) > 1:
        if notation[1].isdigit():
            spec = notation[1] -1
            for candidate_figure in candidate_figures():
                if candidate_figure[0] != spec:
                    candidate_figures.remove(candidate_figure)
        else:
            spec = 7-(ord(notation[1]) - 97)
            for candidate_figure in candidate_figures:
                if candidate_figure[1] != spec:
                    candidate_figures.remove(candidate_figure)
        if len(candidate_figures) > 1:
            return "Nie wykonano ruchu, potrzeba więcej informacji"
    if len(candidate_figures) == 1:
        return (candidate_figures[0][0],candidate_figures[0][1],target_field.y,target_field.x)
    elif len(candidate_figures) == 0:
        return "Nie wykonano ruchu, nie ma figury zdolnej do tego ruchu"

def tryMove(turn:str,main_board,y1:int, x1:int, y2:int, x2:int)->bool:
    """ Próbuje zrobić ruch

Args:
    turn (str): Tura gracza ('w' lub 'b').
    main_board (Board): Obiekt planszy szachowej.
    y1 (int): Współrzędna wiersza początkowego.
    x1 (int): Współrzędna kolumny początkowej.
    y2 (int): Współrzędna wiersza docelowego.
    x2 (int): Współrzędna kolumny docelowej.

Returns:
    bool: True, jeśli ruch jest poprawny i został wykonany, False w przeciwnym razie.
    """
    passed_over_tile = (-1,-1)
    halfmove_reset = True
    start_tile = main_board.board_state[y1][x1] 
    destination_tile = main_board.board_state[y2][x2]
    if start_tile.figure:    
        if start_tile.figure.type == "p":
            halfmove_reset = False
            if y1 - y2 in [-2,2]:
                passed_over_tile = (y2 - ((y2 - y1)/2),x1)
    elif destination_tile.figure:
        halfmove_reset = False
    if(y2,x2) in main_board.get_legal_moves(start_tile,turn):
        color_to_check = 'b' if start_tile.figure.color == 'w' else 'b'
        main_board.moves_algebraic += [chr(104 - x2) + str(y2+1)]
        if destination_tile.figure:
            main_board.moves_algebraic[-1] = chr(104 - x1) +  'x' + main_board.moves_algebraic[-1]
            main_board.moves_algebraic_long += [chr(104-x1)+str(y1+1)+'x'+chr(104-x2)+str(y2+1)]
        else:
            main_board.moves_algebraic_long += [chr(104-x1)+str(y1+1)+'-'+chr(104-x2)+str(y2+1)]
        if not start_tile.figure.type == "p":
            main_board.moves_algebraic_long[-1] = start_tile.figure.type + main_board.moves_algebraic_long[-1]
        #print(main_board.fen_history)
        #Wykonanie roszady
        if destination_tile.figure:
            if destination_tile.figure.type == 'R' and  destination_tile.figure.color == start_tile.figure.color:
                #Zmiana flag roszady
                start_tile.figure.has_moved = True
                destination_tile.figure.has_moved = True
                #Zmiana pozycji króla
                direction =  -1 if destination_tile.x - start_tile.x < 0 else 1
                main_board.board_state[start_tile.y][start_tile.x + 2*direction].figure = start_tile.figure
                #Zmiana pozycji wieży
                main_board.board_state[start_tile.y][start_tile.x + direction].figure = destination_tile.figure
                destination_tile.figure = None
                start_tile.figure = None
                main_board.piece_cords.remove((start_tile.y, start_tile.x))
                main_board.piece_cords.remove((destination_tile.y,destination_tile.x))
                main_board.piece_cords.append((start_tile.y,start_tile.x + 2*direction))
                main_board.piece_cords.append((start_tile.y,start_tile.x + direction))
                if start_tile.y - destination_tile.y == 3:
                    main_board.moves_algebraic[-1] = "O-O"
                    main_board.moves_algebraic_long[-1] = "O-O"
                else:
                    main_board.moves_algebraic[-1] = "O-O-O"
                    main_board.moves_algebraic_long[-1] = "O-O-O"

                main_board.fen_history.append(fen_operations.board_to_fen_inverted(main_board, "b" if turn == 'w' else "w", halfmove_reset, passed_over_tile))
                return True
        #Wykonanie enpassant
        elif destination_tile.figure == None and start_tile.figure.type == 'p' and x1 - x2 in [-1,1]:
            if main_board.board_state[start_tile.y][destination_tile.x].figure:
                if main_board.board_state[start_tile.y][destination_tile.x].figure.type == 'p':
                        if start_tile.figure.can_enpassant:
                            start_tile.figure.can_enpassant = 0
                            main_board.board_state[start_tile.y][destination_tile.x].figure = None
                            main_board.moves_algebraic[-1] = chr(104 - x1) + main_board.moves_algebraic[-1]
                            main_board.moves_algebraic_long[-1] = chr(104-x1)+str(y1+1)+'x'+chr(104-x2)+str(y2+1)
                            main_board.piece_cords.remove((start_tile.y, destination_tile.x))
        main_board.make_move(y1, x1, y2, x2)
        main_board.piece_cords.remove((y1,x1))
        if (y2,x2) not in main_board.piece_cords:
            main_board.piece_cords.append((y2,x2))
        if destination_tile.figure:
            if destination_tile.figure.type in ['p','K','R']:
                destination_tile.figure.has_moved = True
            if destination_tile.figure.type != 'p':
                main_board.moves_algebraic[-1] = destination_tile.figure.type + main_board.moves_algebraic[-1]
            
        main_board.is_in_check(color_to_check)
        if main_board.incheck:
            main_board.moves_algebraic[-1] += '+'
            main_board.moves_algebraic_long[-1] += '+'
        main_board.fen_history.append(fen_operations.board_to_fen_inverted(main_board, "b" if turn == 'w' else "w", halfmove_reset, passed_over_tile))
        return True
    else: 
        print("Nielegalny ruch!")
        return False
    
def undoMove(main_board: board_and_fields.Board) -> bool:
    """Cofa ruch, bazując na fenach zapisanych w historii. Należy zmieniać turn po cofnięciu ruchu!
    Zwraca True jeżeli operacja się powiodła, False w przeciwnym razie.
    """
    if len(main_board.fen_history) > 1:
        fen_operations.fen_to_board(main_board.fen_history[-2],main_board)
        main_board.fen_history.pop()
        main_board.print_board()
        main_board.moves_algebraic.pop()
        return True
    else:
        return False

def afterMove(turn: str, board, y1: int, x1: int, y2: int, x2: int) -> str:
    """
    Sprawdza stan planszy po wykonaniu ruchu.

    Args:
        turn (str): Tura gracza ('w' lub 'b').
        main_board (Board): Obiekt planszy szachowej.
        y1 (int): Współrzędna wiersza początkowego.
        x1 (int): Współrzędna kolumny początkowej.
        y2 (int): Współrzędna wiersza docelowego.
        x2 (int): Współrzędna kolumny docelowej.

    Returns:
        str: Komunikat wskazujący wynik ruchu (np. "checkmate", "stalemate", "check").
    """
    start_tile = board.board_state[y1][x1]
    destination_tile = board.board_state[y2][x2]
    available_moves = []
    only_kings = True 
    i=0
    while i < len(board.piece_cords):
        cord = board.piece_cords[i]
        field = board.board_state[cord[0]][cord[1]]
        if field.figure.color == turn:
            available_moves+=board.get_legal_moves(field,turn)
        if field.figure.type == 'p':
            #Sprawdzanie flag enpassant
            if field.figure.can_enpassant:
                field.figure.can_enpassant = 0
        if field.figure.type != 'K':
            only_kings = False
        i +=1 
        board.piece_cords.sort()
    if only_kings:
        return ("stalemate",0,0)
    if available_moves == []:
        board.is_in_check(turn)
        if board.incheck == True:
            board.print_board()
            return("checkmate", 0, 0)
        else:
            board.print_board()
            return("stalemate", 0, 0)

    #Sprawdzanie enpassant
    if destination_tile.figure:
        if destination_tile.figure.type == 'p' :
            if (destination_tile.y - start_tile.y) in [2,-2]:
                direction_x = -1
                for i in range(2):
                    if destination_tile.x + direction_x >= 0 and destination_tile.x + direction_x <= 7:
                        if board.board_state[destination_tile.y][destination_tile.x + direction_x].figure:
                            if (board.board_state[destination_tile.y][destination_tile.x + direction_x].figure.type == 'p' 
                            and board.board_state[destination_tile.y][destination_tile.x + direction_x].figure.color != destination_tile.figure.color):
                                board.board_state[destination_tile.y][destination_tile.x + direction_x].figure.can_enpassant = -direction_x
                    direction_x = 1
        #Sprawdzanie promocji pionków
            if destination_tile.y in [0,7]:
                return("promotion", destination_tile.y, destination_tile.x)
        board.is_in_check(turn)
        if board.incheck == True:
            return ("check",0,0)
    return(1,1,1)



def promotion(y: int, x: int, main_board: board_and_fields.Board, choice: str) -> None:
    """
    Handles pawn promotion.

    Args:
        y (int): Row coordinate of the pawn.
        x (int): Column coordinate of the pawn.
        main_board (Board): Chessboard object.
        choice (str): Promotion choice ('1' for Knight, '2' for Bishop, '3' for Rook, '4' for Queen).

    Returns:
        None: Promotes the pawn to the selected piece.

    Raises:
        ValueError: If the choice is invalid.
    """
    color = main_board.board_state[y][x].figure.color
    if choice == "1":
        main_board.board_state[y][x].figure = figures.Knight(color)
    elif choice == "2":
        main_board.board_state[y][x].figure = figures.Bishop(color)
    elif choice == "3":
        main_board.board_state[y][x].figure = figures.Rook(color)
    elif choice == "4":
        main_board.board_state[y][x].figure = figures.Queen(color)
    else:
        raise ValueError("Invalid promotion choice. Please select '1', '2', '3', or '4'.")
    
def save_in_short_algebraic(board, winner, result):
    """
    Saves the game moves in PGN format with timestamp filename.
    
    Args:
        board (Board): The chess board containing move history
        
    Returns:
        str: Path to the saved file or None if failed
    """
    from datetime import datetime
    import os

    if winner=="Biały" or winner=="White":
        result_number = "1-0"
    elif winner=="Czarny" or winner=="Black":
        result_number = "0-1"
    elif winner=="Remis" or winner =="Draw":
        result_number = "1/2-1/2"
    else:
        result_number = "*"

    try:
        # Create pgn folder if it doesn't exist
        if not os.path.exists('saves'):
            os.makedirs('saves')
            
        # Generate timestamp filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"saves/game_{timestamp}.pgn"

        
        # Format moves with move numbers
        formatted_moves = []
        for i in range(0, len(board.moves_algebraic), 2):
            move_number = i // 2 + 1
            white_move = board.moves_algebraic[i]
            
            if i + 1 < len(board.moves_algebraic):
                black_move = board.moves_algebraic[i + 1]
                formatted_moves.append(f"{move_number}. {white_move} {black_move}")
            else:
                formatted_moves.append(f"{move_number}. {white_move}")
        
        # Create PGN content with headers
        pgn_content = [
            '[Event "Chess Game"]',
            f'[Date "{datetime.now().strftime("%Y.%m.%d")}"]',
            '[White "Player 1"]',
            '[Black "Player 2"]',
            f'[Result "{result}"]',
            '',
            ' '.join(formatted_moves),
            f' {result_number}',
            ''
        ]
        
        # Save to file
        with open(filename, 'w') as f:
            f.write('\n'.join(pgn_content))
            
        return filename
        
    except Exception as e:
        print(f"Error saving PGN file: {str(e)}")
        return None

def save_in_long_algebraic(board, winner, result):
    """
    Saves the game moves in long PGN format with timestamp filename.
    
    Args:
        board (Board): The chess board containing move history
        
    Returns:
        str: Path to the saved file or None if failed
    """
    from datetime import datetime
    import os

    if winner=="Biały" or winner=="White":
        result_number = "1-0"
    elif winner=="Czarny" or winner=="Black":
        result_number = "0-1"
    elif winner=="Remis" or winner =="Draw":
        result_number = "1/2-1/2"
    else:
        result_number = "*"

    try:
        # Create pgn folder if it doesn't exist
        if not os.path.exists('saves'):
            os.makedirs('saves')
            
        # Generate timestamp filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"saves/game_{timestamp}_long.pgn"

        
        # Format moves with move numbers
        formatted_moves = []
        for i in range(0, len(board.moves_algebraic_long), 2):
            move_number = i // 2 + 1
            white_move = board.moves_algebraic_long[i]
            
            if i + 1 < len(board.moves_algebraic_long):
                black_move = board.moves_algebraic_long[i + 1]
                formatted_moves.append(f"{move_number}. {white_move} {black_move}")
            else:
                formatted_moves.append(f"{move_number}. {white_move}")
        
        # Create PGN content with headers
        pgn_content = [
            '[Event "Chess Game"]',
            f'[Date "{datetime.now().strftime("%Y.%m.%d")}"]',
            '[White "Player 1"]',
            '[Black "Player 2"]',
            f'[Result "{result}"]',
            '',
            ' '.join(formatted_moves),
            f' {result_number}',
            ''
        ]
        
        # Save to file
        with open(filename, 'w') as f:
            f.write('\n'.join(pgn_content))
            
        return filename
        
    except Exception as e:
        print(f"Error saving PGN file: {str(e)}")
        return None

'''
running = True
main_board = board_and_fields.Board()
turn = 'b'
while running:
turn = 'w' if turn == 'b' else 'b'
main_board.print_board()
main_board.is_in_check(turn)
if main_board.incheck == True:
    print("Szach!", end=" ")
moving = True
while moving:
    y1 = int(input("Podaj rząd figury: "))
    x1 = int(input("Podaj kolumnę figury: "))
    y2 = int(input("Podaj rząd celu: "))
    x2 = int(input("Podaj kolumnę celu: "))
    start_tile = main_board.board_state[y1][x1] 
    destination_tile = main_board.board_state[y2][x2]
    #Mechanizm roszady
    if (start_tile.figure 
        and destination_tile.figure):
        if (start_tile.figure.type == 'K' 
            and destination_tile.figure.type == 'R' ):
                if( destination_tile.figure.color == turn 
                and start_tile.figure.color == turn):
                    if (start_tile.figure.has_moved == False 
                        and destination_tile.figure.has_moved == False):
                        space_free = True
                        tile_to_check_y = start_tile.y
                        if start_tile.x < destination_tile.x:
                            j = 1
                        else:
                            j = -1
                            for i in range (1,start_tile.x - destination_tile.x):
                                tile_to_check_x = start_tile.x + i * j
                                if main_board.board_state[tile_to_check_y][tile_to_check_x].figure:
                                    space_free = False
                                    break
                        if space_free:
                            #Zmiana flag roszady
                            start_tile.figure.has_moved = True
                            destination_tile.figure.has_moved = True
                            #Zmiana pozycji króla
                            main_board.board_state[start_tile.y][start_tile.x + 2*j].figure = start_tile.figure
                            #Zmiana pozycji wieży
                            main_board.board_state[start_tile.y][start_tile.x + j].figure = destination_tile.figure
                            destination_tile.figure = None
                            start_tile.figure = None
                            moving = False
                else:
                    print("Nie twój ruch!")
    if(y2,x2) in main_board.get_legal_moves(start_tile,turn):
            main_board.make_move(y1, x1, y2,x2)
            if destination_tile.figure.type in ['p','R','K']:
                destination_tile.figure.has_moved = True
            moving = False
    else: 
        print("Nielegalny ruch!")
available_moves = []
for y in range(0,8):
    for x in range(0,8):
        if main_board.board_state[y][x].figure:
            color_to_check = 'w' if turn == 'b' else 'b'
            if main_board.board_state[y][x].figure.color == color_to_check:
                available_moves+=main_board.get_legal_moves(main_board.board_state[y][x],main_board.board_state[y][x].figure.color)
            if main_board.board_state[y][x].figure.type == 'p':
                #Sprawdzanie flag enpassant
                if main_board.board_state[y][x].figure.can_enpassant_l == True:
                    main_board.board_state[y][x].figure.can_enpassant_l = False
                if main_board.board_state[y][x].figure.can_enpassant_r == True:
                    main_board.board_state[y][x].figure.can_enpassant_r = False
                #Sprawdzanie enpassant
                if destination_tile.figure:
                    if destination_tile.figure.type == 'p' :
                        direction = 1 if destination_tile.figure.color == 'w' else -1
                        try:
                            if main_board.board_state[destination_tile.y][destination_tile.x +direction].figure:
                                if (main_board.board_state[destination_tile.y][destination_tile.x+direction].figure.type == 'p' 
                                and main_board.board_state[destination_tile.y][destination_tile.x+direction].figure.color != destination_tile.figure.color):
                                    main_board.board_state[destination_tile.y][destination_tile.x+direction].figure.can_enpassant_l = True
                            if main_board.board_state[destination_tile.y][destination_tile.x -direction].figure:
                                if (main_board.board_state[destination_tile.y][destination_tile.x-direction].figure.type == 'p' 
                                and main_board.board_state[destination_tile.y][destination_tile.x-direction].figure.color != destination_tile.figure.color):
                                    main_board.board_state[destination_tile.y][destination_tile.x-direction].figure.can_enpassant_r = True
                            if (destination_tile.x - start_tile.x) * direction and destination_tile.figure.can_enpassant_l:
                                destination_tile.figure.can_enpassant_l = False
                                main_board.board_state[start_tile.y][destination_tile.x].figure = None
                            if (start_tile.x - destination_tile.x) * direction and destination_tile.figure.can_enpassant_r:
                                destination_tile.figure.can_enpassant_r = False
                                main_board.board_state[start_tile.y][destination_tile.x].figure = None
                        except IndexError:
                            continue
                if y in [0,7]:
                    main_board.print_board()
                    choice = input(f"""Pionek w kolumnie {x} dotarł do końca planszy. Wpisz:
1 - Aby zmienić go w Skoczka
2 - Aby zmienić go w Gońca
3 - Aby zmienić go w Wieżę
4 - Aby zmienić go w Królową
                            """)
                    if choice == "1":
                        main_board.board_state[y][x].figure = figures.Knight(turn)
                    if choice == "2":
                        main_board.board_state[y][x].figure = figures.Bishop(turn)
                    if choice == "3":
                        main_board.board_state[y][x].figure = figures.Rook(turn)
                    if choice == "4":
                        main_board.board_state[y][x].figure = figures.Queen(turn)
if available_moves == []:
    if main_board.incheck == True:
        main_board.print_board()
        print("Szach mat! Koniec gry")
        running = False
    else:
        main_board.print_board()
        print("Pat! Koniec gry")
        running = False

'''