"""
Tu będzie handlowany user input poprzez notację szachową
"""
import  board_and_fields

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
    if available_moves == []:
        if main_board.incheck == True:
            main_board.print_board()
            print("Szach mat! Koniec gry")
            running = False
        else:
            main_board.print_board()
            print("Pat! Koniec gry")
            running = False
    
