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
from algorithms.evaluation import get_evaluation  # Import evaluation function
from nerd_view import *


def start_server():
    """Tworzy serwer, akceptuje jedno połączenie i kończy działanie wątku."""
    global server, conn, addr, client_connected, client_ip
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(1)
    print("🔵 Serwer czeka na połączenie...")
    
    conn, addr = server.accept()
    client_ip = addr[0]  # Get client IP address
    print(f"🟢 Połączono z {client_ip}")
    client_connected = True  # Informujemy główną pętlę, że można rozpocząć grę

def disconnect():
    global server, conn, addr, client_connected
    conn.sendall("exit".encode('utf-8'))
    conn.close()
    server.close()
    client_connected = False
def force_quit():
    global server, conn
    try:
        conn.close()
        server.close()
    except:
        None
    """Wyłącza sockety, bez powiadamiania klienta
    """

def get_server_ip():
    """
    Pobiera adres IP serwera.

    Returns:
        str: Adres IP serwera.
    """
    hostname = socket.gethostname()
    server_ip = socket.gethostbyname(hostname)
    return server_ip


def waiting_screen(screen, font, server_ip):
    """
    Elegancki ekran oczekiwania na klienta z animacją i kodem IP.
    """
    global start_time
    
    # Create fonts
    title_font = pygame.font.Font(None, 48)
    info_font = pygame.font.Font(None, 36)
    ip_font = pygame.font.Font(None, 72)
    
    # Colors
    BACKGROUND = (32, 32, 32)
    TEXT_COLOR = (255, 255, 255)
    GOLD = (255, 215, 0)
    BUTTON_COLOR = (60, 60, 60)
    BUTTON_HOVER = (80, 80, 80)
    
    # Create cancel button
    cancel_button = pygame.Rect(screen.get_width() // 2 - 100, 600, 200, 50)
    
    clock = pygame.time.Clock()
    animation_frame = 0
    dots = ""
    
    while not client_connected:
        screen.fill(BACKGROUND)
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                force_quit
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if cancel_button.collidepoint(mouse_pos):
                    force_quit()
                    return False
                
        # Draw title
        title = title_font.render("Oczekiwanie na przeciwnika", True, GOLD)
        title_rect = title.get_rect(center=(screen.get_width() // 2, 150))
        screen.blit(title, title_rect)
        
        # Draw IP box
        pygame.draw.rect(screen, (45, 45, 45), (screen.get_width() // 2 - 200, 250, 400, 100))
        pygame.draw.rect(screen, GOLD, (screen.get_width() // 2 - 200, 250, 400, 100), 2)
        
        # Draw IP text
        ip_text = ip_font.render(server_ip, True, TEXT_COLOR)
        ip_rect = ip_text.get_rect(center=(screen.get_width() // 2, 300))
        screen.blit(ip_text, ip_rect)
        
        # Draw info text
        info_text = info_font.render("Podaj ten kod drugiemu graczowi", True, (200, 200, 200))
        info_rect = info_text.get_rect(center=(screen.get_width() // 2, 400))
        screen.blit(info_text, info_rect)
        
        # Animate waiting dots
        dots = "." * ((animation_frame // 15) % 4)
        waiting_text = info_font.render(f"Oczekiwanie{dots}", True, GOLD)
        waiting_rect = waiting_text.get_rect(center=(screen.get_width() // 2, 500))
        screen.blit(waiting_text, waiting_rect)
        
        # Draw cancel button with hover effect
        button_color = BUTTON_HOVER if cancel_button.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, button_color, cancel_button)
        pygame.draw.rect(screen, GOLD, cancel_button, 2)
        
        cancel_text = info_font.render("Anuluj", True, TEXT_COLOR)
        cancel_rect = cancel_text.get_rect(center=cancel_button.center)
        screen.blit(cancel_text, cancel_rect)
        
        pygame.display.flip()
        animation_frame = (animation_frame + 1) % 60
        clock.tick(60)
    
    start_time = time.time()
    return True

# Funkcja główna
def main():
    global conn
    global HOST, PORT, server, conn, addr, client_connected, start_time
    HOST = '0.0.0.0'
    PORT = 12345
    server = None
    conn = None
    addr = None
    client_connected = False
    start_time = None  # Inicjalizacja zmiennej start_time

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
    texts = (
        (font.render(f"Kolejka: białe", True, WHITE), (8 * SQUARE_SIZE + 10, 10)),
        (font.render(f"Kolejka: czarne", True, WHITE), (8 * SQUARE_SIZE + 10, 10)),
        (font.render(f"Wyjście", True, GRAY), (8 * SQUARE_SIZE + 10, height - 50)),
        (font.render(f"Cofnij ruch", True, GRAY), (8 * SQUARE_SIZE + 10, height - 100)),  # Dodano przycisk "Cofnij ruch"
    )
    check_text = font.render("Szach!", True, pygame.Color("red"))

    # Czasy graczy
    # start_time = time.time()
    black_time = 0
    white_time = 0
    result = ""
    winner = ""
    in_check = None
    is_reversed = True #aby czarne były na dole

    # Pobieranie adresu IP serwera
    server_ip = get_server_ip()
    ping_time = 0

    # Wyświetlamy animację oczekiwania z adresem IP
    if not waiting_screen(screen, font, server_ip):
        return

    # Po podłączeniu klienta ustawiamy timeout
    conn.settimeout(0.05)

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
    
    nerd_view = config["nerd_view"]
    if nerd_view:
        from queue import Queue
        nerd_view_queue = Queue()
        ping_nerd_view_queue = Queue()
        moves_queue = Queue()
        root = tk.Tk()
        root_network = tk.Tk()
        root_network.geometry("600x600+800+500")
        root.geometry("600x600+800+100")
        stats_window = NormalStatsWindow(root, nerd_view_queue, moves_queue)
        network_stats_window = NetworkStatsWindow(root_network, ping_nerd_view_queue, server_ip, client_ip, is_server=True)
        moves_number = sum(len(value) for value in main_board.get_all_moves(turn))        

    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                try: disconnect()
                except: pass
                try: 
                    root.destroy()
                    root_network.destroy()
                except: pass
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                print(pos)
                col = pos[0] // SQUARE_SIZE
                row = pos[1] // SQUARE_SIZE
                if col < 8 and row < 8:
                    if selected_piece and turn =='b':
                        if tryMove(turn, main_board, selected_piece[0], selected_piece[1], row, col):
                            draw_board(screen,SQUARE_SIZE,main_board,main_board.incheck, is_reversed)
                            draw_pieces(screen, main_board, SQUARE_SIZE, pieces, is_reversed)
                            pygame.display.flip()
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
                            #nerd view:
                            if nerd_view:
                                moves_number = sum(len(value) for value in main_board.get_all_moves(turn))
                                moves_queue.put(move_time)
                            start_time = time.time()
                        else:
                            selected_piece = (row, col)
                    else:
                        selected_piece = (row, col)
                if pos[0]> SQUARE_SIZE*8 and pos[0]<= width-20 and pos[1] >= height-80:
                    try: disconnect()
                    except: pass
                    try: 
                        root.destroy()
                        root_network.destroy()
                    except: pass
                    running = False
                    return
                # Obsługa przycisku "Cofnij ruch"
                if pos[0] > SQUARE_SIZE * 8 and pos[0] <= width - 20 and height - 100 <= pos[1] < height - 80:
                    if request_undo(screen, SQUARE_SIZE):
                        conn.sendall("undo_request".encode('utf-8'))
                        print("📤 Wysłano żądanie cofnięcia ruchu.")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        try:
            data = conn.recv(1024).decode('utf-8')
            if data:
                if data.startswith("exit") :
                    running = False
                    result = "Disconnected"
                    winner = "You"
                    break
                elif data.startswith("undo_request"):
                    if confirm_undo_dialog(screen, SQUARE_SIZE):
                        conn.sendall("undo_confirm".encode('utf-8'))
                        undoMove(main_board)
                        turn = 'w' if turn == 'b' else 'b'
                        print("✅ Cofnięto ruch.")
                        start_time = time.time()
                    else:
                        conn.sendall("undo_reject".encode('utf-8'))
                elif data.startswith("undo_confirm"):
                    undoMove(main_board)
                    turn = 'w' if turn == 'b' else 'b'
                    print("✅ Cofnięto ruch.")
                    start_time = time.time()
                elif data.startswith("undo_reject"):
                    print("❌ Cofnięcie ruchu zostało odrzucone.")
                elif data.startswith("ping"):
                    conn.sendall("pong".encode('utf-8'))
                elif data.startswith("ptime"):
                    ping_time = data.split(' ')[1]
                    ping_time = float(ping_time[:4])
                    print(f"Ping: {ping_time:.2f} ms")
                else:
                    data = data.split()
                    selected_piece = (int(data[0]), int(data[1]))
                    row = int(data[2])
                    col = int(data[3])
                    if tryMove(turn, main_board, selected_piece[0], selected_piece[1], row, col):
                        draw_board(screen,SQUARE_SIZE,main_board,main_board.incheck, is_reversed)
                        draw_pieces(screen, main_board, SQUARE_SIZE, pieces, is_reversed)
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
                        #nerd view:
                        if nerd_view:
                            moves_number = sum(len(value) for value in main_board.get_all_moves(turn))
                            moves_queue.put(move_time)
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

        evaluation = get_evaluation(main_board, turn)[0] - get_evaluation(main_board, turn)[1]  # Calculate evaluation

        player_times_font = ((font.render(format_time(current_white_time), True, YELLOW if turn == 'w' else GRAY), 
                              (8 * SQUARE_SIZE + 10, height - 150)),
                             (font.render(format_time(current_black_time), True, YELLOW if turn == 'b' else GRAY), 
                              (8 * SQUARE_SIZE + 10, 80)))
        screen.fill(BLACK)
        draw_board(screen, SQUARE_SIZE, main_board, in_check, is_reversed)
        draw_interface(screen, turn, SQUARE_SIZE, BLACK, texts, player_times_font, in_check, check_text, evaluation=evaluation, ping = ping_time)
        try:
            if config["highlight_enemy"] or main_board.get_piece(selected_piece[0],selected_piece[1])[0] == 'b':
                highlight_moves(screen, main_board.board_state[selected_piece[0]][selected_piece[1]],SQUARE_SIZE,main_board,  HIGHLIGHT_MOVES, HIGHLIGHT_TAKES, is_reversed)
        except TypeError:
            pass
        except AttributeError:
            pass
        draw_pieces(screen, main_board, SQUARE_SIZE, pieces, is_reversed)
        pygame.display.flip()
        clock.tick(60)

        #nerd view
        if nerd_view:
            current_time_for_stats = time.time()
            evaluation = get_evaluation(main_board)
            evaluation = evaluation[0] - evaluation[1]
            nerd_view_queue.put((current_time_for_stats, evaluation, moves_number))
            root.update()
    
    end_screen(screen, result, winner, white_time, black_time, SQUARE_SIZE, width, height, WHITE, BLACK)
    try:disconnect()
    except:pass
    try: 
        root.destroy()
        root_network.destroy()
    except: pass
    return
if __name__ == "__main__":

    main()
