import board_and_fields
import engine


class evaluation:
    def __init__(self):
        self.main_board = board_and_fields.Board()
        self.waga_czarnych = 0
        self.waga_białych = 0
        self.Pionek = 1
        self.Skoczek = 3
        self.Goniec = 3
        self.Wieża = 5
        self.Hetman = 9
        self.Król = 1000
    # w stoi za white a b za black
    def ocena_materiału(self): 
        for i in range(8):
            for j in range(8):
                pole = self.main_board.board[i][j]
                if pole[1] == 'p'       
