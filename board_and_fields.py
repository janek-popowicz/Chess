"""
This is gonna be chess game. Here are gonna be classes for figures and board.
"""
import figures
class Field:
    def __init__(self, x, y,  figure=None):
        self.x = x
        self.y = y
        self.figure = figure

    def remove_figure(self):
        self.figure = None
    def what_figure(self):
        return self.figure
class Board:
    def __init__(self):
        self.board = [[Field(0, 0, figures.Rook('w')), Field(1, 0, figures.Knight('w')), Field(2, 0, figures.Bishop('w')), Field(3, 0, figures.King('w')), Field(4, 0, figures.Queen('w')), Field(5, 0, figures.Bishop('w')), Field(6, 0, figures.Knight('w')), Field(7, 0, figures.Rook('w'))],
                [Field(0, 1, figures.Pawn('w')), Field(1, 1, figures.Pawn('w')), Field(2, 1, figures.Pawn('w')), Field(3, 1, figures.Pawn('w')), Field(4, 1, figures.Pawn('w')), Field(5, 1, figures.Pawn('w')), Field(6, 1, figures.Pawn('w')), Field(7, 1, figures.Pawn('w'))],
                [Field(0, 2), Field(1, 2), Field(2, 2), Field(3, 2), Field(4, 2), Field(5, 2), Field(6, 2), Field(7, 2)],
                [Field(0, 3), Field(1, 3), Field(2, 3), Field(3, 3), Field(4, 3), Field(5, 3), Field(6, 3), Field(7, 3)],
                [Field(0, 4), Field(1, 4), Field(2, 4), Field(3, 4), Field(4, 4), Field(5, 4), Field(6, 4), Field(7, 4)],
                [Field(0, 5), Field(1, 5), Field(2, 5), Field(3, 5), Field(4, 5), Field(5, 5), Field(6, 5), Field(7, 5)],
                [Field(0, 6, figures.Pawn('b')), Field(1, 6, figures.Pawn('b')), Field(2, 6, figures.Pawn('b')), Field(3, 6, figures.Pawn('b')), Field(4, 6, figures.Pawn('b')), Field(5, 6, figures.Pawn('b')), Field(6, 6, figures.Pawn('b')), Field(7, 6, figures.Pawn('b'))],
                [Field(0, 7, figures.Rook('b')), Field(1, 7, figures.Knight('b')), Field(2, 7, figures.Bishop('b')), Field(3, 7, figures.King('b')), Field(4, 7, figures.Queen('b')), Field(5, 7, figures.Bishop('b')), Field(6, 7, figures.Knight('b')), Field(7, 7, figures.Rook('b'))]
        ]
        self.incheck = False
    def print_board(self):
        print("\n" + "     7    6    5    4    3    2    1    0")
        print("  +" + "----+" *8 )
        for x in range(7,-1,-1):
            print(x, "| ",end="")
            for y in range(7,-1,-1):
                if self.board[x][y].figure == None:
                    print("  ",end="")
                else:
                    self.board[x][y].figure.print_figure()
                print(" | ",end="")
            print("\n" "  +" + "----+" *8 )
    def get_valid_moves(self,field):
        valid_cords = []
        if field.figure == None:
            print("Na tym polu nie ma figury")
        #Pionek to jedyna figura, której kierunek ruchu zależy od koloru
        elif field.figure.type == 'p':
            #Dla białego pionka
            if field.figure.color == 'w':
                #Ruchy bicia 
                if self.board[field.y+1][field.x + 1].figure != None:
                    valid_cords.append((field.x + 1,field.y+1))
                if self.board[field.y+1][field.x - 1].figure != None:
                    valid_cords.append((field.x - 1,field.y+1))
                #Zwykły ruch
                if self.board[field.y+1][field.x].figure == None:
                    valid_cords.append((field.x,field.y+1))
                #Pierwszy ruch
                if self.board[field.y+2][field.x].figure == None and field.figure.first_move == True:
                    valid_cords.append((field.x,field.y+2))
            else:
                #Ruchy bicia 
                if self.board[field.y-1][field.x + 1].figure != None:
                    valid_cords.append((field.x + 1,field.y-1))
                if self.board[field.y-1][field.x - 1].figure != None:
                    valid_cords.append((field.x - 1,field.y-1))
                #Zwykły ruch
                if self.board[field.y-1][field.x].figure == None:
                    valid_cords.append((field.x,field.y-1))
                #Pierwszy ruch
                if self.board[field.y-2][field.x].figure == None and field.figure.first_move == True:
                    valid_cords.append((field.x,field.y-2))
        #Ruchy dla innych figur
        else:
            movescheme = field.figure.move_scheme 
            for direction in movescheme:
                for distance in range(1,direction[2]+1):
                    try:
                        field_to_check = self.board[field.y + direction[1]*distance][field.x + direction[0]*distance]
                    #Sprawdzanie, czy koordynaty pola nie wyszły poza szachownicę
                    except IndexError:
                        break
                    #Sprawdzanie, czy na danym polu jest jakaś figura, i czy jest to król
                    if field_to_check.figure == None:
                        valid_cords.append((field_to_check.x,field_to_check.y))
                    else:
                        if field_to_check.figure.color == field.figure.color:
                            break
                        else:
                            if field_to_check.figure.type == 'K':
                                self.incheck = True
                                break
                            else:
                                valid_cords.append((field_to_check.x,field_to_check.y))
                        
        return valid_cords   
    def make_move(self, x1, y1, x2, y2):
        self.board[y2][x2].figure = self.board[y1][x1].figure
        self.board[y1][x1].figure = None