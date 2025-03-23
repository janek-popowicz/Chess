import pygame
import time
import socket
import threading
from engine.board_and_fields import *
from engine.engine import *
from engine.figures import *
from graphics import *

server_connected_event = threading.Event()  # Zamiast zmiennej server_connected

def disconnect():
    global client
    client.sendall("exit".encode('utf-8'))
    client.close()

def connect_to_server():
    """Próbuje połączyć się z serwerem i kończy działanie wątku po sukcesie."""
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    while not server_connected_event.is_set():  # Sprawdzamy, czy połączenie zostało nawiązane
        try:
            print("🔵 Próba połączenia z serwerem...")
            client.connect((HOST, PORT))
            print("🟢 Połączono z serwerem!")
            server_connected_event.set()  # Ustawiamy flagę, że połączenie zostało nawiązane
        except (socket.error, ConnectionRefusedError):
            time.sleep(0.1)  # Skracamy czas oczekiwania na kolejną próbę

def connect_to_server_with_timeout(host, port, timeout=3):
    """
    Próbuje połączyć się z serwerem w określonym czasie.

    Args:
        host (str): Adres IP serwera.
        port (int): Port serwera.
        timeout (int): Maksymalny czas oczekiwania na połączenie w sekundach.

    Returns:
        socket.socket: Połączone gniazdo, jeśli połączenie się powiedzie.
        None: Jeśli połączenie nie zostanie nawiązane w określonym czasie.
    """
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(timeout)
        client_socket.connect((host, port))
        return client_socket
    except (socket.timeout, ConnectionRefusedError):
        return None

def ip_input_screen(screen, font):
    """
    Wyświetla ekran wejściowy do wpisania adresu IP serwera.

    Args:
        screen (pygame.Surface): Powierzchnia ekranu gry.
        font (pygame.Font): Czcionka do renderowania tekstu.

    Returns:
        str: Wpisany adres IP.
    """
    input_active = True
    ip_address = ""
    clock = pygame.time.Clock()

    while input_active:
        screen.fill((0, 0, 0))
        prompt_text = font.render("Wpisz adres IP serwera:", True, (255, 255, 255))
        input_text = font.render(ip_address, True, (255, 255, 255))
        screen.blit(prompt_text, (250, 200))
        screen.blit(input_text, (250, 300))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                disconnect()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Zatwierdzenie adresu IP
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:  # Usuwanie znaków
                    ip_address = ip_address[:-1]
                else:
                    ip_address += event.unicode  # Dodawanie znaków

        clock.tick(30)

    return ip_address

def waiting_screen(screen, font):
    """Animacja łączenia się z serwerem."""
    dots = ""
    clock = pygame.time.Clock()
    while not server_connected_event.is_set():  # Sprawdzamy flagę zamiast zmiennej
        screen.fill((0, 0, 0))
        text = font.render(f"Łączenie z serwerem{dots}", True, (255, 255, 255))
        screen.blit(text, (250, 300))
        pygame.display.flip()

        dots = "." * ((len(dots) + 1) % 4)
        clock.tick(30)  # Ograniczamy liczbę odświeżeń do 30 FPS

def request_undo(screen, SQUARE_SIZE):
    """
    Wyświetla okno dialogowe z pytaniem, czy gracz chce cofnąć ruch.

    Args:
        screen (pygame.Surface): Powierzchnia ekranu gry.
        SQUARE_SIZE (int): Rozmiar pojedynczego pola na szachownicy.

    Returns:
        bool: True, jeśli gracz chce cofnąć ruch, False w przeciwnym razie.
    """
    return confirm_undo_dialog(screen, SQUARE_SIZE)

# Funkcja główna
def main():
    global HOST, PORT, client
    PORT = 12345
    client = None

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

    # Czcionka
    font = pygame.font.Font(None, 36)

    # Pętla do wpisywania adresu IP i próby połączenia
    while True:
        HOST = ip_input_screen(screen, font)
        client = connect_to_server_with_timeout(HOST, PORT)
        if client:
            print("🟢 Połączono z serwerem!")
            break
        else:
            # Wyświetlenie komunikatu o błędzie
            error_text = font.render("Nie udało się połączyć z serwerem. Spróbuj ponownie.", True, (255, 0, 0))
            screen.fill((0, 0, 0))
            screen.blit(error_text, (250, 300))
            pygame.display.flip()
            pygame.time.wait(2000)  # Wyświetl komunikat przez 2 sekundy

    client.settimeout(0.05)

    # Kolory
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (100, 100, 100)
    YELLOW = pygame.Color("yellow")
    HIGHLIGHT_MOVES = (100, 200, 100)
    HIGHLIGHT_TAKES = (147, 168, 50)

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
    texts = (
        (font.render(f"Kolejka: białe", True, WHITE), (8 * SQUARE_SIZE + 10, 10)),
        (font.render(f"Kolejka: czarne", True, WHITE), (8 * SQUARE_SIZE + 10, 10)),
        (font.render(f"Wyjście", True, GRAY), (8 * SQUARE_SIZE + 10, height - 50)),
        (font.render(f"Cofnij ruch", True, GRAY), (8 * SQUARE_SIZE + 10, height - 100)),  # Dodano przycisk "Cofnij ruch"
    )
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
                disconnect()
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                print(pos)
                col = 7 - (pos[0] // SQUARE_SIZE)
                row = 7 - (pos[1] // SQUARE_SIZE)
                if col < 8 and row < 8:
                    if selected_piece and turn =='w':
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
                                client.sendall(message.encode('utf-8'))
                                if whatAfter == "checkmate":
                                    result = "Szach Mat!"
                                    winner = "Ty" if turn == 'b' else "Przeciwnik"
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
                # Obsługa przycisku "Cofnij ruch"
                if pos[0] > SQUARE_SIZE * 8 and pos[0] <= width - 20 and height - 100 <= pos[1] < height - 80:
                    if request_undo(screen, SQUARE_SIZE):
                        client.sendall("undo_request".encode('utf-8'))
                        print("📤 Wysłano żądanie cofnięcia ruchu.")
                if pos[0]> SQUARE_SIZE*8 and pos[0]<= width-20 and pos[1] >= height-80: #kliknięcie wyjścia
                    disconnect()
                    running = False
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        try:
            data = client.recv(1024).decode('utf-8')
            if data:
                if data == "exit":
                    running = False
                    result = "Rozłączono"
                    winner = "Ty"
                    break
                elif data == "undo_request":
                    if confirm_undo_dialog(screen, SQUARE_SIZE):
                        client.sendall("undo_confirm".encode('utf-8'))
                        undoMove(main_board)
                        turn = 'w' if turn == 'b' else 'b'
                        print("✅ Cofnięto ruch.")
                        start_time = time.time()
                    else:
                        client.sendall("undo_reject".encode('utf-8'))
                elif data == "undo_confirm":
                    undoMove(main_board)
                    turn = 'w' if turn == 'b' else 'b'
                    print("✅ Cofnięto ruch.")
                    start_time = time.time()
                elif data == "undo_reject":
                    print("❌ Cofnięcie ruchu zostało odrzucone.")
                else:
                    print(f"📩 Otrzymano ruch: {data}")
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
            if turn == 'w' and (config["highlight_enemy"] or main_board.get_piece(selected_piece[0],selected_piece[1])[0] == turn):
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
