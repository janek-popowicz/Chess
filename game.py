"""
Tu będzie handlowany user input poprzez notację szachową
"""


import figures, board_and_fields

running = True

board = board_and_fields.Board()
while running:
    board.print_board()
    while True:
        y1 = int(input("Podaj rząd figury: "))
        x1 = int(input("Podaj kolumnę figury: "))
        y2 = int(input("Podaj rząd celu: "))
        x2 = int(input("Podaj kolumnę celu: "))
        print(board.incheck)
        if(x2,y2) in board.get_valid_moves(board.board[y1][x1]):
            board.make_move(x1, y1, x2, y2)
            break
        else: 
            print("Nielegalny ruch!")
        
