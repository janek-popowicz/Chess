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
    while True:
        y1 = int(input("Podaj rząd figury: "))
        x1 = int(input("Podaj kolumnę figury: "))
        y2 = int(input("Podaj rząd celu: "))
        x2 = int(input("Podaj kolumnę celu: "))
        if(y2,x2) in main_board.get_legal_moves(main_board.board_state[y1][x1],turn):
            main_board.make_move(y1, x1, y2,x2)
            if main_board.board_state[y2][x2].figure.type in ['p','R','K']:
                main_board.board_state[y2][x2].figure.has_moved = True
            break
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
            break
        else:
            main_board.print_board()
            print("Pat! Koniec gry")
            break
    
