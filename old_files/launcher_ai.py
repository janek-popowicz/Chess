import pygame
import time
import sys
import os

# Add the main directory to sys.path if it's not already there
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import minimax algorithm
from algorithms.minimax import Minimax

class ChessAIHandler:
    """
    Class to handle AI moves and integration with the main chess game
    """
    def __init__(self, difficulty='medium'):
        """
        Initialize the Chess AI handler
        
        Parameters:
        difficulty (str): 'easy', 'medium', or 'hard' - affects search depth
        """
        self.difficulty = difficulty
        self.minimax = Minimax()
        
        # Set difficulty level for minimax
        depth_map = {
            'easy': 1,
            'medium': 2,
            'hard': 3
        }
        self.minimax.depth = depth_map.get(difficulty, 2)
        
        # Thinking time simulation based on difficulty
        self.thinking_time = {
            'easy': 0.5,
            'medium': 1.0,
            'hard': 1.5
        }.get(difficulty, 1.0)
    
    def get_ai_move(self, board, turn):
        """
        Get the best move for the AI using minimax algorithm
        
        Parameters:
        board: The current chess board
        turn: Current player's turn ('w' or 'b')
        
        Returns:
        Tuple (from_row, from_col, to_row, to_col) or None if no move is possible
        """
        # Update the minimax object with current board state
        self.minimax.set_board(board)
        self.minimax.set_player(turn)
        
        # Get the best move
        try:
            # Simulate "thinking" time
            time.sleep(self.thinking_time)
            move = self.minimax.get_best_move()
            
            if move:
                from_row, from_col, to_row, to_col = move
                return from_row, from_col, to_row, to_col
        except Exception as e:
            print(f"AI Error: {e}")
        
        return None

def ai_promotion_dialog(turn):
    """
    Returns the piece type that AI chooses for promotion.
    For simplicity, always returns 'Q' (Queen) as it's typically the strongest piece.
    
    Parameters:
    turn: Current player's turn ('w' or 'b')
    
    Returns:
    str: The piece type for promotion ('Q', 'R', 'B', or 'N')
    """
    return 'Q'  # AI always promotes to Queen

def handle_ai_turn(screen, SQUARE_SIZE, main_board, turn, ai_handler, start_time):
    """
    Handle the AI's turn
    
    Parameters:
    screen: Pygame screen
    SQUARE_SIZE: Size of chess squares
    main_board: Current chess board
    turn: Current player ('w' or 'b')
    ai_handler: The ChessAIHandler instance
    start_time: Time when the turn started
    
    Returns:
    tuple: (new_turn, move_time, whatAfter, in_check, selected_piece)
    """
    # Display "Thinking..." text
    font = pygame.font.Font(None, 36)
    thinking_text = font.render("AI is thinking...", True, pygame.Color("yellow"))
    text_rect = thinking_text.get_rect(center=(4 * SQUARE_SIZE, 4 * SQUARE_SIZE))
    
    # Create a semi-transparent overlay
    overlay = pygame.Surface((8 * SQUARE_SIZE, 8 * SQUARE_SIZE), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    screen.blit(thinking_text, text_rect)
    pygame.display.flip()
    
    # Get AI move
    move = ai_handler.get_ai_move(main_board, turn)
    
    if move:
        from_row, from_col, to_row, to_col = move
        
        # Highlight selected piece
        pygame.draw.rect(screen, pygame.Color("yellow"),
                        pygame.Rect(SQUARE_SIZE * (7 - from_col), SQUARE_SIZE * (7 - from_row),
                                    SQUARE_SIZE, SQUARE_SIZE), 3)
        pygame.display.flip()
        time.sleep(0.5)  # Brief pause to show the selected piece
        
        # Try to make the move
        if tryMove(turn, main_board, from_row, from_col, to_row, to_col):
            # Calculate move time
            move_time = time.time() - start_time
            
            # Switch turns
            new_turn = 'w' if turn == 'b' else 'b'
            
            # Check what happens after the move
            whatAfter, yForPromotion, xForPromotion = afterMove(new_turn, main_board, from_row, from_col, to_row, to_col)
            
            # Handle promotion
            if whatAfter == "promotion":
                promotion_choice = ai_promotion_dialog(turn)
                promotion(yForPromotion, xForPromotion, main_board, promotion_choice)
                whatAfter, _, _ = afterMove(new_turn, main_board, from_row, from_col, to_row, to_col)
            
            # Check for check state
            in_check = new_turn if whatAfter == "check" else None
            
            return new_turn, move_time, whatAfter, in_check, None
    
    # If no move was made, return original values
    return turn, 0, None, None, None

def add_ai_mode_to_main():
    """
    This function modifies the main game loop to add AI functionality.
    It should be called from the main() function after creating the game window.
    
    Example usage in main():
    # After config loading and before game loop
    ai_enabled, ai_color, ai_difficulty, ai_handler = add_ai_mode_to_main()
    """
    # Create a window for game mode selection
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Chess Game Mode")
    
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (100, 100, 100)
    BLUE = (0, 0, 255)
    
    font = pygame.font.Font(None, 36)
    
    # Game mode options
    options = [
        "Two Players",
        "Play as White (vs AI)",
        "Play as Black (vs AI)"
    ]
    
    # Difficulty options
    difficulties = ["Easy", "Medium", "Hard"]
    
    selected_option = 0
    selected_difficulty = 1  # Default to Medium
    
    # Game mode selection screen
    mode_selected = False
    while not mode_selected:
        screen.fill(BLACK)
        
        # Draw title
        title = font.render("Select Game Mode", True, WHITE)
        screen.blit(title, (100, 30))
        
        # Draw options
        for i, option in enumerate(options):
            color = BLUE if i == selected_option else WHITE
            text = font.render(option, True, color)
            screen.blit(text, (100, 100 + i * 50))
        
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    mode_selected = True
    
    # If AI mode is selected, show difficulty selection
    ai_enabled = selected_option > 0
    ai_color = 'b' if selected_option == 1 else 'w'
    ai_difficulty = 'medium'  # Default
    
    if ai_enabled:
        difficulty_selected = False
        while not difficulty_selected:
            screen.fill(BLACK)
            
            # Draw title
            title = font.render("Select AI Difficulty", True, WHITE)
            screen.blit(title, (100, 30))
            
            # Draw options
            for i, difficulty in enumerate(difficulties):
                color = BLUE if i == selected_difficulty else WHITE
                text = font.render(difficulty, True, color)
                screen.blit(text, (150, 100 + i * 50))
            
            pygame.display.flip()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_difficulty = (selected_difficulty - 1) % len(difficulties)
                    elif event.key == pygame.K_DOWN:
                        selected_difficulty = (selected_difficulty + 1) % len(difficulties)
                    elif event.key == pygame.K_RETURN:
                        difficulty_selected = True
        
        ai_difficulty = difficulties[selected_difficulty].lower()
    
    # Create AI handler if needed
    ai_handler = ChessAIHandler(ai_difficulty) if ai_enabled else None
    
    return ai_enabled, ai_color, ai_difficulty, ai_handler