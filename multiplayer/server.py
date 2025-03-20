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




def setup_server():
    """
    Tworzy i konfiguruje serwer nasłuchujący na porcie 5555.
    Oczekuje na połączenie klienta i zwraca obiekt serwera oraz połączenie.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))  # Listen on all network interfaces
    server.listen(1)  # Allow 1 client
    print("Waiting for opponent...")
    conn, addr = server.accept()
    print(f"Connected to {addr}")
    return server, conn

def handle_disconnect(conn, server):
    """
    Obsługuje rozłączenie klienta i zamyka serwer.
    
    Args:
        conn: Obiekt połączenia z klientem.
        server: Obiekt serwera.
    """
    to_send = "disconnect"
    conn.send(to_send.encode())
    conn.close()
    server.close()

def receive_move(conn):
    """
    Odbiera ruch od klienta.
    
    Args:
        conn: Obiekt połączenia z klientem.
    
    Returns:
        Lista zawierająca dane ruchu lub None, jeśli klient się rozłączył.
    """
    received = conn.recv(1024).decode()
    if received == "disconnect":
        return None
    return received.split(' ')

def send_move(conn, move_data):
    """
    Wysyła dane ruchu do klienta.
    
    Args:
        conn: Obiekt połączenia z klientem.
        move_data: Dane ruchu w formacie tekstowym.
    """
    conn.send(move_data.encode())

def get_server_ip_and_port():
    """
    Pobiera adres IP i port serwera.
    
    Returns:
        Tuple zawierający adres IP i port serwera.
    """
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    port = 5555  # Default port
    return ip_address, port

def server_communication(conn, communication_data, running_flag):
    """
    Obsługuje komunikację serwera w osobnym wątku.
    
    Args:
        conn: Obiekt połączenia z klientem.
        communication_data: Słownik przechowujący dane komunikacji.
        running_flag: Obiekt threading.Event do kontrolowania stanu gry.
    """
    while running_flag.is_set():
        try:
            if communication_data["to_receive"]:  # Oczekiwanie na ruch przeciwnika
                received = conn.recv(1024).decode()
                if received == "disconnect":
                    running_flag.clear()
                    break
                communication_data["received"] = received
                communication_data["to_receive"] = False
            elif communication_data["to_send"]:  # Wysyłanie ruchu do klienta
                conn.send(communication_data["to_send"].encode())
                communication_data["to_send"] = None
                communication_data["to_receive"] = True
        except (ConnectionResetError, OSError):
            running_flag.clear()
            break

# Funkcja główna
def main():
    """
    Główna funkcja gry serwera. Inicjalizuje serwer, obsługuje logikę gry
    oraz interfejs graficzny.
    """
    server, conn = setup_server()

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
    communication_data = {"to_send": None, "received": None, "to_receive": True}

    # Uruchomienie wątku komunikacji serwera
    communication_thread = threading.Thread(target=server_communication, args=(conn, communication_data, running_flag))
    communication_thread.start()

    main_board = Board()
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
                handle_disconnect(conn, server)
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and communication_data["to_receive"]:
                pos = pygame.mouse.get_pos()
                col = 7 - (pos[0] // SQUARE_SIZE)
                row = 7 - (pos[1] // SQUARE_SIZE)
                if col < 8 and row < 8:
                    if selected_piece:
                        if tryMove('w', main_board, selected_piece[0], selected_piece[1], row, col):
                            to_send = f"{selected_piece[0]} {selected_piece[1]} {row} {col}"
                            communication_data["to_send"] = to_send
                            selected_piece = None
                        else:
                            selected_piece = (row, col)
                    else:
                        selected_piece = (row, col)
                if pos[0]> SQUARE_SIZE*8 and pos[0]<= width-20 and pos[1] >= height-80:
                    running = False
                    running_flag.clear()
                    communication_thread.join()
                    handle_disconnect(conn, server)
                    return

        if communication_data["received"] and not communication_data["to_receive"]:
            received = communication_data["received"].split(' ')
            selected_piece = (int(received[0]), int(received[1]))
            row, col = int(received[2]), int(received[3])
            if tryMove('b', main_board, selected_piece[0], selected_piece[1], row, col):
                # sprawdzanie co po ruchu
                if selected_piece is not None:
                    whatAfter, yForPromotion, xForPromotion = afterMove('b', main_board, selected_piece[0], selected_piece[1], row, col)
                    if whatAfter == "promotion":
                        choiceOfPromotion = received[4]
                        promotion(yForPromotion, xForPromotion, main_board, choiceOfPromotion)
                        whatAfter, yForPromotion, xForPromotion = afterMove('b', main_board, selected_piece[0], selected_piece[1], row, col)
                    if whatAfter == "checkmate":
                        result = "Szach Mat!"
                        winner = "Białas"
                        running = False
                    elif whatAfter == "stalemate":
                        result = "Pat"
                        winner = "Remis"
                        running = False
                    elif whatAfter == "check":
                        in_check = 'b'
                    else:
                        in_check = None
                selected_piece = None
                start_time = time.time()
            communication_data["received"] = None

        # Aktualizacja czasu gracza na żywo
        current_time = time.time()
        if communication_data["to_receive"]:
            current_white_time = white_time + (current_time - start_time)
            current_black_time = black_time
        else:
            current_black_time = black_time + (current_time - start_time)
            current_white_time = white_time

        player_times_font = ((font.render(format_time(current_white_time), True, YELLOW if communication_data["to_receive"] else GRAY),
                              (8 * SQUARE_SIZE + 10, height - 150)),
                             (font.render(format_time(current_black_time), True, YELLOW if not communication_data["to_receive"] else GRAY),
                              (8 * SQUARE_SIZE + 10, 80)))
        screen.fill(BLACK)
        draw_board(screen, SQUARE_SIZE, main_board, in_check)
        draw_interface(screen, 'w' if communication_data["to_receive"] else 'b', SQUARE_SIZE, BLACK, texts, player_times_font, in_check, check_text)
        try:
            if config["highlight"] or main_board.get_piece(selected_piece[0], selected_piece[1])[0] == 'w':
                highlight_moves(screen, main_board.board_state[selected_piece[0]][selected_piece[1]], SQUARE_SIZE,
                                main_board, HIGHLIGHT_MOVES, HIGHLIGHT_TAKES)
        except (TypeError, AttributeError):
            pass
        draw_pieces(screen, main_board, SQUARE_SIZE, pieces)
        pygame.display.flip()
        clock.tick(60)
    
    end_screen(screen, result, winner, white_time, black_time, SQUARE_SIZE, width, height, WHITE, BLACK)
    handle_disconnect(conn, server)
    return
if __name__ == "__main__":
    ip, port = get_server_ip_and_port()
    print(f"Server running on IP: {ip}, Port: {port}")
    main()
