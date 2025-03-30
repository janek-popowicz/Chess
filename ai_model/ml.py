import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from pathlib import Path
import logging
import time
from engine.board_and_fields import Board
import random
import engine.figures as figures
import copy
import psutil
import engine.engine as engine

class ChessNN(nn.Module):
    def __init__(self):
        super(ChessNN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(773, 2048),
            nn.LeakyReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(2048, 1024),
            nn.LeakyReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(1024, 512),
            nn.LeakyReLU(),
            
            nn.Linear(512, 1),
            nn.Tanh()
        )
    
    def forward(self, x):
        return self.network(x)

class Field:
    """Field class for board state representation"""
    def __init__(self):
        self.figure = None
        self.x = None  # Add required attributes
        self.y = None

class ChessQLearningAI:
    def __init__(self, board, learning_rate=0.001, color='w'):
        self.board = board
        self.color = color
        self.initial_board_state = self._create_initial_board_state()
        self.model = ChessNN()
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.criterion = nn.MSELoss()
        self.logger = self._setup_logger()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

    def _setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            handlers=[logging.FileHandler('training.log'), logging.StreamHandler()]
        )
        return logging.getLogger(__name__)

    def _create_initial_board_state(self):
        """Creates proper initial board state with Field objects"""
        initial_state = []
        for row in range(8):
            row_state = []
            for col in range(8):
                # Create new Field object directly
                field = Field()
                field.figure = None
                row_state.append(field)
            initial_state.append(row_state)
        
        # Set up initial pieces
        piece_setup = {
            0: {'w': [('R', figures.Rook), ('N', figures.Knight), ('B', figures.Bishop), 
                      ('K', figures.King), ('Q', figures.Queen), ('B', figures.Bishop), 
                      ('N', figures.Knight), ('R', figures.Rook)]},
            1: {'w': [('P', figures.Pawn)]*8},
            6: {'b': [('P', figures.Pawn)]*8},
            7: {'b': [('R', figures.Rook), ('N', figures.Knight), ('B', figures.Bishop),
                      ('K', figures.King), ('Q', figures.Queen), ('B', figures.Bishop),
                      ('N', figures.Knight), ('R', figures.Rook)]}
        }
        
        # Place pieces
        for row in piece_setup:
            color = list(piece_setup[row].keys())[0]
            for col, (piece_type, piece_class) in enumerate(piece_setup[row][color]):
                piece = piece_class(color)
                piece.type = piece_type  # Explicitly set piece type
                initial_state[row][col].figure = piece
                
        return initial_state

    def _reset_board(self):
        """Reset board with better error handling"""
        try:
            self.board.board_state = copy.deepcopy(self.initial_board_state)
            self.board.piece_cords = []
            for row in range(8):
                for col in range(8):
                    if self.board.board_state[row][col].figure:
                        self.board.piece_cords.append((row, col))
            self.board.incheck = False
            return True
        except Exception as e:
            self.logger.error(f"Error resetting board: {e}")
            return False

    def train(self, num_episodes):
        """Train model with detailed metrics"""
        self.model.train()
        total_loss = 0
        valid_episodes = 0
        
        try:
            for episode in range(num_episodes):
                if not self._reset_board():
                    continue
                    
                episode_loss = self._train_episode()
                
                if episode_loss > 0:
                    total_loss += episode_loss
                    valid_episodes += 1
                    
                # Periodic logging for longer batches
                if num_episodes > 1000 and (episode + 1) % 100 == 0:
                    avg_loss = total_loss / valid_episodes if valid_episodes > 0 else 0
                    self.logger.debug(
                        f"Batch progress - Episode {episode + 1}/{num_episodes} | "
                        f"Loss: {avg_loss:.4f} | "
                        f"Valid: {valid_episodes}"
                    )
            
            # Return average loss for batch
            return total_loss / valid_episodes if valid_episodes > 0 else 0
            
        except Exception as e:
            self.logger.error(f"Training batch error: {e}")
            return 0

    def _train_episode(self):
        """Training episode with batch processing"""
        states = []
        rewards = []
        
        try:
            # Collect multiple states before training
            max_attempts = 50  # Max moves per episode
            attempts = 0
            
            while attempts < max_attempts and len(states) < 32:  # Ensure minimum batch size
                if not self._verify_board_state():
                    if not self._reset_board():
                        return 0.0
                    continue
                    
                try:
                    state = self.encode_position(self.board)
                    if state is None:
                        continue
                        
                    reward = self._get_position_reward()
                    if reward is None:
                        continue
                    
                    states.append(state)
                    rewards.append(reward)
                    
                    # Make moves
                    moves = self._get_safe_moves(self.board, 'w')
                    if not moves:
                        break
                        
                    piece = random.choice(list(moves.keys()))
                    move = random.choice(moves[piece])
                    if not self.board.make_move(piece[0], piece[1], move[0], move[1]):
                        break
                        
                except Exception as e:
                    self.logger.debug(f"Move generation error: {e}")
                    break
                    
                attempts += 1
                
            # Train only if we have enough samples
            if len(states) >= 2:  # Minimum batch size
                try:
                    states_tensor = torch.stack(states)
                    rewards_tensor = torch.FloatTensor(rewards).to(self.device)
                    
                    # Ensure tensors have correct shape
                    if states_tensor.shape[0] != rewards_tensor.shape[0]:
                        return 0.0
                        
                    self.optimizer.zero_grad()
                    outputs = self.model(states_tensor).squeeze()
                    loss = self.criterion(outputs, rewards_tensor)
                    loss.backward()
                    self.optimizer.step()
                    
                    return float(loss.item())  # Ensure we return a float
                    
                except Exception as e:
                    self.logger.error(f"Training step error: {e}")
                    return 0.0
                    
        except Exception as e:
            self.logger.error(f"Training episode error: {e}")
            
        return 0.0  # Default return value

    def _verify_board_state(self):
        """Verify board state with proper type checking"""
        try:
            white_king = False
            black_king = False
            valid_cords = []
            
            for row in range(8):
                for col in range(8):
                    field = self.board.board_state[row][col]
                    if not hasattr(field, 'figure'):
                        continue
                        
                    piece = field.figure
                    if piece is not None:
                        valid_cords.append((row, col))
                        if hasattr(piece, 'type') and piece.type == 'K':
                            if piece.color == 'w':
                                white_king = True
                            elif piece.color == 'b':
                                black_king = True
                                
            self.board.piece_cords = valid_cords
            return white_king and black_king
            
        except Exception as e:
            self.logger.error(f"Board state verification failed: {e}")
            return False

    def _get_safe_moves(self, board, color):
        """Get legal moves with enhanced error handling"""
        moves = {}
        
        try:
            for cord in board.piece_cords:
                field = board.board_state[cord[0]][cord[1]]
                if field and field.figure and field.figure.color == color:
                    try:
                        legal_moves = board.get_legal_moves(field, color)
                        if legal_moves:
                            moves[(cord[0], cord[1])] = legal_moves
                    except Exception as e:
                        self.logger.debug(f"Error getting legal moves for piece at {cord}: {e}")
                        continue
        except Exception as e:
            self.logger.warning(f"Error in move generation: {e}")
            
        return moves

    def encode_position(self, board):
        """Convert board state to neural network input with error handling"""
        features = []
        
        # Board representation (8x8x12 = 768)
        piece_map = {
            'wP':0, 'wN':1, 'wB':2, 'wR':3, 'wQ':4, 'wK':5,
            'bP':6, 'bN':7, 'bB':8, 'bR':9, 'bQ':10, 'bK':11
        }
        
        # Process each square
        for row in range(8):
            for col in range(8):
                piece_vec = [0] * 12
                try:
                    piece = board.board_state[row][col].figure
                    if piece and piece.color and piece.type:
                        piece_str = piece.color + piece.type
                        if piece_str in piece_map:
                            piece_vec[piece_map[piece_str]] = 1
                except:
                    pass  # Use zero vector for any errors
                features.extend(piece_vec)
        
        # Add additional features with error handling
        try:
            additional_features = self._calculate_additional_features(board)
            features.extend(additional_features)
        except Exception as e:
            # Add zero features if calculation fails
            features.extend([0.0] * 5)
            self.logger.warning(f"Error calculating additional features: {e}")
        
        return torch.FloatTensor(features).to(self.device)

    def _calculate_additional_features(self, board):
        """Calculate additional positional features with proper error handling"""
        features = []
        
        # Center control
        center_control = 0
        for row, col in [(3,3), (3,4), (4,3), (4,4)]:
            piece = board.board_state[row][col].figure
            if piece:
                center_control += 1 if piece.color == 'w' else -1
        features.append(center_control / 4.0)
        
        # Piece mobility - with safe move calculation
        try:
            white_moves = len(self._get_safe_moves(board, 'w'))
            black_moves = len(self._get_safe_moves(board, 'b'))
            mobility_score = (white_moves - black_moves) / 64.0
        except:
            mobility_score = 0.0
        features.append(mobility_score)
        
        # Add remaining features with safe defaults
        features.extend([
            self._evaluate_king_safety(board),
            self._evaluate_pawn_structure(board),
            self._evaluate_development(board)
        ])
        
        return features

    def _evaluate_king_safety(self, board):
        """Evaluate king safety for both sides"""
        score = 0
        for color in ['w', 'b']:
            # Find king
            king_pos = None
            for row in range(8):
                for col in range(8):
                    piece = board.board_state[row][col].figure
                    if piece and piece.type == 'K' and piece.color == color:
                        king_pos = (row, col)
                        break
                if king_pos:
                    break
                    
            if king_pos:
                # Check pawns in front of king
                row, col = king_pos
                pawn_shield = 0
                for dc in [-1, 0, 1]:
                    next_col = col + dc
                    if 0 <= next_col < 8:
                        next_row = row + (1 if color == 'w' else -1)
                        if 0 <= next_row < 8:
                            piece = board.board_state[next_row][next_col].figure
                            if piece and piece.type == 'P' and piece.color == color:
                                pawn_shield += 1
                
                score += pawn_shield * (0.1 if color == 'w' else -0.1)
                
        return score

    def _evaluate_pawn_structure(self, board):
        """Evaluate pawn structure strength"""
        score = 0
        
        # Check for doubled pawns and isolated pawns
        for col in range(8):
            white_pawns = 0
            black_pawns = 0
            adjacent_cols = []
            
            # Count pawns in current column
            for row in range(8):
                piece = board.board_state[row][col].figure
                if piece and piece.type == 'P':
                    if piece.color == 'w':
                        white_pawns += 1
                    else:
                        black_pawns += 1
            
            # Check adjacent columns for isolated pawns
            for adj_col in [col-1, col+1]:
                if 0 <= adj_col < 8:
                    for row in range(8):
                        piece = board.board_state[row][adj_col].figure
                        if piece and piece.type == 'P':
                            if piece.color == 'w':
                                white_pawns += 0.5  # Add half point for adjacent pawn
                            else:
                                black_pawns += 0.5
            
            # Penalize doubled pawns and isolated pawns
            if white_pawns > 1:
                score -= 0.2  # Penalty for doubled pawns
            if black_pawns > 1:
                score += 0.2
                
            if white_pawns == 0.5:  # Only adjacent pawns, isolated
                score -= 0.1
            if black_pawns == 0.5:
                score += 0.1
        
        return score

    def _evaluate_development(self, board):
        """Evaluate piece development and activity"""
        score = 0
        
        # Evaluate minor piece development
        for piece_type in ['N', 'B']:
            for color in ['w', 'b']:
                developed = 0
                for row in range(8):
                    for col in range(8):
                        piece = board.board_state[row][col].figure
                        if piece and piece.type == piece_type and piece.color == color:
                            # Check if piece has moved from starting position
                            if color == 'w':
                                if row > 1:  # Piece has moved from back rank
                                    developed += 1
                            else:  # black pieces
                                if row < 6:  # Piece has moved from back rank
                                    developed += 1
                
                # Add development bonus
                if color == 'w':
                    score += developed * 0.1
                else:
                    score -= developed * 0.1
        
        # Castling bonus (approximate by king position and rook movement)
        for color in ['w', 'b']:
            start_row = 0 if color == 'w' else 7
            king_moved = False
            rooks_moved = 0
            
            # Check king position
            for col in range(8):
                piece = board.board_state[start_row][col].figure
                if piece and piece.type == 'K' and piece.color == color:
                    if col != 4:  # King has moved
                        king_moved = True
                    break
            
            # Check rook positions
            if board.board_state[start_row][0].figure is None or \
               board.board_state[start_row][7].figure is None:
                rooks_moved += 1
            
            # Add castling penalty if pieces moved without castling
            if king_moved and rooks_moved > 0:
                if color == 'w':
                    score -= 0.3
                else:
                    score += 0.3
        
        return score

    def save_model(self, filename):
        path = Path('models') / filename
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict()
        }, path)
        self.logger.info(f"Model saved to {path}")

    def load_model(self, filename):
        try:
            path = Path('models') / filename
            checkpoint = torch.load(path)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.logger.info(f"Model loaded from {path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            return False

    def _get_position_reward(self):
        """Calculate position reward with improved scaling"""
        material = self._calculate_material()
        position = self._evaluate_position() * 100  # Scale positional score
        
        # Combine scores with weights
        total_score = material * 0.7 + position * 0.3
        
        # Sigmoid-like normalization to [-1, 1]
        return 2 / (1 + np.exp(-total_score/1000)) - 1

    def _calculate_material(self):
        """Calculate material balance with improved piece values and positional bonuses"""
        values = {
            'wP': 100, 'wN': 320, 'wB': 330, 'wR': 500, 'wQ': 900, 'wK': 20000,
            'bP': -100, 'bN': -320, 'bB': -330, 'bR': -500, 'bQ': -900, 'bK': -20000
        }
        
        # Piece-square tables for positional bonuses
        pawn_table = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5,  5, 10, 25, 25, 10,  5,  5],
            [0,  0,  0, 20, 20,  0,  0,  0],
            [5, -5,-10,  0,  0,-10, -5,  5],
            [5, 10, 10,-20,-20, 10, 10,  5],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ]
        
        total = 0
        for row in range(8):
            for col in range(8):
                piece = self.board.board_state[row][col].figure
                if piece:
                    piece_str = piece.color + piece.type
                    if piece_str in values:
                        value = values[piece_str]
                        # Add positional bonus for pawns
                        if piece.type == 'P':
                            if piece.color == 'w':
                                value += pawn_table[row][col]
                            else:
                                value -= pawn_table[7-row][col]
                        total += value
        
        return total

    def _evaluate_position(self):
        """Enhanced positional evaluation with multiple factors"""
        score = 0
        
        # Center control (weighted by piece type)
        center_weights = {'P': 0.3, 'N': 0.4, 'B': 0.4, 'R': 0.2, 'Q': 0.1}
        center_squares = [(3,3), (3,4), (4,3), (4,4)]
        extended_center = [(2,2), (2,3), (2,4), (2,5), 
                          (3,2), (3,5), (4,2), (4,5),
                          (5,2), (5,3), (5,4), (5,5)]
        
        for row, col in center_squares:
            piece = self.board.board_state[row][col].figure
            if piece:
                weight = center_weights.get(piece.type, 0.1)
                score += weight if piece.color == 'w' else -weight
        
        # Extended center control (less weight)
        for row, col in extended_center:
            piece = self.board.board_state[row][col].figure
            if piece:
                weight = center_weights.get(piece.type, 0.1) * 0.5
                score += weight if piece.color == 'w' else -weight
        
        # Development and piece activity
        for row in range(8):
            for col in range(8):
                piece = self.board.board_state[row][col].figure
                if piece:
                    # Penalize undeveloped pieces
                    if piece.color == 'w':
                        if row < 2 and piece.type in ['N', 'B']:
                            score -= 0.15
                        elif row == 1 and piece.type == 'P':
                            score -= 0.05
                    else:
                        if row > 5 and piece.type in ['N', 'B']:
                            score += 0.15
                        elif row == 6 and piece.type == 'P':
                            score += 0.05
                    
                    # Bonus for controlling long diagonals (bishops)
                    if piece.type == 'B':
                        if (row + col == 7) or (row - col == 0):
                            score += 0.2 if piece.color == 'w' else -0.2
        
        return score

    def get_best_move(self):
        """Get best move for current position"""
        try:
            moves = self._get_safe_moves(self.board, self.color)
            if not moves:
                return None
                
            # Choose best move based on Q-learning
            best_move = None
            best_value = float('-inf')
            
            for piece, piece_moves in moves.items():
                for move in piece_moves:
                    # Try move
                    temp_board = copy.deepcopy(self.board)
                    if temp_board.make_move(piece[0], piece[1], move[0], move[1]):
                        state = self.encode_position(temp_board)
                        value = self.model(state).item()
                        
                        if value > best_value:
                            best_value = value
                            best_move = (piece[0], piece[1], move[0], move[1])
            
            return best_move
            
        except Exception as e:
            print(f"Error getting best move: {e}")
            return None

    def _play_validation_game(self):
        """Play a single validation game with better error handling"""
        try:
            board = copy.deepcopy(self.board)
            board.board_state = copy.deepcopy(self.initial_board_state)
            moves_count = 0
            max_moves = 100

            # Reset piece coordinates
            board.piece_cords = []
            for row in range(8):
                for col in range(8):
                    if board.board_state[row][col].figure:
                        board.piece_cords.append((row, col))

            while moves_count < max_moves:
                # Get AI move
                try:
                    legal_moves = board.get_all_moves(self.color)
                    if not legal_moves:
                        return 0.0 if board.is_in_check(self.color) else 0.5
                        
                    # Make AI move
                    move = self.get_best_move()
                    if not move:
                        return 0.0
                        
                    y1, x1, y2, x2 = move
                    if not board.make_move(y1, x1, y2, x2):
                        return 0.0
                        
                    # Check opponent status
                    opponent_color = 'b' if self.color == 'w' else 'w'
                    opponent_moves = board.get_all_moves(opponent_color)
                    
                    if not opponent_moves:
                        return 1.0 if board.is_in_check(opponent_color) else 0.5
                        
                    # Make random opponent move
                    piece = random.choice(list(opponent_moves.keys()))
                    move = random.choice(opponent_moves[piece])
                    if not board.make_move(piece[0], piece[1], move[0], move[1]):
                        return 0.0
                        
                except Exception as e:
                    self.logger.debug(f"Move error in validation game: {e}")
                    return 0.0
                    
                moves_count += 1
                
            return 0.5  # Draw if max moves reached
            
        except Exception as e:
            self.logger.error(f"Validation game error: {e}")
            return 0.0

    def validate(self, num_games=20):
        """Run multiple validation games and return win rate"""
        try:
            wins = 0.0  # Use float to handle None values
            games_played = 0
            
            for _ in range(num_games):
                result = self._play_validation_game()
                if result is not None:  # Only count valid results
                    wins += float(result)
                    games_played += 1
                    
            # Calculate win rate only if we have valid games
            if games_played > 0:
                win_rate = wins / games_played
            else:
                win_rate = 0.0
                
            self.logger.info(f"Validation win rate: {win_rate:.2%} ({games_played} games)")
            return win_rate
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return 0.0

    def test_training(self, episodes=200):
        """Run test training with proper board state handling"""
        self.logger.info(f"Starting test training with {episodes} episodes...")
        
        try:
            # Initialize game tracking
            total_games = 0
            successful_games = 0
            
            for episode in range(episodes):
                # Reset board state
                if not self._reset_board():
                    continue
                    
                # Run training episode
                try:
                    self.model.train()
                    episode_loss = self._train_episode()
                    
                    if episode_loss is not None:
                        successful_games += 1
                    total_games += 1
                    
                    # Log progress
                    if (episode + 1) % 20 == 0:
                        success_rate = successful_games / total_games
                        self.logger.info(
                            f"Test episode {episode + 1}/{episodes} | "
                            f"Loss: {episode_loss:.4f} | "
                            f"Success rate: {success_rate:.2%}"
                        )
                        
                    # Periodic validation
                    if (episode + 1) % 50 == 0:
                        win_rate = self._evaluate_model(num_games=5)
                        self.logger.info(f"Test validation at episode {episode + 1}: {win_rate:.2%}")
                        
                except Exception as e:
                    self.logger.warning(f"Error in episode {episode}: {e}")
                    continue
                    
            # Final validation
            self.logger.info("Running final validation...")
            win_rate = self.validate(num_games=20)
            self.logger.info(f"Test training completed with {win_rate:.2%} win rate")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Test training failed: {e}")
            return False

    def full_training(self):
        """Run full training with 50K episodes"""
        self.logger.info("Starting full training with 50K episodes...")
        start_time = time.time()
        
        try:
            # First run test training
            if not self.test_training():
                self.logger.error("Test training failed, aborting full training")
                return False
                
            self.logger.info("Test successful, starting full training...")
            
            # Run full training
            self.train(50000)
            
            # Log results
            elapsed = time.time() - start_time
            self.logger.info(f"Full training completed in {elapsed:.2f}s")
            
            # Final validation
            win_rate = self.validate(num_games=100)
            self.logger.info(f"Final validation win rate: {win_rate:.2%}")
            
            # Save final model
            self.save_model("final_model.pt")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Full training failed: {e}")
            return False

    def _board_to_tensor(self, board):
        """Convert board to tensor format"""
        try:
            # Use existing encode_position method
            state = self.encode_position(board)
            # Add batch dimension
            return state.unsqueeze(0)
        except Exception as e:
            self.logger.error(f"Error converting board to tensor: {e}")
            # Return zero tensor as fallback
            return torch.zeros(1, 773).to(self.device)

    def _verify_move(self, board, move):
        """Verify if a move is legal and safe"""
        try:
            y1, x1, y2, x2 = move
            piece = board.board_state[y1][x1].figure
            
            # Basic validation
            if not piece:
                return False
            if piece.color != self.color:
                return False
                
            # Check if move is in legal moves
            legal_moves = board.get_all_moves(self.color)
            if (y1, x1) not in legal_moves:
                return False
            if (y2, x2) not in legal_moves[(y1, x1)]:
                return False
                
            # Try move on copy
            temp_board = copy.deepcopy(board)
            if not temp_board.make_move(y1, x1, y2, x2):
                return False
                
            # Check if we're not in check after move
            if temp_board.is_in_check(self.color):
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Move verification error: {e}")
            return False

    def _check_memory(self):
        """Monitor memory usage and cleanup if needed"""
        try:
            process = psutil.Process()
            memory_percent = process.memory_percent()
            
            if memory_percent > 80:  # Over 80% memory usage
                self.logger.warning("High memory usage detected, cleaning up...")
                import gc
                gc.collect()
                torch.cuda.empty_cache()  # If using CUDA
                
            return memory_percent
            
        except Exception as e:
            self.logger.error(f"Memory check error: {e}")
            return None

    def _evaluate_model(self, num_games=10):
        """Evaluate model performance"""
        try:
            self.model.eval()  # Set to evaluation mode
            win_rate = self.validate(num_games)
            self.model.train()  # Set back to training mode
            return win_rate
        except Exception as e:
            self.logger.error(f"Model evaluation error: {e}")
            return 0.0