import pygame
import sys
import os
from pathlib import Path
from engine.board_and_fields import Board
import time
from tkinter import *
from tkinter import ttk

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
                self.game_time = float(game_time.get()) * 60  # Convert to seconds
                self.move_time = float(move_time.get())
                root.destroy()
        
        frame = ttk.Frame(root, padding="10")
        frame.grid(row=0, column=0, sticky=(N, W, E, S))
        
        ttk.Label(frame, text="Game time (minutes):").grid(row=0, column=0)
        ttk.Entry(frame, textvariable=game_time).grid(row=0, column=1)
        
        ttk.Label(frame, text="Move time (seconds):").grid(row=1, column=0)
        ttk.Entry(frame, textvariable=move_time).grid(row=1, column=1)
        
        ttk.Button(frame, text="Start", command=save_settings).grid(row=2, column=0, columnspan=2)
        
        root.mainloop()

    def main_game_loop(self, human_color):
        self.get_time_settings()
        if not self.game_time or not self.move_time:
            return
            
        game_start = time.time()
        clock = pygame.time.Clock()
        running = True
        
        while running:
            current_time = time.time()
            elapsed = current_time - game_start
            
            if elapsed >= self.game_time:
                print("Game over - Time's up!")
                break
                
            if self.board.current_turn == human_color:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = pygame.mouse.get_pos()
                        col = x // self.square_size
                        row = y // self.square_size
                        
                        if self.selected_piece:
                            if self.board.make_move(
                                self.selected_piece[0],
                                self.selected_piece[1],
                                row, col
                            ):
                                self.selected_piece = None
                            else:
                                self.selected_piece = (row, col)
                        else:
                            piece = self.board.board_state[row][col].figure
                            if piece and piece.color == human_color:
                                self.selected_piece = (row, col)
            else:
                # AI move
                move_start = time.time()
                ai_move = self.ai.get_best_move()
                
                if ai_move and time.time() - move_start <= self.move_time:
                    y1, x1, y2, x2 = ai_move
                    self.board.make_move(y1, x1, y2, x2)
            
            # Draw everything
            self.draw_board()
            self.draw_pieces()
            pygame.display.flip()
            clock.tick(60)
        
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
