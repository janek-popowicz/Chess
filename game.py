"""
Tu będzie handlowany user input poprzez notację szachową
"""
import figures, board_and_fields

running = True

main_board = board_and_fields.Board()

def get_valid_moves(current_board,field):
        valid_cords = []
        if field.figure == None:
            print("Na tym polu nie ma figury")
        #Pionek to jedyna figura, której kierunek ruchu zależy od koloru
        elif field.figure.type == 'p':
            #Dla białego pionka
            if field.figure.color == 'w':
                #Ruchy bicia 
                if current_board.board_state[field.y+1][field.x + 1].figure != None:
                    valid_cords.append((field.x + 1,field.y+1))
                if current_board.board_state[field.y+1][field.x - 1].figure != None:
                    valid_cords.append((field.x - 1,field.y+1))
                #Zwykły ruch
                if current_board.board_state[field.y+1][field.x].figure == None:
                    valid_cords.append((field.x,field.y+1))
                #Pierwszy ruch
                if current_board.board_state[field.y+2][field.x].figure == None and field.figure.first_move == True:
                    valid_cords.append((field.x,field.y+2))
            else:
                #Ruchy bicia 
                if current_board.board_state[field.y-1][field.x + 1].figure != None:
                    valid_cords.append((field.x + 1,field.y-1))
                if current_board.board_state[field.y-1][field.x - 1].figure != None:
                    valid_cords.append((field.x - 1,field.y-1))
                #Zwykły ruch
                if current_board.board_state[field.y-1][field.x].figure == None:
                    valid_cords.append((field.x,field.y-1))
                #Pierwszy ruch
                if current_board.board_state[field.y-2][field.x].figure == None and field.figure.first_move == True:
                    valid_cords.append((field.x,field.y-2))
        #Ruchy dla innych figur
        else:
            movescheme = field.figure.move_scheme 
            for direction in movescheme:
                for distance in range(1,direction[2]+1):
                    try:
                        field_to_check = current_board.board_state[field.y + direction[1]*distance][field.x + direction[0]*distance]
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
                                current_board.incheck = True
                                break
                            else:
                                valid_cords.append((field_to_check.x,field_to_check.y))
                        
        return valid_cords   

while running:
    main_board.print_board()
    while True:
        y1 = int(input("Podaj rząd figury: "))
        x1 = int(input("Podaj kolumnę figury: "))
        y2 = int(input("Podaj rząd celu: "))
        x2 = int(input("Podaj kolumnę celu: "))
        if(x2,y2) in get_valid_moves(main_board,main_board.board_state[y1][x1]):
            main_board.make_move(x1, y1, x2, y2)
            break
        else: 
            print("Nielegalny ruch!")
        
