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
