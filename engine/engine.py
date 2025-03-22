import engine.figures as figures
import engine.board_and_fields as board_and_fields
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
                direction = -1
            else:
                direction = 1
            return (king_pos[0],king_pos[1],king_pos[0],king_pos+2*direction)
        #Ruch dla pozostałych figur
        else:
            directions_to_check = moveschemes[notation]    
    #Ruch dla pionków
    else:
        notation = "p" + notation
        if turn == 'w':
            directions_to_check = [(1,0,1), (2,0,1),(1,1,1), (1,-1,1)]
        else:
            directions_to_check = [(-1,0,1), (-2,0,1),(-1,1,1), (-1,-1,1)]
    #Dekodowanie koordynatów
    for i in range(len(notation)):
        if notation[i].isdigit():
            target_field = board.board_state[(int(notation[i])-1)][7-(ord(notation[i-1]) - 97)]
            break
    #Szukanie figur określonych w notacji
    candidate_figures = []
    for row in range(0,8):
        for col in range(0,8):
            field = board.board_state[row][col]
            if field.figure:
                if field.figure.color == turn and field.figure.type == notation[0]:
                    #Dostosowanie pól do sprawdzenia dla pionków
                    if notation[0] == 'p':
                        if field.figure.has_moved:
                            directions_to_check[1] = (0,0,0) #zamiast usuwać ten kierunek, ustawiamy go na (0,0,0), aby zachować spójność indeksów
                        if "x" in notation:
                            directions_to_check[0] = (0,0,0)
                            directions_to_check[1] = (0,0,0)
                            directions_to_check[2] = (0,0,0)
                            directions_to_check[3] = (0,0,0)
                    #Sprawdzanie, czy pole docelowe jest w ruchach danej figury
                    for direction in directions_to_check:
                        for distance in range(1,direction[2]+1):
                            field_to_check_x = field.x + direction[1] * distance
                            field_to_check_y= field.y + direction[0] * distance
                            #Sprawdzanie, czy koordynaty pola nie wyszły poza szachownicę
                            if field_to_check_y > 7 or field_to_check_y < 0 or field_to_check_x > 7 or field_to_check_x < 0:
                                break
                            field_to_check = board.board_state[field_to_check_y][field_to_check_x]
                            #Sprawdzanie czy na docelowym polu jest jakaś figura i czy zgadza się z notacją
                            if field_to_check == target_field:
                                if notation[2] == "x" and notation[0] == "p":
                                    #sprawdzamy specjalny przypadek - en passant
                                    if target_field.figure != None and field.figure.can_enpassant == True:
                                        candidate_figures.append((field.y,field.x))
                                else:
                                    if field_to_check.figure and "x" in notation:
                                        candidate_figures.append((field.y,field.x))
                                    elif field_to_check.figure == None and "x" not in notation:
                                        candidate_figures.append((field.y,field.x))
    if len(candidate_figures) > 1:
        return "Nie wykonano ruchu, potrzeba więcej informacji"
    elif len(candidate_figures) == 1:
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
    start_tile = main_board.board_state[y1][x1] 
    destination_tile = main_board.board_state[y2][x2]
    if(y2,x2) in main_board.get_legal_moves(start_tile,turn):
        color_to_check = 'b' if start_tile.figure.color == 'w' else 'b'
        main_board.moves_algebraic += [chr(104 - x2) + str(y2+1)]
        if destination_tile.figure:
            main_board.moves_algebraic[-1] = 'x' + main_board.moves_algebraic[-1]
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
                if start_tile.y - destination_tile.y == 3:
                    main_board.moves_algebraic[-1] = "O-O"
                else:
                    main_board.moves_algebraic[-1] = "O-O-O"
                return True
        #Wykonanie enpassant
        elif destination_tile.figure == None and start_tile.figure.type == 'p':
            if main_board.board_state[start_tile.y][destination_tile.x].figure:
                if main_board.board_state[start_tile.y][destination_tile.x].figure.type == 'p':
                    if start_tile.figure.can_enpassant:
                        start_tile.figure.can_enpassant = False
                        main_board.board_state[start_tile.y][destination_tile.x].figure = None
                        main_board.moves_algebraic[-1] = str(start_tile.x) + main_board.moves_algebraic[-1]
        main_board.make_move(y1, x1, y2, x2)
        if destination_tile.figure:
            if destination_tile.figure.type in ['p','K','R']:
                destination_tile.figure.has_moved = True
        main_board.is_in_check(color_to_check)
        if main_board.incheck:
            main_board.moves_algebraic[-1] += '+'
        return True
    else: 
        print("Nielegalny ruch!")
        return False

def afterMove(turn: str, main_board, y1: int, x1: int, y2: int, x2: int) -> str:
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
    start_tile = main_board.board_state[y1][x1]
    destination_tile = main_board.board_state[y2][x2]
    available_moves = []
    for y in range(0,8):
        for x in range(0,8):
            if main_board.board_state[y][x].figure:
                if main_board.board_state[y][x].figure.color == turn:
                    available_moves+=main_board.get_legal_moves(main_board.board_state[y][x],turn)
                if main_board.board_state[y][x].figure.type == 'p':
                    #Sprawdzanie flag enpassant
                    if main_board.board_state[y][x].figure.can_enpassant == True:
                        main_board.board_state[y][x].figure.can_enpassant = False
    #Sprawdzanie enpassant
    if destination_tile.figure:
        if destination_tile.figure.type == 'p' :
            if (destination_tile.y - start_tile.y) in [2,-2]:
                direction_x = -1
                for i in range(2):
                    if destination_tile.x + direction_x >= 0 and destination_tile.x + direction_x <= 7:
                        if main_board.board_state[destination_tile.y][destination_tile.x + direction_x].figure:
                            if (main_board.board_state[destination_tile.y][destination_tile.x + direction_x].figure.type == 'p' 
                            and main_board.board_state[destination_tile.y][destination_tile.x + direction_x].figure.color != destination_tile.figure.color):
                                main_board.board_state[destination_tile.y][destination_tile.x + direction_x].figure.can_enpassant = True
                    direction_x = 1
        #Sprawdzanie promocji pionków
            if destination_tile.y in [0,7]:
                return("promotion", destination_tile.y, destination_tile.x)
        if available_moves == []:
            main_board.is_in_check(turn)
            if main_board.incheck == True:
                main_board.print_board()
                return("checkmate", 0, 0)
            else:
                main_board.print_board()
                return("stalemate", 0, 0)
        main_board.is_in_check(turn)
        if main_board.incheck == True:
            return ("check",0,0)
        return(1,1,1)



def promotion(y: int, x: int, main_board, choice: str) -> None:
    """
    Obsługuje promocję pionka.

    Args:
        y (int): Współrzędna wiersza pionka.
        x (int): Współrzędna kolumny pionka.
        main_board (Board): Obiekt planszy szachowej.
        choice (str): Wybór promocji ('1' dla skoczka, '2' dla gońca, '3' dla wieży, '4' dla królowej).

    Returns:
        None
    """
    color = main_board.board_state[y][x].figure.color 
    if choice == "1":
        main_board.board_state[y][x].figure = figures.Knight(color)
    if choice == "2":
        main_board.board_state[y][x].figure = figures.Bishop(color)
    if choice == "3":
        main_board.board_state[y][x].figure = figures.Rook(color)
    if choice == "4":
        main_board.board_state[y][x].figure = figures.Queen(color)
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