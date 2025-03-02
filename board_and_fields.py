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
class Board:
    def __init__(self):
        self.board_state = [[Field(0, 0, figures.Rook('w')), Field(1, 0, figures.Knight('w')), Field(2, 0, figures.Bishop('w')), Field(3, 0, figures.King('w')), Field(4, 0, figures.Queen('w')), Field(5, 0, figures.Bishop('w')), Field(6, 0, figures.Knight('w')), Field(7, 0, figures.Rook('w'))],
                [Field(0, 1, figures.Pawn('w')), Field(1, 1, figures.Pawn('w')), Field(2, 1, figures.Pawn('w')), Field(3, 1, figures.Pawn('w')), Field(4, 1, figures.Pawn('w')), Field(5, 1, figures.Pawn('w')), Field(6, 1, figures.Pawn('w')), Field(7, 1, figures.Pawn('w'))],
                [Field(0, 2), Field(1, 2), Field(2, 2), Field(3, 2), Field(4, 2), Field(5, 2), Field(6, 2), Field(7, 2)],
                [Field(0, 3), Field(1, 3), Field(2, 3), Field(3, 3), Field(4, 3), Field(5, 3), Field(6, 3), Field(7, 3)],
                [Field(0, 4), Field(1, 4), Field(2, 4), Field(3, 4), Field(4, 4), Field(5, 4), Field(6, 4), Field(7, 4)],
                [Field(0, 5), Field(1, 5), Field(2, 5), Field(3, 5), Field(4, 5), Field(5, 5), Field(6, 5), Field(7, 5)],
                [Field(0, 6, figures.Pawn('b')), Field(1, 6, figures.Pawn('b')), Field(2, 6, figures.Pawn('b')), Field(3, 6, figures.Pawn('b')), Field(4, 6, figures.Pawn('b')), Field(5, 6, figures.Pawn('b')), Field(6, 6, figures.Pawn('b')), Field(7, 6, figures.Pawn('b'))],
                [Field(0, 7, figures.Rook('b')), Field(1, 7, figures.Knight('b')), Field(2, 7, figures.Bishop('b')), Field(3, 7, figures.King('b')), Field(4, 7, figures.Queen('b')), Field(5, 7, figures.Bishop('b')), Field(6, 7, figures.Knight('b')), Field(7, 7, figures.Rook('b'))]
        ]
        self.incheck = False
    def make_move(self, y1, x1, y2, x2):
        self.board_state[y2][x2].figure = self.board_state[y1][x1].figure
        self.board_state[y1][x1].figure = None
    def get_regular_moves(self,field):
        possible_cords = [] 
        if field.figure == None:
            print("Na tym polu nie ma figury!",end=" ")
            return []
        movescheme = []
        for direction in field.figure.move_scheme:
            movescheme.append(direction)
        if field.figure.type == 'p':
            if field.figure.has_moved == False:
                if field.figure.color == 'w':
                    movescheme.append((0,1,2))
                else:
                    movescheme.append((0,-1,2))            
        for direction in movescheme:
            for distance in range(1,direction[2]+1):
                field_to_check_x = field.x + direction[0] * distance
                field_to_check_y= field.y + direction[1] * distance
                #Sprawdzanie, czy koordynaty pola nie wyszły poza szachownicę
                if field_to_check_y > 7 or field_to_check_y < 0 or field_to_check_x > 7 or field_to_check_x < 0:
                    break 
                field_to_check = self.board_state[field_to_check_y][field_to_check_x]
                #Sprawdzanie, czy na danym polu jest jakaś figura
                if field_to_check.figure != None:
                    break    
                possible_cords.append((field_to_check.y,field_to_check.x))

        return possible_cords   
    def get_attack_moves(self,field):
        possible_cords = [] 
        try:
            attackscheme = field.figure.attack_scheme 
        except AttributeError:
            attackscheme = field.figure.move_scheme
        for direction in attackscheme:
            for distance in range(1,direction[2]+1):
                field_to_check_x = field.x + direction[0] * distance
                field_to_check_y= field.y + direction[1] * distance
                #Sprawdzanie, czy koordynaty pola nie wyszły poza szachownicę
                if field_to_check_y > 7 or field_to_check_y < 0 or field_to_check_x > 7 or field_to_check_x < 0:
                    break 
                field_to_check = self.board_state[field_to_check_y][field_to_check_x]
                #Sprawdzanie, czy na polu do zbicia jest król
                if field_to_check.figure != None:
                    if field_to_check.figure.color != field.figure.color:
                        if field_to_check.figure.type == 'K':
                            self.incheck = True
                        possible_cords.append((field_to_check.y,field_to_check.x)) 
                    break
        return possible_cords
    def is_in_check(self,color):
        enemy_attacks = []
        for y in range(0,8):
            for x in range(0,8):
                tile = self.board_state[y][x]
                if tile.figure !=None:
                    if tile.figure.type == 'K' and tile.figure.color == color:
                        king_position = (y,x)
                    if tile.figure.color !=color:
                        enemy_attacks = enemy_attacks + self.get_attack_moves(tile)
        enemy_attacks = set(enemy_attacks)
        if king_position in enemy_attacks:
            if self.incheck == False:
                self.incheck = True
                print("Szach!",end=" ")
        else:
            self.incheck = False   
    def get_legal_moves(self,field,turn):
        if field.figure == None:
            print("Na tym polu nie ma figury!",end=" ")
            return []
        elif field.figure.color != turn:
            print("To nie twój ruch!", end=" ")
            return []
        else:
            possible_moves = self.get_regular_moves(field) + self.get_attack_moves(field)
            legal_cords = []
            for move in possible_moves:
                if self.board_state[move[0]][move[1]].figure != None:
                    if self.board_state[move[0]][move[1]].figure.type == 'K' and self.board_state[move[0]][move[1]].figure.color != turn:
                        self.incheck = True
                        print("Szach!",end=" ")
                    else:
                        legal_cords.append(move)
                else:            
                    self.make_move(field.y,field.x,move[0],move[1])
                    self.is_in_check(turn)
                    if not self.incheck:
                        legal_cords.append(move)
                    self.make_move(move[0],move[1],field.y,field.x)
            return legal_cords
        
    def print_board(self):
        print("+" + "----+" *8 )
        for x in range(7,-1,-1):
            print( "| ",end="")
            for y in range(7,-1,-1):
                if self.board_state[x][y].figure == None:
                    print("  ",end="")
                else:
                    self.board_state[x][y].figure.print_figure()
                print(" | ",end="")
            print(x)
            print("+" + "----+" *8 )
        print("  7    6    5    4    3    2    1    0")
    