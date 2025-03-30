# ml_game.py
import pygame
import time
import sys
from engine.board_and_fields import Board
from engine.engine import tryMove, afterMove, promotion, undoMove
from graphics import *
from ai_model.ml import ChessAI
import json

def format_time(seconds):
    """Convert seconds to MM:SS format"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except:
        return {"resolution": "1260x960", "icons": "classic", "volume": 50}

def main(player_color='w', game_time=600):
    pygame.init()
    config = load_config()
    resolution = config["resolution"]
    width, height = map(int, resolution.split('x'))
    SQUARE_SIZE = height // 8

    # Setup display
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Chess ML")
    icon_logo = pygame.image.load('program_logo.png')
    pygame.display.set_icon(icon_logo)

    # Colors and settings
    COLORS = {
        'WHITE': (255, 255, 255),
        'BLACK': (0, 0, 0),
        'GRAY': (100, 100, 100),
        'YELLOW': pygame.Color("yellow"),
        'HIGHLIGHT': (100, 200, 100),
        'HIGHLIGHT_TAKE': (147, 168, 50)
    }
    
    # Load pieces
    pieces = {}
    icon_type = config["icons"]
    pieces_short = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces_short:
        pieces[piece] = pygame.transform.scale(
            pygame.image.load(f"pieces/{icon_type}/{piece}.png"),
            (SQUARE_SIZE-10, SQUARE_SIZE-10)
        )

    # Game initialization
    font = pygame.font.Font(None, 36)
    board = Board()
    ai = ChessAI()
    selected_piece = None
    turn = 'w'
    running = True
    clock = pygame.time.Clock()
    in_check = None

    # Interface texts
    texts = [
        (font.render("Turn: White", True, COLORS['WHITE']), (8 * SQUARE_SIZE + 10, 10)),
        (font.render("Turn: Black", True, COLORS['WHITE']), (8 * SQUARE_SIZE + 10, 10)),
        (font.render("Exit", True, COLORS['GRAY']), (8 * SQUARE_SIZE + 10, height - 50)),
        (font.render("Undo", True, COLORS['GRAY']), (8 * SQUARE_SIZE + 10, height - 100))
    ]
    check_text = font.render("Check!", True, pygame.Color("red"))

    # Time tracking
    start_time = time.time()
    white_time = black_time = game_time
    result = ""
    winner = ""

    while running:
        current_time = time.time()
        
        # Update times
        if turn == 'w':
            current_white_time = max(0, white_time - (current_time - start_time))
            current_black_time = black_time
        else:
            current_black_time = max(0, black_time - (current_time - start_time))
            current_white_time = white_time

        # Check for timeout
        if current_white_time <= 0 or current_black_time <= 0:
            result = "Time's up!"
            winner = "Black" if current_white_time <= 0 else "White"
            running = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and turn == player_color:
                x, y = pygame.mouse.get_pos()
                
                # Interface buttons
                if x > 8*SQUARE_SIZE:
                    if y >= height - 80:  # Exit button
                        running = False
                    elif height - 130 <= y < height - 80:  # Undo button
                        if confirm_undo_dialog(screen, SQUARE_SIZE):
                            if undoMove(board):
                                turn = 'w' if turn == 'b' else 'b'
                                start_time = time.time()
                    continue

                # Board interaction
                col = x // SQUARE_SIZE
                row = y // SQUARE_SIZE
                
                if selected_piece:
                    if tryMove(turn, board, selected_piece[0], selected_piece[1], row, col):
                        # Update time
                        move_time = time.time() - start_time
                        if turn == 'w':
                            white_time -= move_time
                        else:
                            black_time -= move_time
                        
                        # Handle move completion
                        whatAfter, yPromotion, xPromotion = afterMove(turn, board)
                        if whatAfter == "promotion":
                            choice = promotion_dialog(screen, SQUARE_SIZE, turn)
                            promotion(yPromotion, xPromotion, board, choice)
                            whatAfter, _, _ = afterMove(turn, board)
                        
                        if whatAfter == "checkmate":
                            result = "Checkmate!"
                            winner = "White" if turn == 'w' else "Black"
                            running = False
                        elif whatAfter == "stalemate":
                            result = "Stalemate!"
                            winner = "Draw"
                            running = False
                        elif whatAfter == "check":
                            in_check = turn
                        else:
                            in_check = None
                        
                        turn = 'b' if turn == 'w' else 'w'
                        start_time = time.time()
                    selected_piece = None
                else:
                    piece = board.board_state[row][col].figure
                    if piece and piece.color == turn:
                        selected_piece = (row, col)

        # AI move
        if turn != player_color and running:
            ai_move = ai.get_best_move(board, turn)
            if ai_move:
                y1, x1, y2, x2 = ai_move
                if tryMove(turn, board, y1, x1, y2, x2):
                    move_time = time.time() - start_time
                    if turn == 'w':
                        white_time -= move_time
                    else:
                        black_time -= move_time
                    
                    whatAfter, yPromotion, xPromotion = afterMove(turn, board)
                    if whatAfter == "promotion":
                        promotion(yPromotion, xPromotion, board, '10')  # Always promote to queen
                        whatAfter, _, _ = afterMove(turn, board)
                    
                    if whatAfter == "checkmate":
                        result = "Checkmate!"
                        winner = "White" if turn == 'w' else "Black"
                        running = False
                    elif whatAfter == "stalemate":
                        result = "Stalemate!"
                        winner = "Draw"
                        running = False
                    elif whatAfter == "check":
                        in_check = turn
                    else:
                        in_check = None
                    
                    turn = 'b' if turn == 'w' else 'w'
                    start_time = time.time()

        # Draw game state
        screen.fill(COLORS['BLACK'])
        draw_board(screen, SQUARE_SIZE, board, in_check)
        
        if selected_piece:
            piece = board.board_state[selected_piece[0]][selected_piece[1]]
            highlight_moves(screen, piece, SQUARE_SIZE, board, COLORS['HIGHLIGHT'], COLORS['HIGHLIGHT_TAKE'])
        
        draw_pieces(screen, board, SQUARE_SIZE, pieces)

        # Draw times
        times = (
            (font.render(format_time(current_black_time), True, COLORS['YELLOW'] if turn == 'b' else COLORS['GRAY']),
             (8 * SQUARE_SIZE + 10, 80)),
            (font.render(format_time(current_white_time), True, COLORS['YELLOW'] if turn == 'w' else COLORS['GRAY']),
             (8 * SQUARE_SIZE + 10, height - 150))
        )

        # Draw interface
        draw_interface(screen, turn, SQUARE_SIZE, COLORS['BLACK'], texts, times, in_check, check_text)
        
        pygame.display.flip()
        clock.tick(60)

    # Show end screen if game ended
    if result:
        end_screen(screen, result, winner, white_time, black_time, SQUARE_SIZE, width, height, COLORS['WHITE'], COLORS['BLACK'])
        pygame.time.wait(3000)

    pygame.quit()

if __name__ == "__main__":
    main()