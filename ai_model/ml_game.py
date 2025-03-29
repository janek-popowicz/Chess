import pygame
import sys
import os
from pathlib import Path
from engine.board_and_fields import Board
import time
from tkinter import *
from tkinter import ttk
import random
from pygame.locals import QUIT, MOUSEBUTTONDOWN
import threading
import queue

# Add root directory to Python path for proper imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

class MLGameUI:
    def __init__(self, ai, screen_size=800):
        pygame.init()
        self.screen_size = screen_size
        self.square_size = screen_size // 8
        self.screen = pygame.display.set_mode((screen_size, screen_size))
        pygame.display.set_caption('Chess ML Game')
        
        # Set up project paths
        self.project_root = Path(__file__).parent.parent
        self.pieces_dir = self.project_root / 'assets' / 'pieces'  # Changed from interface to assets
        
        # Create pieces directory if it doesn't exist
        self.pieces_dir.mkdir(parents=True, exist_ok=True)
        
        # Game state initialization
        self.board = Board()
        self.selected_piece = None
        self.ai = ai
        self.game_time = None
        self.move_time = None
        
        # Load pieces with error handling
        self.pieces_images = self._load_pieces()
        
        # AI threading
        self.move_queue = queue.Queue()
        self.ai_thinking = False

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (128, 128, 128)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        
        # Move history for undo
        self.move_history = []
        self.game_started = False
        
        # Time settings with defaults
        self.settings = {
            'game_time': 600,  # 10 minutes in seconds
            'move_time': 10,   # 10 seconds
            'custom_settings': False
        }

    def _load_pieces(self):
        """Load piece images with proper path handling and error checking"""
        pieces = {}
        
        # Verify pieces directory exists
        if not self.pieces_dir.exists():
            raise FileNotFoundError(f"Pieces directory not found at {self.pieces_dir}")
            
        for color in ['w', 'b']:
            for piece in ['P', 'R', 'N', 'B', 'Q', 'K']:
                piece_path = self.pieces_dir / f'{color}{piece}.png'
                
                # Check if piece image exists, use placeholder if not
                if not piece_path.exists():
                    print(f"Warning: Missing piece image: {piece_path}")
                    # Create a simple colored rectangle as placeholder
                    surface = pygame.Surface((self.square_size, self.square_size))
                    surface.fill((255, 0, 0) if color == 'w' else (0, 0, 255))
                    pieces[f'{color}{piece}'] = surface
                else:
                    image = pygame.image.load(str(piece_path))
                    pieces[f'{color}{piece}'] = pygame.transform.scale(
                        image, (self.square_size, self.square_size)
                    )
        return pieces

    def load_settings(self):
        """Load game settings from settings.txt"""
        settings_path = self.project_root / 'settings.txt'
        if settings_path.exists():
            try:
                with open(settings_path, 'r') as f:
                    for line in f:
                        key, value = line.strip().split('=')
                        if key in ['game_time', 'move_time']:
                            self.settings[key] = float(value)
                self.settings['custom_settings'] = True
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save_settings(self):
        """Save current settings to file"""
        settings_path = self.project_root / 'settings.txt'
        try:
            with open(settings_path, 'w') as f:
                f.write(f"game_time={self.settings['game_time']}\n")
                f.write(f"move_time={self.settings['move_time']}\n")
        except Exception as e:
            print(f"Error saving settings: {e}")

    def draw_board(self):
        for row in range(8):
            for col in range(8):
                color = self.WHITE if (row + col) % 2 == 0 else self.GRAY
                pygame.draw.rect(self.screen, color,
                               (col * self.square_size, row * self.square_size,
                                self.square_size, self.square_size))

    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                piece = self.board.board_state[row][col].figure
                if piece:
                    piece_str = f'{piece.color}{piece.type}'
                    if piece_str in self.pieces_images:
                        self.screen.blit(
                            self.pieces_images[piece_str],
                            (col * self.square_size, row * self.square_size)
                        )

    def draw_time_and_info(self, elapsed):
        """Draw time and game information"""
        font = pygame.font.Font(None, 36)
        
        # Time remaining
        time_left = max(0, self.settings['game_time'] - elapsed)
        minutes = int(time_left // 60)
        seconds = int(time_left % 60)
        time_text = f"Time: {minutes:02d}:{seconds:02d}"
        time_surface = font.render(time_text, True, self.BLACK)
        self.screen.blit(time_surface, (self.screen_size - 200, 10))
        
        # Game controls info
        controls = [
            "R - Restart",
            "Z - Undo",
            "Q - Quit"
        ]
        
        y_offset = 50
        for control in controls:
            text = font.render(control, True, self.BLACK)
            self.screen.blit(text, (self.screen_size - 200, y_offset))
            y_offset += 30

    def undo_move(self):
        """Undo the last two moves (human and AI)"""
        if len(self.move_history) >= 2:
            # Undo AI move
            last_move = self.move_history.pop()
            self.board.undo_move(*last_move)
            # Undo human move
            last_move = self.move_history.pop()
            self.board.undo_move(*last_move)
            return True
        return False

    def get_time_settings(self):
        root = Tk()
        root.title("Game Settings")
        
        game_time = StringVar(value="10")
        move_time = StringVar(value="3")
        
        def validate_times():
            try:
                g_time = float(game_time.get())
                m_time = float(move_time.get())
                if m_time > g_time * 0.3:
                    return False
                return True
            except ValueError:
                return False
        
        def save_settings():
            if validate_times():
                self.settings['game_time'] = float(game_time.get()) * 60  # Convert to seconds
                self.settings['move_time'] = float(move_time.get())
                root.destroy()
        
        frame = ttk.Frame(root, padding="10")
        frame.grid(row=0, column=0, sticky=(N, W, E, S))
        
        ttk.Label(frame, text="Game time (minutes):").grid(row=0, column=0)
        ttk.Entry(frame, textvariable=game_time).grid(row=0, column=1)
        
        ttk.Label(frame, text="Move time (seconds):").grid(row=1, column=0)
        ttk.Entry(frame, textvariable=move_time).grid(row=1, column=1)
        
        ttk.Button(frame, text="Start", command=save_settings).grid(row=2, column=0, columnspan=2)
        
        root.mainloop()

    def ai_move_thread(self):
        """Separate thread for AI move calculation"""
        try:
            moves = self.ai._get_safe_moves(self.board, self.board.current_turn)
            if not moves:
                self.move_queue.put(None)
                return

            move_start = time.time()
            ai_move = None

            # Try to get best move with timeout
            while time.time() - move_start < 10:
                ai_move = self.ai.get_best_move()
                if ai_move:
                    break
                time.sleep(0.1)

            # If no best move found, use random move
            if not ai_move and moves:
                piece = random.choice(list(moves.keys()))
                move = random.choice(moves[piece])
                ai_move = (piece[0], piece[1], move[0], move[1])

            self.move_queue.put(ai_move)
        except Exception as e:
            print(f"Error in AI thread: {e}")
            self.move_queue.put(None)
        finally:
            self.ai_thinking = False

    def main_game_loop(self, human_color):
        # Load saved settings or use defaults
        if not self.settings['custom_settings']:
            self.load_settings()
            self.get_time_settings()
        
        game_start = time.time()
        clock = pygame.time.Clock()
        running = True
        
        while running:
            current_time = time.time()
            elapsed = current_time - game_start
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Restart
                        from algorithms.algorithms_game import main as start_game
                        pygame.quit()
                        start_game('ml', human_color=human_color)
                        return
                    elif event.key == pygame.K_z:  # Undo
                        if self.undo_move():
                            self.selected_piece = None
                    elif event.key == pygame.K_q:  # Quit to launcher
                        pygame.quit()
                        return
                elif event.type == pygame.MOUSEBUTTONDOWN and self.board.current_turn == human_color:
                    x, y = pygame.mouse.get_pos()
                    col = x // self.square_size
                    row = y // self.square_size
                    
                    if self.selected_piece:
                        if self.board.make_move(
                            self.selected_piece[0],
                            self.selected_piece[1],
                            row, col
                        ):
                            self.move_history.append((
                                self.selected_piece[0],
                                self.selected_piece[1],
                                row, col
                            ))
                            self.selected_piece = None
                        else:
                            self.selected_piece = (row, col)
                    else:
                        piece = self.board.board_state[row][col].figure
                        if piece and piece.color == human_color:
                            self.selected_piece = (row, col)

            # Handle AI move in separate thread
            if self.board.current_turn != human_color and not self.ai_thinking:
                self.ai_thinking = True
                threading.Thread(target=self.ai_move_thread, daemon=True).start()

            # Check for completed AI move
            try:
                ai_move = self.move_queue.get_nowait()
                if ai_move:
                    y1, x1, y2, x2 = ai_move
                    if self.board.make_move(y1, x1, y2, x2):
                        self.move_history.append((y1, x1, y2, x2))
            except queue.Empty:
                pass  # No move available yet

            # Draw everything
            self.draw_board()
            self.draw_pieces()
            self.draw_time_and_info(elapsed)
            
            # Draw "Thinking..." text when AI is calculating
            if self.ai_thinking:
                font = pygame.font.Font(None, 36)
                text = font.render("AI thinking...", True, self.RED)
                self.screen.blit(text, (10, 10))
            
            pygame.display.flip()
            clock.tick(60)
            
            # Check for game over conditions
            if elapsed >= self.settings['game_time']:
                font = pygame.font.Font(None, 48)
                text = font.render("Time's up!", True, self.RED)
                self.screen.blit(text, (self.screen_size//2 - 100, self.screen_size//2))
                pygame.display.flip()
                time.sleep(2)
                break
        
        pygame.quit()

class ChessGame:
    def __init__(self, ai, board):
        self.ai = ai
        self.board = board

    def play_interactive_game(self, human_color):
        """
        Play an interactive chess game against a human player using Pygame.
        """
        # Initialize Pygame
        pygame.init()
        screen = pygame.display.set_mode((800, 800))
        pygame.display.set_caption("Chess Game")
        clock = pygame.time.Clock()

        # Colors
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        HIGHLIGHT = (0, 255, 0)
        TILE_SIZE = 100

        # Load images for pieces (assuming images are in a folder named 'assets')
        piece_images = {}
        for piece in ['wP', 'wN', 'wB', 'wR', 'wQ', 'wK', 'bP', 'bN', 'bB', 'bR', 'bQ', 'bK']:
            piece_images[piece] = pygame.image.load(f'assets/{piece}.png')

        # Reset the board
        self.ai._reset_board()
        current_color = 'w'
        selected_piece = None
        legal_moves = []

        def draw_board():
            """Draw the chessboard and pieces."""
            for row in range(8):
                for col in range(8):
                    # Flip the board for black
                    display_row = 7 - row if human_color == 'b' else row
                    display_col = 7 - col if human_color == 'b' else col

                    # Draw tiles
                    color = WHITE if (row + col) % 2 == 0 else BLACK
                    pygame.draw.rect(screen, color, (display_col * TILE_SIZE, display_row * TILE_SIZE, TILE_SIZE, TILE_SIZE))

                    # Highlight legal moves
                    if (row, col) in legal_moves:
                        pygame.draw.rect(screen, HIGHLIGHT, (display_col * TILE_SIZE, display_row * TILE_SIZE, TILE_SIZE, TILE_SIZE), 5)

                    # Draw pieces
                    piece = self.board.board_state[row][col].figure
                    if piece:
                        piece_str = piece.color + piece.type
                        if piece_str in piece_images:
                            screen.blit(piece_images[piece_str], (display_col * TILE_SIZE, display_row * TILE_SIZE))

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONDOWN:
                    # Handle human player's move
                    if current_color == human_color:
                        mouse_x, mouse_y = event.pos
                        clicked_col = mouse_x // TILE_SIZE
                        clicked_row = mouse_y // TILE_SIZE

                        # Flip the board for black
                        board_row = 7 - clicked_row if human_color == 'b' else clicked_row
                        board_col = 7 - clicked_col if human_color == 'b' else clicked_col

                        if selected_piece:
                            # Attempt to make a move
                            if (board_row, board_col) in legal_moves:
                                self.board.make_move(selected_piece[0], selected_piece[1], board_row, board_col)
                                current_color = 'w' if current_color == 'b' else 'b'
                                selected_piece = None
                                legal_moves = []
                            else:
                                # Deselect if clicked outside legal moves
                                selected_piece = None
                                legal_moves = []
                        else:
                            # Select a piece
                            piece = self.board.board_state[board_row][board_col].figure
                            if piece and piece.color == human_color:
                                selected_piece = (board_row, board_col)
                                legal_moves = self.ai._get_safe_moves(self.board, human_color).get(selected_piece, [])

            # AI's turn
            if current_color != human_color:
                try:
                    moves = self.ai._get_safe_moves(self.board, current_color)
                    if not moves:
                        print(f"{current_color} has no legal moves. Game over!")
                        running = False
                        continue

                    # Choose a random move for simplicity
                    piece = random.choice(list(moves.keys()))
                    move = random.choice(moves[piece])
                    self.board.make_move(piece[0], piece[1], move[0], move[1])
                    current_color = 'w' if current_color == 'b' else 'b'
                except Exception as e:
                    print(f"Error during AI move: {e}")
                    running = False

            # Update the display
            screen.fill((255, 255, 255))  # Clear the screen
            draw_board()
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()

def main(ai, human_color='w'):
    """Main function to start the game with proper model handling"""
    try:
        game = MLGameUI(ai)
        game.main_game_loop(human_color)
    except Exception as e:
        print(f"Error starting game: {e}")
        pygame.quit()

if __name__ == "__main__":
    # For testing purposes only
    from ai_model.ml import ChessQLearningAI
    
    # Initialize AI with proper model path
    ai = ChessQLearningAI(Board())
    model_path = PROJECT_ROOT / 'models' / 'test_model.pt'
    
    if model_path.exists():
        ai.load_model(str(model_path))
        main(ai)
    else:
        print(f"Model not found at {model_path}")
