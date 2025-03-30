import pygame
import sys
import time
from pathlib import Path
from engine.board_and_fields import Board
from engine.engine import tryMove, afterMove, promotion, getPossibleMoves
from graphics import *  # Ensure draw_game_state is defined in this module or imported
from graphics import draw_game_state  # Explicitly import draw_game_state if it exists
from ml import ChessQLearningAI, get_best_move

def initialize_ml():
    """Initialize ML model"""
    try:
        board = Board()
        ml = ChessQLearningAI(board)
        if not ml.load_model('chess_model.pkl'):
            print("Warning: Could not load trained model.")
        return ml
    except Exception as e:
        print(f"Error initializing ML: {e}")
        return None

def main(player_color='w'):
    """Main game function"""
    pygame.init()
    config = load_config()
    resolution = config["resolution"]
    width, height = map(int, resolution.split('x'))
    SQUARE_SIZE = height // 8
    
    # Setup display
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Chess vs ML")
    
    # Initialize board and ML
    board = Board()
    ml = initialize_ml()
    if not ml:
        return

    # Game state
    running = True
    turn = 'w'
    selected_square = None
    possible_moves = []
    last_move = None
    clock = pygame.time.Clock()

    # Load pieces
    pieces = load_pieces(SQUARE_SIZE)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and turn == player_color:
                x, y = pygame.mouse.get_pos()
                col = x // SQUARE_SIZE
                row = y // SQUARE_SIZE
                
                if selected_square:
                    move_made = handle_move(board, turn, selected_square, (row, col))
                    if move_made:
                        turn = 'b' if turn == 'w' else 'w'
                        last_move = (selected_square, (row, col))
                    selected_square = None
                    possible_moves = []
                else:
                    piece = board.board_state[row][col].figure
                    if piece and piece.color == player_color:
                        selected_square = (row, col)
                        possible_moves = getPossibleMoves(turn, board, row, col)

        # AI move
        if turn != player_color and running:
            ml_move = get_best_move(board, turn)
            if ml_move:
                from_row, from_col, to_row, to_col = ml_move
                if tryMove(turn, board, from_row, from_col, to_row, to_col):
                    last_move = ((from_row, from_col), (to_row, to_col))
                    handle_after_move(board, turn)
                    turn = 'b' if turn == 'w' else 'w'

        # Draw everything
        draw_game_state(screen, board, selected_square, possible_moves, last_move, pieces, SQUARE_SIZE)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

def handle_move(board, turn, from_pos, to_pos):
    """Handle move execution and after-move effects"""
    if tryMove(turn, board, from_pos[0], from_pos[1], to_pos[0], to_pos[1]):
        handle_after_move(board, turn)
        return True
    return False

def handle_after_move(board, turn):
    """Handle promotion and check game ending conditions"""
    next_turn = 'b' if turn == 'w' else 'w'
    whatAfter, yForPromotion, xForPromotion = afterMove(next_turn, board)
    
    if whatAfter == "promotion":
        promotion(yForPromotion, xForPromotion, board, '10')  # Always queen
        whatAfter, _, _ = afterMove(next_turn, board)
    
    if whatAfter == "checkmate":
        print(f"Checkmate! {'White' if turn == 'w' else 'Black'} wins!")
    elif whatAfter == "stalemate":
        print("Stalemate! Game drawn.")

def load_pieces(SQUARE_SIZE):
    """Load piece images"""
    config = load_config()
    pieces = {}
    icon_type = config["icons"]
    pieces_short = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces_short:
        pieces[piece] = pygame.transform.scale(
            pygame.image.load(f"pieces/{icon_type}/{piece}.png"), 
            (SQUARE_SIZE-10, SQUARE_SIZE-10)
        )
    return pieces

if __name__ == "__main__":
    main()