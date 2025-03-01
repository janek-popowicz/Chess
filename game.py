"""
Tu będzie handlowany user input poprzez notację szachową
"""
import figures, board_and_fields

running = True

main_board = board_and_fields.Board()

turn = 'b'
     
while running:
    turn = 'w' if turn == 'b' else 'b'
    main_board.print_board()
    while True:
        y1 = int(input("Podaj rząd figury: "))
        x1 = int(input("Podaj kolumnę figury: "))
        y2 = int(input("Podaj rząd celu: "))
        x2 = int(input("Podaj kolumnę celu: "))
        if(x2,y2) in main_board.get_legal_moves(main_board.board_state[y1][x1],turn):
            main_board.make_move(x1, y1, x2, y2)
            break
        else: 
            print("Nielegalny ruch!")
        
