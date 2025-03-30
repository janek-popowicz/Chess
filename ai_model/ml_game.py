import pygame
import sys
import os
from pathlib import Path
import time
import threading
import queue
from engine.board_and_fields import Board
from engine.engine import tryMove, afterMove, promotion

def play_against_ai(ai, human_color='w'):
    """Play chess against AI using pygame interface"""
    pygame.init()
    
    # Setup display
    SQUARE_SIZE = 100
    WIDTH = SQUARE_SIZE * 8
    HEIGHT = SQUARE_SIZE * 8
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Chess ML Game')
    
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    HIGHLIGHT = (100, 200, 100)
    HIGHLIGHT_TAKES = (147, 168, 50)
    
    # Load piece images
    pieces_dir = Path(__file__).parent.parent / 'assets' / 'pieces'
    pieces = {}
    for color in ['w', 'b']:
        for piece in ['P', 'R', 'N', 'B', 'Q', 'K']:
            piece_path = pieces_dir / f'{color}{piece}.png'
            if piece_path.exists():
                image = pygame.image.load(str(piece_path))
                pieces[f'{color}{piece}'] = pygame.transform.scale(image, (SQUARE_SIZE-10, SQUARE_SIZE-10))
    
    # Game state
    board = Board()
    turn = 'w'
    selected_piece = None
    running = True
    clock = pygame.time.Clock()
    
    # AI move handling
    ai_thinking = False
    move_queue = queue.Queue()
    
    def draw_board():
        """Draw chess board"""
        for row in range(8):
            for col in range(8):
                color = WHITE if (row + col) % 2 == 0 else GRAY
                pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    def draw_pieces():
        """Draw chess pieces"""
        for row in range(8):
            for col in range(8):
                piece = board.board_state[row][col].figure
                if piece:
                    piece_str = f'{piece.color}{piece.type}'
                    if piece_str in pieces:
                        screen.blit(pieces[piece_str], 
                                  (col * SQUARE_SIZE + 5, row * SQUARE_SIZE + 5))
    
    def highlight_moves(selected):
        """Highlight legal moves for selected piece"""
        if not selected:
            return
            
        row, col = selected
        piece = board.board_state[row][col].figure
        if piece:
            legal_moves = board.get_legal_moves(board.board_state[row][col], turn)
            for move in legal_moves:
                y, x = move
                target = board.board_state[y][x].figure
                color = HIGHLIGHT_TAKES if target else HIGHLIGHT
                pygame.draw.rect(screen, color, 
                               (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
    
    def ai_move_thread():
        """Handle AI move calculation in separate thread"""
        try:
            ai_move = ai.get_best_move()
            move_queue.put(ai_move)
        except Exception as e:
            print(f"AI move error: {e}")
            move_queue.put(None)
    
    # Main game loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:  # Restart
                    board = Board()
                    turn = 'w'
                    selected_piece = None
            elif event.type == pygame.MOUSEBUTTONDOWN and turn == human_color:
                x, y = pygame.mouse.get_pos()
                col = x // SQUARE_SIZE
                row = y // SQUARE_SIZE
                
                if selected_piece:
                    if tryMove(turn, board, selected_piece[0], selected_piece[1], row, col):
                        # Handle move completion
                        whatAfter, yForPromotion, xForPromotion = afterMove(turn, board, 
                            selected_piece[0], selected_piece[1], row, col)
                            
                        if whatAfter == "promotion":
                            promotion(yForPromotion, xForPromotion, board, '4')  # Always queen
                            
                        turn = 'w' if turn == 'b' else 'b'
                        selected_piece = None
                    else:
                        selected_piece = (row, col)
                else:
                    piece = board.board_state[row][col].figure
                    if piece and piece.color == human_color:
                        selected_piece = (row, col)
        
        # Handle AI move
        if turn != human_color and not ai_thinking:
            ai_thinking = True
            threading.Thread(target=ai_move_thread, daemon=True).start()
            
        try:
            ai_move = move_queue.get_nowait()
            if ai_move:
                y1, x1, y2, x2 = ai_move
                if tryMove(turn, board, y1, x1, y2, x2):
                    whatAfter, yForPromotion, xForPromotion = afterMove(turn, board, y1, x1, y2, x2)
                    if whatAfter == "promotion":
                        promotion(yForPromotion, xForPromotion, board, '4')
                    turn = 'w' if turn == 'b' else 'b'
            ai_thinking = False
        except queue.Empty:
            pass
        
        # Draw everything
        screen.fill(BLACK)
        draw_board()
        draw_pieces()
        if selected_piece:
            highlight_moves(selected_piece)
            
        # Show "Thinking..." when AI is calculating
        if ai_thinking:
            font = pygame.font.Font(None, 36)
            text = font.render("AI thinking...", True, (255, 0, 0))
            screen.blit(text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

def watch_ai_game(ai):
    """Watch AI play against itself"""
    # Similar implementation as play_against_ai but with AI playing both sides
    pass
