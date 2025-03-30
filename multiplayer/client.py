import pygame
import time
import socket
import threading
from engine.board_and_fields import *
from engine.engine import *
from engine.figures import *
from graphics import *
from algorithms.evaluation import get_evaluation  # Import evaluation function
from nerd_view import *

def get_ip() -> str:
    """
    Retrieves the IP address of the current machine.

    This function uses the system's hostname to determine the IP address
    of the machine on which it is executed.

    Returns:
        str: The IP address of the current machine.
    """
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip
    

server_connected_event = threading.Event()  # Event to signal server connection status.

def disconnect() -> None:
    """
    Disconnects the client from the server.

    This function sends an "exit" message to the server and closes the socket connection.
    It ensures a clean disconnection from the server.
    """
    global client
    client.sendall("exit".encode('utf-8'))
    client.close()

def force_quit() -> None:
    """
    Forces the client to close the connection.

    This function closes the socket connection without sending any message to the server.
    It is used in scenarios where immediate termination is required.
    """
    global client
    client.close()

def connect_to_server() -> None:
    """
    Attempts to connect to the server in a loop until successful.

    This function creates a socket and continuously tries to establish a connection
    with the server. Once connected, it sets the `server_connected_event` to signal
    that the connection has been established.

    Raises:
        socket.error: If there is an issue with the socket connection.
        ConnectionRefusedError: If the server refuses the connection.
    """
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    while not server_connected_event.is_set():  # Check if the connection has been established
        try:
            print("🔵 Attempting to connect to the server...")
            client.connect((HOST, PORT))
            print("🟢 Connected to the server!")
            server_connected_event.set()  # Set the flag indicating the connection has been established
        except (socket.error, ConnectionRefusedError):
            time.sleep(0.1)  # Reduce the wait time for the next attempt

def connect_to_server_with_timeout(host: str, port: int, timeout: int = 3) -> socket.socket | None:
    """
    Attempts to connect to the server within a specified timeout period.

    Args:
        host (str): The IP address of the server.
        port (int): The port number of the server.
        timeout (int): Maximum time (in seconds) to wait for a connection.

    Returns:
        socket.socket: The connected socket object if successful.
        None: If the connection could not be established within the timeout period.

    Raises:
        socket.timeout: If the connection attempt exceeds the timeout.
        ConnectionRefusedError: If the server refuses the connection.
    """
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(timeout)
        client_socket.connect((host, port))
        return client_socket
    except (socket.timeout, ConnectionRefusedError):
        return None

def ip_input_screen(screen: pygame.Surface, font: pygame.font.Font) -> str | None:
    """
    Displays an elegant input screen for entering the server's IP address.

    This function creates a graphical interface using Pygame to allow the user
    to input the server's IP address. It includes buttons for connecting or canceling.

    Args:
        screen (pygame.Surface): The Pygame screen surface.
        font (pygame.Font): The font used for rendering text.

    Returns:
        str: The entered IP address if the user confirms.
        None: If the user cancels the input or closes the window.
    """
    input_active = True
    ip_address = ""
    clock = pygame.time.Clock()
    
    # Create fonts
    title_font = pygame.font.Font(None, 48)
    input_font = pygame.font.Font(None, 36)
    
    # Define colors
    BACKGROUND = (32, 32, 32)
    TEXT_COLOR = (255, 255, 255)
    ACTIVE_COLOR = (255, 215, 0)  # Gold
    INACTIVE_COLOR = (100, 100, 100)
    INPUT_BG = (45, 45, 45)
    BUTTON_COLOR = (60, 60, 60)
    
    # Create buttons
    connect_button = pygame.Rect(screen.get_width() // 2 - 200, 400, 180, 50)
    cancel_button = pygame.Rect(screen.get_width() // 2 + 20, 400, 180, 50)
    input_box = pygame.Rect(screen.get_width() // 2 - 150, 280, 300, 40)

    while input_active:
        screen.fill(BACKGROUND)
        
        # Draw title
        title = title_font.render("Połączenie z drugim graczem", True, ACTIVE_COLOR)
        title_rect = title.get_rect(center=(screen.get_width() // 2, 150))
        screen.blit(title, title_rect)
        
        # Draw subtitle
        subtitle = font.render("Wprowadź kod dołączenia:", True, TEXT_COLOR)
        subtitle_rect = subtitle.get_rect(center=(screen.get_width() // 2, 220))
        screen.blit(subtitle, subtitle_rect)
        
        # Draw input box
        pygame.draw.rect(screen, INPUT_BG, input_box)
        pygame.draw.rect(screen, ACTIVE_COLOR, input_box, 2)
        
        # Draw input text
        input_surface = input_font.render(ip_address, True, TEXT_COLOR)
        input_rect = input_surface.get_rect(center=input_box.center)
        screen.blit(input_surface, input_rect)
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        
        # Connect button
        connect_color = ACTIVE_COLOR if connect_button.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, connect_color, connect_button)
        pygame.draw.rect(screen, ACTIVE_COLOR, connect_button, 2)
        connect_text = font.render("Połącz", True, TEXT_COLOR)
        connect_rect = connect_text.get_rect(center=connect_button.center)
        screen.blit(connect_text, connect_rect)
        
        # Cancel button
        cancel_color = ACTIVE_COLOR if cancel_button.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, cancel_color, cancel_button)
        pygame.draw.rect(screen, ACTIVE_COLOR, cancel_button, 2)
        cancel_text = font.render("Anuluj", True, TEXT_COLOR)
        cancel_rect = cancel_text.get_rect(center=cancel_button.center)
        screen.blit(cancel_text, cancel_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if cancel_button.collidepoint(event.pos):
                    return None
                if connect_button.collidepoint(event.pos) and ip_address:
                    return ip_address
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and ip_address:
                    return ip_address
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    ip_address = ip_address[:-1]
                else:
                    # Only allow valid IP address characters
                    if event.unicode in "0123456789.":
                        ip_address += event.unicode

        clock.tick(60)

    return None

def waiting_screen(screen: pygame.Surface, font: pygame.font.Font) -> None:
    """
    Displays a waiting animation while attempting to connect to the server.

    This function shows a simple animation with dots to indicate that the client
    is trying to establish a connection with the server.

    Args:
        screen (pygame.Surface): The Pygame screen surface.
        font (pygame.Font): The font used for rendering text.
    """
    dots = ""
    clock = pygame.time.Clock()
    while not server_connected_event.is_set():  # Check the flag instead of a variable
        screen.fill((0, 0, 0))
        text = font.render(f"Łączenie z serwerem{dots}", True, (255, 255, 255))
        screen.blit(text, (250, 300))
        pygame.display.flip()

        dots = "." * ((len(dots) + 1) % 4)
        clock.tick(30)  # Limit refresh rate to 30 FPS

def request_undo(screen: pygame.Surface, SQUARE_SIZE: int) -> bool:
    """
    Displays a dialog box asking the player if they want to undo their move.

    Args:
        screen (pygame.Surface): The Pygame screen surface.
        SQUARE_SIZE (int): The size of a single square on the chessboard.

    Returns:
        bool: True if the player agrees to undo the move, False otherwise.
    """
    return confirm_undo_dialog(screen, SQUARE_SIZE)

def main() -> None:
    """
    The main function that initializes and runs the chess game.

    This function sets up the game environment, including the Pygame screen,
    fonts, and configurations. It handles the game loop, player interactions,
    and communication with the server.

    Global Variables:
        HOST (str): The server's IP address.
        PORT (int): The server's port number.
        client (socket.socket): The socket object for server communication.

    Raises:
        pygame.error: If there is an issue with Pygame initialization or rendering.
        socket.error: If there is an issue with server communication.
    """
    global HOST, PORT, client
    PORT = 12345
    client = None

    pygame.init()
    # Load configuration
    config = load_config()
    resolution = config["resolution"]
    nerd_view = config["nerd_view"]
    width, height = map(int, resolution.split('x'))
    SQUARE_SIZE = height // 8
    print(width, height, SQUARE_SIZE)
    # Screen settings
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Chess Game")
    icon_logo = pygame.image.load('program_logo.png')
    pygame.display.set_icon(icon_logo)

    # Font
    font = pygame.font.Font(None, 36)

    # Loop for entering IP address and attempting connection
    while True:
        HOST = ip_input_screen(screen, font)
        if HOST == None:
            return
        client = connect_to_server_with_timeout(HOST, PORT)
        if client:
            print("🟢 Connected to the server!")
            break
        else:
            # Display error message
            error_text = font.render("Nie udało się połączyć z serwerem. Spróbuj ponownie.", True, (255, 0, 0))
            screen.fill((0, 0, 0))
            screen.blit(error_text, (250, 300))
            pygame.display.flip()
            pygame.time.wait(2000)  # Display message for 2 seconds

    client.settimeout(0.05)

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (100, 100, 100)
    YELLOW = pygame.Color("yellow")
    HIGHLIGHT_MOVES = (100, 200, 100)
    HIGHLIGHT_TAKES = (147, 168, 50)

    # Load piece icons
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
    ping_time = 0

    # Interface texts
    texts = (
        (font.render(f"Kolejka: białe", True, WHITE), (8 * SQUARE_SIZE + 10, 10)),
        (font.render(f"Kolejka: czarne", True, WHITE), (8 * SQUARE_SIZE + 10, 10)),
        (font.render(f"Wyjście", True, GRAY), (8 * SQUARE_SIZE + 10, height - 50)),
        (font.render(f"Cofnij ruch", True, GRAY), (8 * SQUARE_SIZE + 10, height - 100)),  # Added "Undo Move" button
    )
    check_text = font.render("Szach!", True, pygame.Color("red"))

    ping_start_time = time.time()
    # Player times
    start_time = time.time()
    black_time = 0
    white_time = 0
    result = ""
    winner = ""
    in_check = None

    # Add ping timing variables
    last_ping_time = time.time()
    ping_interval = 2.0  # Send ping every 2 seconds
    ping_start_time = 0

    # Nerd view data:
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
        network_stats_window = NetworkStatsWindow(root_network, ping_nerd_view_queue, get_ip(), HOST, False)
        moves_number = sum(len(value) for value in main_board.get_all_moves(turn))
    
    while running:
        current_time = time.time()
        
        # Send ping every 2 seconds
        if current_time - last_ping_time >= ping_interval:
            client.sendall("ping".encode('utf-8'))
            ping_start_time = current_time
            last_ping_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                try: disconnect()
                except: pass
                try: 
                    root.destroy()
                    root_network.destroy()
                except: pass
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
                            
                            # Check after move
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
                            # Nerd view:
                            if nerd_view:
                                moves_number = sum(len(value) for value in main_board.get_all_moves(turn))
                                moves_queue.put(move_time)
                            selected_piece = None
                            start_time = time.time()
                        else:
                            selected_piece = (row, col)
                    else:
                        selected_piece = (row, col)
                # Handle "Undo Move" button
                if pos[0] > SQUARE_SIZE * 8 and pos[0] <= width - 20 and height - 100 <= pos[1] < height - 80:
                    if request_undo(screen, SQUARE_SIZE):
                        client.sendall("undo_request".encode('utf-8'))
                        print("📤 Undo request sent.")
                if pos[0]> SQUARE_SIZE*8 and pos[0]<= width-20 and pos[1] >= height-80: # Click exit
                    try: disconnect()
                    except: pass
                    try: 
                        root.destroy()
                        root_network.destroy()
                    except: pass
                    running = False
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    disconnect()
        
        try:
            data = client.recv(1024).decode('utf-8')
            if data:
                if data.startswith("exit"):
                    running = False
                    result = "Rozłączono"
                    winner = "Ty"
                    break
                elif data.startswith("undo_request"):
                    if confirm_undo_dialog(screen, SQUARE_SIZE):
                        client.sendall("undo_confirm".encode('utf-8'))
                        undoMove(main_board)
                        turn = 'w' if turn == 'b' else 'b'
                        print("✅ Move undone.")
                        start_time = time.time()
                    else:
                        client.sendall("undo_reject".encode('utf-8'))
                elif data.startswith("undo_confirm"):
                    undoMove(main_board)
                    turn = 'w' if turn == 'b' else 'b'
                    print("✅ Move undone.")
                    start_time = time.time()
                elif data.startswith("undo_reject"):
                    print("❌ Undo request rejected.")
                elif data.startswith("pong"):
                    ping_time = round((time.time() - ping_start_time) * 1000, 2)  # Convert to ms and round to 2 decimal places
                    print(f"Ping: {ping_time:.2f} ms")
                    if nerd_view:
                        ping_nerd_view_queue.put(ping_time)
                        root_network.update()
                    client.sendall(("ptime " + str(ping_time)).encode('utf-8'))
                else:
                    print(f"📩 Received move: {data}")
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
                        
                        # Check after move
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
                        # Nerd view:
                        if nerd_view:
                            moves_number = sum(len(value) for value in main_board.get_all_moves(turn))
                            moves_queue.put(move_time)
                        start_time = time.time()
                    
                data = None
        except socket.timeout:
            pass

        # Update player time live
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
        draw_board(screen, SQUARE_SIZE, main_board, in_check)
        draw_interface(screen, turn, SQUARE_SIZE, BLACK, texts, player_times_font, in_check, check_text, evaluation=evaluation, ping=ping_time)
        try:
            if config["highlight_enemy"] or main_board.get_piece(selected_piece[0],selected_piece[1])[0] == 'w':
                highlight_moves(screen, main_board.board_state[selected_piece[0]][selected_piece[1]],SQUARE_SIZE,main_board,  HIGHLIGHT_MOVES, HIGHLIGHT_TAKES)
        except TypeError:
            pass
        except AttributeError:
            pass
        draw_pieces(screen, main_board, SQUARE_SIZE, pieces)
        pygame.display.flip()
        clock.tick(60)

        # Nerd view
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
