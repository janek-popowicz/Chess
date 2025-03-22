
# SERWER JEST CZARNY A KLIENT BIAŁY
import pygame
import time
import socket
import threading
#wygląda dziwnie ale musi działać
from engine.board_and_fields import *
from engine.engine import *
from engine.figures import *
from engine.fen_operations import *
from graphics import *



def start_server():
    """Tworzy serwer, akceptuje jedno połączenie i kończy działanie wątku."""
    global server, conn, addr, client_connected
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print("🔵 Serwer czeka na połączenie...")
    
    conn, addr = server.accept()
    print(f"🟢 Połączono z {addr}")
    client_connected = True  # Informujemy główną pętlę, że można rozpocząć grę

def disconnect():
    global server, conn, addr, client_connected
    conn.sendall("exit".encode('utf-8'))
    conn.close()
    server.close()
    client_connected = False


def waiting_screen(screen, font):
    """Animacja oczekiwania na klienta"""
    dots = ""
    clock = pygame.time.Clock()
    while not client_connected:
        screen.fill((0, 0, 0))
        text = font.render(f"Oczekiwanie na gracza{dots}", True, (255, 255, 255))
        screen.blit(text, (250, 300))
        pygame.display.flip()

        # Zmieniamy ilość kropek w animacji
        dots = "." * ((len(dots) + 1) % 4)

        # Unikamy 100% użycia CPU
        time.sleep(0.5)
        clock.tick(10)


# Funkcja główna
def main():
    global conn
    global HOST, PORT, server, conn, addr, client_connected
    HOST = '0.0.0.0'
    PORT = 12345
    server = None
    conn = None
    addr = None
    client_connected = False

    # Tworzymy wątek serwera (działa w tle)
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

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

    # Wyświetlamy animację oczekiwania
    waiting_screen(screen, font)

    # Po podłączeniu klienta ustawiamy timeout
    conn.settimeout(0.1)

    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                disconnect()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                print(pos)
                col = 7 - (pos[0] // SQUARE_SIZE)
                row = 7 - (pos[1] // SQUARE_SIZE)
                if col < 8 and row < 8:
                    if selected_piece and turn =='b':
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
                                message = str(selected_piece[0])+" "+str(selected_piece[1])+" "+str(row)+" "+str(col)
                                if whatAfter == "promotion":
                                    choiceOfPromotion = promotion_dialog(screen, SQUARE_SIZE, turn)
                                    promotion(yForPromotion, xForPromotion, main_board, choiceOfPromotion)
                                    message = message + " " + choiceOfPromotion
                                    whatAfter, yForPromotion, xForPromotion = afterMove(turn, main_board, selected_piece[0], selected_piece[1], row, col)
                                conn.sendall(message.encode('utf-8'))
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
        try:
            data = conn.recv(1024).decode('utf-8')
            if data:
                if data == "exit":
                    running = False
                    result = "Disconnected"
                    winner = "You"
                data = data.split()
                selected_piece = (int(data[0]), int(data[1]))
                row = int(data[2])
                col = int(data[3])
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
                            choiceOfPromotion = data[4]
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
                data = None
        except socket.timeout:
            pass

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
            if config["highlight_enemy"] or main_board.get_piece(selected_piece[0],selected_piece[1])[0] == turn:
                highlight_moves(screen, main_board.board_state[selected_piece[0]][selected_piece[1]],SQUARE_SIZE,main_board,  HIGHLIGHT_MOVES, HIGHLIGHT_TAKES)
        except TypeError:
            pass
        except AttributeError:
            pass
        draw_pieces(screen, main_board, SQUARE_SIZE, pieces)
        pygame.display.flip()
        clock.tick(60)
    
    end_screen(screen, result, winner, white_time, black_time, SQUARE_SIZE, width, height, WHITE, BLACK)
    disconnect()
    return
if __name__ == "__main__":

    main()
