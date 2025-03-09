"""
Tu jest silnik, obsługujący ruchy. Obsługa imputu usera i pętle gry mają być w osobnych plikach:
- test-mode-normal-game.py
- test-mode-random-ai.py
- test-mode-minimax-ai.py
- test-mode-monte-carlo-ai.py
- test-mode-server.py
- test-mode-client.py
Finalnie będą to podobne pliki, ale bez test-mode w nazwie, i to one będą w sobie też miały pygame moduły szachownicy.
Dlaczego w nich będzie pygame, i będzie się dużo razy powtarzał? Bo i gra szachowa i pygame gui wymagają pętli gry, więc będą miały one wspólne pętle.
Jeżeli jest to głupie i (Benedykt) masz lepszy plan, to daj znać.
Dzięki copilot za pomoc w pisaniu tego komentarza.
"""

import figures,board_and_fields

def tryMove(turn:str,main_board,y1:int, x1:int, y2:int, x2:int)->bool:
    """ Próbuje zrobić ruch

    Args:
        turn (str): 'w' lub 'b'
        main_board (_type_): board object
        y1 (int): coordinate
        x1 (int): coordinate
        y2 (int): coordinate
        x2 (int): coordinate

    Returns:
        bool: True when move was done, False when not
    """
    start_tile = main_board.board_state[y1][x1] 
    destination_tile = main_board.board_state[y2][x2]
    if(y2,x2) in main_board.get_legal_moves(start_tile,turn):
            #Wykonanie roszady
            if destination_tile.figure != None:
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
                    return True
            #Wykonanie enpassant
            elif destination_tile.figure == None and start_tile.figure.type == 'p':
                if main_board.board_state[start_tile.y][destination_tile.x].figure != None:
                    if main_board.board_state[start_tile.y][destination_tile.x].figure.type == 'p':
                        if start_tile.figure.can_enpassant_l:
                            start_tile.figure.can_enpassant_l = False
                            main_board.board_state[start_tile.y][destination_tile.x].figure = None
                            return True
                        elif start_tile.figure.can_enpassant_r:
                            start_tile.figure.can_enpassant_r = False
                            main_board.board_state[start_tile.y][destination_tile.x].figure = None
                            return True
            main_board.make_move(y1, x1, y2, x2)
            if destination_tile.figure != None:
                if destination_tile.figure.type in ['p','K','R']:
                    destination_tile.figure.has_moved = True
            return True
    else: 
        print("Nielegalny ruch!")
        return False

def afterMove(turn:str, main_board, y1:int, x1:int, y2:int, x2:int)->str:
    """To jest potrzebne, aby sprawdzać szachmata, enpassant

    Args:
        turn (str): 'w' or 'b'
        main_board (_type_): board object
        y1 (int): coordinate
        x1 (int): coordinate
        y2 (int): coordinate
        x2 (int): coordinate

    Returns:
        str: returns action to do
    """
    start_tile = main_board.board_state[y1][x1]
    destination_tile = main_board.board_state[y2][x2]
    available_moves = []
    for y in range(0,8):
        for x in range(0,8):
            if main_board.board_state[y][x].figure != None:
                if main_board.board_state[y][x].figure.color == turn:
                    available_moves+=main_board.get_legal_moves(main_board.board_state[y][x],turn)
                if main_board.board_state[y][x].figure.type == 'p':
                    #Sprawdzanie flag enpassant
                    if main_board.board_state[y][x].figure.can_enpassant_l == True:
                        main_board.board_state[y][x].figure.can_enpassant_l = False
                    if main_board.board_state[y][x].figure.can_enpassant_r == True:
                        main_board.board_state[y][x].figure.can_enpassant_r = False
    #Sprawdzanie enpassant
    if destination_tile.figure != None:
        if destination_tile.figure.type == 'p' :
            direction = 1 if destination_tile.figure.color == 'w' else -1
            try:
                if main_board.board_state[destination_tile.y][destination_tile.x +direction].figure != None:
                    if (main_board.board_state[destination_tile.y][destination_tile.x+direction].figure.type == 'p' 
                    and main_board.board_state[destination_tile.y][destination_tile.x+direction].figure.color != destination_tile.figure.color):
                        main_board.board_state[destination_tile.y][destination_tile.x+direction].figure.can_enpassant_l = True
                if main_board.board_state[destination_tile.y][destination_tile.x -direction].figure != None:
                    if (main_board.board_state[destination_tile.y][destination_tile.x-direction].figure.type == 'p' 
                    and main_board.board_state[destination_tile.y][destination_tile.x-direction].figure.color != destination_tile.figure.color):
                        main_board.board_state[destination_tile.y][destination_tile.x-direction].figure.can_enpassant_r = True
            except IndexError:
                pass
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
    return(1,1,1)
    
def promotion(y:int,x:int,main_board, choice:str)->None:
    """ Robi promocję na podstawie wybranego wyboru
    
    Args:
        turn (str): 'w' or 'b'
        y (int): earlier y from afterMove
        x (int): earlier x from afterMove
        main_board (): board object
        choice (str): '1', '2', '3', '4'; knight, bishop, rook,queen
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
        if (start_tile.figure != None 
            and destination_tile.figure != None):
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
                                    if main_board.board_state[tile_to_check_y][tile_to_check_x].figure != None:
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
            if main_board.board_state[y][x].figure != None:
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
                    if destination_tile.figure != None:
                        if destination_tile.figure.type == 'p' :
                            direction = 1 if destination_tile.figure.color == 'w' else -1
                            try:
                                if main_board.board_state[destination_tile.y][destination_tile.x +direction].figure != None:
                                    if (main_board.board_state[destination_tile.y][destination_tile.x+direction].figure.type == 'p' 
                                    and main_board.board_state[destination_tile.y][destination_tile.x+direction].figure.color != destination_tile.figure.color):
                                        main_board.board_state[destination_tile.y][destination_tile.x+direction].figure.can_enpassant_l = True
                                if main_board.board_state[destination_tile.y][destination_tile.x -direction].figure != None:
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