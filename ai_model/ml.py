import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from pathlib import Path
import logging
import time
from engine.board_and_fields import Board
import random

class ChessNN(nn.Module):
    def __init__(self):
        super(ChessNN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(773, 2048),
            nn.LeakyReLU(),
            nn.BatchNorm1d(2048),
            nn.Dropout(0.3),
            
            nn.Linear(2048, 1024),
            nn.LeakyReLU(),
            nn.BatchNorm1d(1024),
            nn.Dropout(0.2),
            
            nn.Linear(1024, 512),
            nn.LeakyReLU(),
            nn.BatchNorm1d(512),
            
            nn.Linear(512, 1),
            nn.Tanh()
        )
    
    def forward(self, x):
        return self.network(x)
import engine.figures as figures 
class ChessQLearningAI:
    def __init__(self, board, learning_rate=0.001):
        self.board = board
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = ChessNN().to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.criterion = nn.MSELoss()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            handlers=[logging.FileHandler('training.log'), logging.StreamHandler()]
        )
        self.logger = logging.getLogger(__name__)
        
        self.initial_board_state = self._create_initial_board_state()
        
    def _create_initial_board_state(self):
        """Creates and stores the initial chess board state"""
#import engine.figures as figures     
        # Save initial state
        initial_state = []
        
        # Initial piece setup
        piece_setup = {
            0: {'w': [figures.Rook, figures.Knight, figures.Bishop, figures.King,
                     figures.Queen, figures.Bishop, figures.Knight, figures.Rook]},
            1: {'w': [figures.Pawn]*8},
            6: {'b': [figures.Pawn]*8},
            7: {'b': [figures.Rook, figures.Knight, figures.Bishop, figures.King,
                     figures.Queen, figures.Bishop, figures.Knight, figures.Rook]}
        }
        
        for row in range(8):
            row_state = []
            for col in range(8):
                if row in piece_setup:
                    color = list(piece_setup[row].keys())[0]
                    piece_class = piece_setup[row][color][col]
                    piece = piece_class(color)
                else:
                    piece = None
                row_state.append(piece)
            initial_state.append(row_state)
            
        return initial_state

    def _reset_board(self):
        """Resets the board to initial position without modifying Board class"""
        # Reset piece positions
        for row in range(8):
            for col in range(8):
                initial_piece = self.initial_board_state[row][col]
                if initial_piece:
                    self.board.board_state[row][col].figure = initial_piece.__class__(initial_piece.color)
                else:
                    self.board.board_state[row][col].figure = None
        
        # Reset piece coordinates
        self.board.piece_cords = []
        for row in range(8):
            for col in range(8):
                if self.board.board_state[row][col].figure:
                    self.board.piece_cords.append((row, col))
        
        # Reset board state
        self.board.incheck = False

    def train(self, num_episodes):
        """
        Trains the model for specified number of episodes
        """
        self.model.train()
        total_loss = 0
        start_time = time.time()
        
        for episode in range(num_episodes):
            # Use our custom reset method
            self._reset_board()
            episode_loss = self._train_episode()
            total_loss += episode_loss
            
            if (episode + 1) % 100 == 0:
                avg_loss = total_loss / 100
                elapsed = time.time() - start_time
                self.logger.info(
                    f"Episode {episode + 1}/{num_episodes} "
                    f"| Loss: {avg_loss:.4f} "
                    f"| Time: {elapsed:.1f}s"
                )
                total_loss = 0
                start_time = time.time()
                
        return total_loss / num_episodes

    def _train_episode(self):
        """Training episode with improved error handling"""
        states = []
        rewards = []
        
        try:
            # Generate training data
            for _ in range(50):  # Max 50 moves per episode
                # Verify board state
                if not self._verify_board_state():
                    self._reset_board()  # Reset if invalid state detected
                    continue
                    
                state = self.encode_position(self.board)
                reward = self._get_position_reward()
                
                states.append(state)
                rewards.append(reward)
                
                # Get and verify moves
                try:
                    moves = self._get_safe_moves(self.board, 'w')
                    if not moves:
                        break
                        
                    # Choose random move for training
                    piece = random.choice(list(moves.keys()))
                    move = random.choice(moves[piece])
                    self.board.make_move(piece[0], piece[1], move[0], move[1])
                except Exception as e:
                    self.logger.warning(f"Move generation error: {e}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Training episode error: {e}")
            return 0.0
            
        # Train on collected data
        if states:
            try:
                states = torch.stack(states)
                rewards = torch.FloatTensor(rewards).to(self.device)
                
                self.optimizer.zero_grad()
                outputs = self.model(states).squeeze()
                loss = self.criterion(outputs, rewards)
                loss.backward()
                self.optimizer.step()
                
                return loss.item()
            except Exception as e:
                self.logger.error(f"Training step error: {e}")
                return 0.0
                
        return 0.0

    def _verify_board_state(self):
        """Verify that the board state is valid"""
        try:
            # Check for kings
            white_king = False
            black_king = False
            
            for row in range(8):
                for col in range(8):
                    piece = self.board.board_state[row][col].figure
                    if piece and piece.type == 'K':
                        if piece.color == 'w':
                            white_king = True
                        else:
                            black_king = True
                            
            # Verify piece coordinates
            valid_cords = []
            for row in range(8):
                for col in range(8):
                    if self.board.board_state[row][col].figure:
                        valid_cords.append((row, col))
                        
            self.board.piece_cords = valid_cords
            
            return white_king and black_king
            
        except Exception as e:
            self.logger.warning(f"Board state verification failed: {e}")
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