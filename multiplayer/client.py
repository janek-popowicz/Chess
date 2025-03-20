import pygame
import sys
import json
import time
import os
import socket
import threading

#wygląda dziwnie ale musi działać
from engine.board_and_fields import *
from engine.engine import *
from engine.figures import *
from graphics import *


def setup_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((input("podaj adres ip serwera"), 5555))  # Connect to the server
    return client

def handle_disconnect(client):
    to_send = "disconnect"
    client.send(to_send.encode())
    client.close()

def receive_move(client):
    received = client.recv(1024).decode()
    if received == "disconnect":
        return None
    return received.split(' ')

def send_move(client, move_data):
    client.send(move_data.encode())

def client_communication(client, main_board, turn_data, running_flag):
    """
    Obsługuje komunikację klienta w osobnym wątku.
    
    Args:
        client: Obiekt klienta.
        main_board: Obiekt planszy gry.
        turn_data: Słownik przechowujący informacje o turze.
        running_flag: Obiekt threading.Event do kontrolowania stanu gry.
    """
    while running_flag.is_set():
        try:
            if turn_data["turn"] == 'w':  # Oczekiwanie na ruch przeciwnika
                received = client.recv(1024).decode()
                if received == "disconnect":
                    running_flag.clear()
                    break
                move = received.split(' ')
                selected_piece = (int(move[0]), int(move[1]))
                row, col = int(move[2]), int(move[3])
                if tryMove('w', main_board, selected_piece[0], selected_piece[1], row, col):
                    turn_data["last_move"] = (selected_piece, row, col)
                    turn_data["turn"] = 'b'
        except (ConnectionResetError, OSError):
            running_flag.clear()
            break

# Funkcja główna
def main():
    client = setup_client()

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
    running_flag = threading.Event()
    running_flag.set()
    turn_data = {"turn": 'b', "last_move": None}
    main_board = Board()

    # Uruchomienie wątku komunikacji klienta
    communication_thread = threading.Thread(target=client_communication, args=(client, main_board, turn_data, running_flag))
    communication_thread.start()

    turn = 'b'
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
                running_flag.clear()
                communication_thread.join()
                handle_disconnect(client)
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and turn_data["turn"] == 'b':
                pos = pygame.mouse.get_pos()
                print(pos)
                col = 7 - (pos[0] // SQUARE_SIZE)
                row = 7 - (pos[1] // SQUARE_SIZE)
                if col < 8 and row < 8:
                    if selected_piece:
                        if tryMove('b', main_board, selected_piece[0], selected_piece[1], row, col):
                            to_send = f"{selected_piece[0]} {selected_piece[1]} {row} {col}"
                            client.send(to_send.encode())
                            turn_data["turn"] = 'w'
                            selected_piece = None
                        else:
                            selected_piece = (row, col)
                    else:
                        selected_piece = (row, col)
                if pos[0] > SQUARE_SIZE * 8 and pos[0] <= width - 20 and pos[1] >= height - 80:
                    running = False
                    running_flag.clear()
                    communication_thread.join()
                    handle_disconnect(client)
                    return

        # Aktualizacja planszy po ruchu przeciwnika
        if turn_data["last_move"] and turn_data["turn"] == 'b':
            selected_piece, row, col = turn_data["last_move"]
            draw_board(screen, SQUARE_SIZE, main_board, main_board.incheck)
            draw_pieces(screen, main_board, SQUARE_SIZE, pieces)
            turn_data["last_move"] = None

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
                highlight_moves(screen, main_board.board_state[selected_piece[0]][selected_piece[1]],SQUARE_SIZE,main_board,  HIGHLIGHT_MOVES, HIGHLIGHT_TAKES,config["highlight"])
        except TypeError:
            pass
        except AttributeError:
            pass
        draw_pieces(screen, main_board, SQUARE_SIZE, pieces)
        pygame.display.flip()
        clock.tick(60)
    
    end_screen(screen, result, winner, white_time, black_time, SQUARE_SIZE, width, height, WHITE, BLACK)
    handle_disconnect(client)
    return
if __name__ == "__main__":
    main()
