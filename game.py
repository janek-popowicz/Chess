"""
Tu będzie handlowany user input poprzez notację szachową
"""


import figures, board_and_fields

running = True

board = board_and_fields.Board()
while running:
    board.print_board()
    ruch = input("Podaj ruch: ")
    if ruch == "exit":
        running = False
        break
    else:
        board.make_move(0,0,4,4)
