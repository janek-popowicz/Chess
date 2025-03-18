import pygame
import sys
import json
import time
import os
import socket

#wygląda dziwnie ale musi działać
from engine.board_and_fields import *
from engine.engine import *
from engine.figures import *

CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"volume": 0.5, "resolution": "1260x960", "icons": "classic","highlight":0}

# Funkcja do rysowania szachownicy
def draw_board(screen, SQUARE_SIZE, main_board, in_check):
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for r in range(8):
        for c in range(8):
            color = colors[(r + c) % 2]
            if in_check and main_board.board_state[r][c].figure and main_board.board_state[r][c].figure.type == 'K' and main_board.board_state[r][c].figure.color == in_check:
                color = pygame.Color("red")
            pygame.draw.rect(screen, color, pygame.Rect((7-c)*SQUARE_SIZE, (7-r)*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(screen, board, SQUARE_SIZE, pieces):
    for r in range(8):
        for c in range(8):
            piece = board.get_piece(r, c)
            if piece != "--":
                screen.blit(pieces[piece], pygame.Rect((7-c)*SQUARE_SIZE, (7-r)*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
# Funkcja do podświetlania możliwych ruchów
def highlight_moves(screen, field, square_size:int,board, color_move, color_take):
    try:
        cords = board.get_legal_moves(field, field.figure.color)
    except AttributeError:
        return None
    for cord in cords:
        highlighted_tile = pygame.Surface((square_size, square_size))
        highlighted_tile.fill(color_move)
        if board.board_state[cord[0]][cord[1]].figure != None:
            if field.figure.color != board.board_state[cord[0]][cord[1]].figure.color:
                highlighted_tile.fill(color_take)
        if field.figure.type == 'p' and (field.x - cord[1]) != 0:
            highlighted_tile.fill(color_take)
        screen.blit(highlighted_tile, (((7-cord[1]) * square_size),((7- cord[0]) * square_size)))
# Funkcja do rysowania interfejsu
def draw_interface(screen, turn, SQUARE_SIZE, BLACK, texts, player_times, in_check, check_text):
    pygame.draw.rect(screen, BLACK, pygame.Rect(SQUARE_SIZE*8, 0, 200, SQUARE_SIZE*8))
    if turn == 'w':
        screen.blit(texts[0][0], texts[0][1])
    else:
        screen.blit(texts[1][0], texts[1][1])
    screen.blit(player_times[0][0], player_times[0][1])
    screen.blit(player_times[1][0], player_times[1][1])
    screen.blit(texts[2][0], texts[2][1])
    if in_check:
        
        screen.blit(check_text, (8*SQUARE_SIZE+10, 150))

#formatuje czas z formatu time.time() na minuty i sekundy
def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}:{seconds:02}"

def promotion_dialog(screen, SQUARE_SIZE:int, color:str)->str:
    """okienko promocji

    Args:
        screen (pygame): pygame screen
        SQUARE_SIZE (int): size of a square
        color (str): 'w' or 'b'

    Returns:
        str: '1', '2', '3' or '4'
    """
    font = pygame.font.Font(None, 36)

    dialog_text = "Pionek dotarł do końca planszy. Wybierz figurę do odzyskania."
    dialog = font.render(dialog_text, True, pygame.Color("white"))

    options = ["1. Koń", "2. Goniec", "3. Wieża", "4. Królowa"]
    # Nie usuwać numeru przed opcjami, on ma znaczenie! Bierze się to z poprzedniości tego jako wybór terminalowy.
    option_rects = []
    for i, option in enumerate(options):
        text = font.render(option, True, pygame.Color("white"))
        rect = text.get_rect(center=(SQUARE_SIZE*4, SQUARE_SIZE*(2+i)))
        option_rects.append((text, rect))
    
    while True:
        screen.fill(pygame.Color("black"))
        screen.blit(dialog, (100, 100))
        mouse_pos = pygame.mouse.get_pos()
        for i, (text, rect) in enumerate(option_rects):
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, pygame.Color("yellow"), rect.inflate(10, 10), 2)
            screen.blit(text, rect)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for i, (text, rect) in enumerate(option_rects):
                    if rect.collidepoint(pos):
                        return options[i][0]  # zwraca pierwszą literę opcji (1, 2, 3, 4)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return '1'
                elif event.key == pygame.K_2:
                    return '2'
                elif event.key == pygame.K_3:
                    return '3'
                elif event.key == pygame.K_4:
                    return '4'

def end_screen(screen, result, winner, white_time, black_time, SQUARE_SIZE, width, height, WHITE, BLACK):
    font = pygame.font.Font(None, 36)
    pygame.draw.rect(screen, BLACK, pygame.Rect(SQUARE_SIZE*8, 0, 200, SQUARE_SIZE*8))
    result_text = font.render(result, True, WHITE)
    winner_text = font.render(f"Zwycięzca: {winner}", True, WHITE)
    white_time_label = font.render("Czas białego gracza:", True, WHITE)
    white_time_value = font.render(format_time(white_time), True, WHITE)
    black_time_label = font.render("Czas czarnego gracza:", True, WHITE)
    black_time_value = font.render(format_time(black_time), True, WHITE)
    exit_text = font.render("Wyjście do menu", True, pygame.Color("yellow"))
    screen.blit(result_text, (SQUARE_SIZE*8+10, SQUARE_SIZE*2))
    screen.blit(winner_text, (SQUARE_SIZE*8+10, SQUARE_SIZE*3))
    screen.blit(white_time_label, (SQUARE_SIZE*8+10, SQUARE_SIZE*4))
    screen.blit(white_time_value, (SQUARE_SIZE*8+10, SQUARE_SIZE*4+30))
    screen.blit(black_time_label, (SQUARE_SIZE*8+10, SQUARE_SIZE*5))
    screen.blit(black_time_value, (SQUARE_SIZE*8+10, SQUARE_SIZE*5+30))
    screen.blit(exit_text, (8*SQUARE_SIZE+10, height-50))
    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if pos[0]> SQUARE_SIZE*8 and pos[1] >= height-80:
                    return

# Funkcja główna
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))  # Listen on all network interfaces
    server.listen(1)  # Allow 1 client
    print("Waiting for opponent...")

    conn, addr = server.accept()
    print(f"Connected to {addr}")

    pygame.init()
    # Ładowanie konfiguracji
    config = load_config()
    resolution = config["resolution"]
    width, height = map(int, resolution.split('x'))
    SQUARE_SIZE = height // 8
    print(width, height, SQUARE_SIZE)
    # Ustawienia ekranu
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Chess Game")
    icon_logo = pygame.image.load('program_logo.png')
    pygame.display.set_icon(icon_logo)

    # Kolory
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (100, 100, 100)
    YELLOW = pygame.Color("yellow")
    HIGHLIGHT_MOVES = (100, 200, 100)
    HIGHLIGHT_TAKES = (147, 168, 50)

    # Czcionka
    font = pygame.font.Font(None, 36)

    # Ładowanie ikon figur
    icon_type = config["icons"]
    pieces_short = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    pieces = {}
    for piece in pieces_short:
        pieces[piece] = pygame.transform.scale(pygame.image.load("pieces/" + icon_type + "/" + piece + ".png"), (SQUARE_SIZE-10, SQUARE_SIZE-10))
    
    running = True
    main_board = Board()
    turn = 'w'
    selected_piece = None
    clock = pygame.time.Clock()

    # Teksty interfejsu
    texts = ((font.render(f"Kolejka: białe", True, WHITE),(8*SQUARE_SIZE+10, 10)),
            (font.render(f"Kolejka: czarne", True, WHITE), (8*SQUARE_SIZE+10, 10)),
            (font.render(f"Wyjście", True, GRAY), (8*SQUARE_SIZE+10, height-50)))
    check_text = font.render("Szach!", True, pygame.Color("red"))

    # Czasy graczy
    start_time = time.time()
    black_time = 0
    white_time = 0
    result = ""
    winner = ""
    in_check = None
    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            elif turn=='b':
                received = conn.recv(1024).decode()
                received = received.split(' ')
                selected_piece = (int(received[0]), int(received[1]))
                row = int(received[2])
                col = int(received[3])
                if tryMove(turn, main_board, selected_piece[0], selected_piece[1], row, col):
                    draw_board(screen,SQUARE_SIZE,main_board,main_board.incheck)
                    draw_pieces(screen, main_board, SQUARE_SIZE, pieces)
                    move_time = time.time() - start_time
                    if turn == 'w':
                        white_time += move_time
                    else:
                        black_time += move_time
                    turn = 'w' if turn == 'b' else 'b'
                    
                    #sprawdzanie co po ruchu
                    if selected_piece!=None:
                        whatAfter, yForPromotion, xForPromotion = afterMove(turn,main_board, selected_piece[0], selected_piece[1], row, col)
                        if whatAfter == "promotion":
                            choiceOfPromotion = received[4]
                            promotion(yForPromotion, xForPromotion, main_board, choiceOfPromotion)
                            whatAfter, yForPromotion, xForPromotion = afterMove(turn, main_board, selected_piece[0], selected_piece[1], row, col)
                        if whatAfter == "checkmate":
                            result = "Szach Mat!"
                            winner = "Białas" if turn == 'b' else "Czarnuch"
                            running = False
                        elif whatAfter == "stalemate":
                            result = "Pat"
                            winner = "Remis"
                            running = False
                        elif whatAfter == "check":
                            in_check = turn
                        else:
                            in_check = None
                    selected_piece = None
                    start_time = time.time()
            elif event.type == pygame.MOUSEBUTTONDOWN and turn=='w':
                pos = pygame.mouse.get_pos()
                print(pos)
                col = 7 - (pos[0] // SQUARE_SIZE)
                row = 7 - (pos[1] // SQUARE_SIZE)
                if col < 8 and row < 8:
                    if selected_piece:
                        if tryMove(turn, main_board, selected_piece[0], selected_piece[1], row, col):
                            draw_board(screen,SQUARE_SIZE,main_board,main_board.incheck)
                            draw_pieces(screen, main_board, SQUARE_SIZE, pieces)
                            move_time = time.time() - start_time
                            if turn == 'w':
                                white_time += move_time
                            else:
                                black_time += move_time
                            turn = 'w' if turn == 'b' else 'b'
                            
                            #sprawdzanie co po ruchu
                            if selected_piece!=None:
                                whatAfter, yForPromotion, xForPromotion = afterMove(turn,main_board, selected_piece[0], selected_piece[1], row, col)
                                to_send = str(selected_piece[0])+ " " + str(selected_piece[1]) + " " + str(row)+ " " +str(col)
                                if whatAfter == "promotion":
                                    choiceOfPromotion = promotion_dialog(screen, SQUARE_SIZE, turn)
                                    promotion(yForPromotion, xForPromotion, main_board, choiceOfPromotion)
                                    whatAfter, yForPromotion, xForPromotion = afterMove(turn, main_board, selected_piece[0], selected_piece[1], row, col)
                                    to_send = to_send + " " + choiceOfPromotion
                                conn.send(to_send)
                                if whatAfter == "checkmate":
                                    result = "Szach Mat!"
                                    winner = "Białas" if turn == 'b' else "Czarnuch"
                                    running = False
                                elif whatAfter == "stalemate":
                                    result = "Pat"
                                    winner = "Remis"
                                    running = False
                                elif whatAfter == "check":
                                    in_check = turn
                                else:
                                    in_check = None
                            selected_piece = None
                            start_time = time.time()
                        else:
                            selected_piece = (row, col)
                    else:
                        selected_piece = (row, col)
                if pos[0]> SQUARE_SIZE*8 and pos[0]<= width-20 and pos[1] >= height-80:
                    running = False
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Aktualizacja czasu gracza na żywo
        current_time = time.time()
        if turn == 'w':
            current_white_time = white_time + (current_time - start_time)
            current_black_time = black_time
        else:
            current_black_time = black_time + (current_time - start_time)
            current_white_time = white_time

        player_times_font = ((font.render(format_time(current_white_time), True, YELLOW if turn=='w' else GRAY),(8*SQUARE_SIZE+10,height - 150)),
                             (font.render(format_time(current_black_time), True, YELLOW if turn=='b' else GRAY),(8*SQUARE_SIZE+10,80)))
        screen.fill(BLACK)
        draw_board(screen, SQUARE_SIZE, main_board, in_check)
        draw_interface(screen, turn, SQUARE_SIZE,BLACK, texts, player_times_font, in_check, check_text)
        try:
            if config["highlight"] or main_board.get_piece(selected_piece[0],selected_piece[1])[0] == turn:
                highlight_moves(screen, main_board.board_state[selected_piece[0]][selected_piece[1]],SQUARE_SIZE,main_board,  HIGHLIGHT_MOVES, HIGHLIGHT_TAKES)
        except TypeError:
            pass
        except AttributeError:
            pass
        draw_pieces(screen, main_board, SQUARE_SIZE, pieces)
        pygame.display.flip()
        clock.tick(60)
    
    end_screen(screen, result, winner, white_time, black_time, SQUARE_SIZE, width, height, WHITE, BLACK)
    conn.close()
    server.close()
    return
if __name__ == "__main__":

    main()
