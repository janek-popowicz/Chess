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
    def ocena_materiału(self,): 
        for i in range(8):
            for j in range(8):
                pole = self.main_board[i][j]
                pole = str(pole)
                #print(f"Checking position ({i}, {j}): {pole}")  # Debugging print statement
                print(pole)
                if len(pole) < 2:
                    continue  # Skip if the pole does not represent a piece
                
                if pole[1] == 'p':
                    if pole[0] == 'w':
                        self.waga_białych += self.Pionek
                    else:
                        self.waga_czarnych += self.Pionek
                elif pole[1] == 'N':
                    if pole[0] == 'w':
                        self.waga_białych += self.Skoczek
                    else:
                        self.waga_czarnych += self.Skoczek
                elif pole[1] == 'B':
                    if pole[0] == 'w':
                        self.waga_białych += self.Goniec
                    else:
                        self.waga_czarnych += self.Goniec
                elif pole[1] == 'R':
                    if pole[0] == 'w':
                        self.waga_białych += self.Wieża
                    else:
                        self.waga_czarnych += self.Wieża
                elif pole[1] == 'Q':
                    if pole[0] == 'w':
                        self.waga_białych += self.Hetman
                    else:
                        self.waga_czarnych += self.Hetman

        print(f"Final weights - White: {self.waga_białych}, Black: {self.waga_czarnych}")  # Debugging print statement
        return [self.waga_białych, self.waga_czarnych]
                
