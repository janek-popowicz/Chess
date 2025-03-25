import numpy as np
import random
import copy
import logging
import time
import engine.board_and_fields as board_and_fields
import engine.engine as engine

class ChessQLearningAI:
    def __init__(self, board, learning_rate=0.1, discount_factor=0.9, exploration_rate=1.0):
        """
        Initialize the Q-learning chess AI with advanced features.
        
        Args:
            board (Board): The chess board object
            learning_rate (float): How much the AI learns from new experiences
            discount_factor (float): How much future rewards are valued
            exploration_rate (float): Probability of choosing a random move
        """
        # Logging setup
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
        self.logger = logging.getLogger(__name__)

        # Board and learning parameters
        self.board = board
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.initial_exploration_rate = exploration_rate
        self.exploration_rate = exploration_rate
        
        # Q-table management
        self.q_table = {}
        self.max_q_table_size = 100000
        self.best_moves_memory = {}
        
        # Training tracking
        self.training_progress = {
            'total_episodes': 0,
            'completed_episodes': 0,
            'average_reward': 0,
            'best_reward': float('-inf'),
            'exploration_decay_rate': 0.99
        }
    
    def get_board_state(self):
        """
        Convert current board state to a hashable representation.
        Improved state representation for better learning.
        
        Returns:
            tuple: Compact board state representation
        """
        state = []
        for y, row in enumerate(self.board.board_state):
            for x, field in enumerate(row):
                if field.figure:
                    # Use a tuple with piece info and board coordinates
                    state.append((
                        field.figure.return_figure(), 
                        y, 
                        x
                    ))
                else:
                    state.append(None)
        return tuple(state)
    
    def get_possible_moves(self, turn):
        """
        Get all legal moves for the current turn.
        
        Args:
            turn (str): Current player's turn ('w' or 'b')
        
        Returns:
            list: List of possible moves
        """
        try:
            all_moves = self.board.get_all_moves(turn)
            moves_list = []
            for start_pos, move_destinations in all_moves.items():
                for dest in move_destinations:
                    moves_list.append((*start_pos, *dest))
            return moves_list
        except Exception as e:
            self.logger.error(f"Error getting moves: {e}")
            return []
    
    def choose_move(self, turn):
        """
        Choose a move using an advanced epsilon-greedy strategy.
        
        Args:
            turn (str): Current player's turn ('w' or 'b')
        
        Returns:
            tuple: Chosen move (start_y, start_x, target_y, target_x)
        """
        possible_moves = self.get_possible_moves(turn)
        
        # Use best moves memory if available
        state = self.get_board_state()
        if state in self.best_moves_memory:
            best_known_move = self.best_moves_memory[state]
            if best_known_move in possible_moves:
                return best_known_move
        
        # Exploration
        if random.random() < self.exploration_rate:
            return random.choice(possible_moves)
        
        # Exploitation
        best_move = None
        best_value = float('-inf')
        
        for move in possible_moves:
            # Get Q-value for this state-action pair
            q_value = self.q_table.get((state, move), 0)
            if q_value > best_value:
                best_value = q_value
                best_move = move
        
        return best_move or random.choice(possible_moves)
    
    def calculate_reward(self, turn):
        """
        Advanced reward calculation considering multiple game aspects.
        
        Args:
            turn (str): Current player's turn
        
        Returns:
            float: Reward value
        """
        # Reward structure
        if self.board.incheck:
            # Higher penalty for being in check
            return -20
        
        # Advanced piece valuation
        piece_values = {
            'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0,
            'p': -1, 'n': -3, 'b': -3, 'r': -5, 'q': -9, 'k': 0
        }
        
        # Calculate piece value difference
        piece_reward = 0
        for row in self.board.board_state:
            for field in row:
                if field.figure:
                    piece_reward += piece_values.get(field.figure.return_figure(), 0)
        
        # Additional strategic bonuses
        bonus = 10 if turn == 'w' and piece_reward > 0 else -10 if turn == 'b' and piece_reward < 0 else 0
        
        return piece_reward + bonus
    
    def update_q_table(self, state, move, reward, next_state):
        """
        Update Q-table with advanced learning strategy.
        
        Args:
            state (tuple): Current board state
            move (tuple): Executed move
            reward (float): Reward received
            next_state (tuple): Next board state
        """
        old_q_value = self.q_table.get((state, move), 0)
        
        # Find maximum Q-value for next state
        max_next_q_value = max(
            [self.q_table.get((next_state, next_move), 0) 
             for next_move in self.get_possible_moves('w' if move[0] < 4 else 'b')]
            or [0]
        )
        
        # Q-learning update rule with adaptive learning
        new_q_value = old_q_value + self.learning_rate * (
            reward + self.discount_factor * max_next_q_value - old_q_value
        )
        
        self.q_table[(state, move)] = new_q_value
        
        # Update best moves memory
        if reward > 0:
            self.best_moves_memory[state] = move
        
        # Prune Q-table if it gets too large
        self.prune_q_table()
    
    def prune_q_table(self):
        """
        Limit the size of Q-table by removing least important entries.
        """
        if len(self.q_table) > self.max_q_table_size:
            # Sort by absolute Q-value and keep top entries
            sorted_q_table = sorted(
                self.q_table.items(), 
                key=lambda x: abs(x[1]), 
                reverse=True
            )
            self.q_table = dict(sorted_q_table[:self.max_q_table_size])
    
    def train(self, num_episodes=5000, verbose=True):
        """
        Train the AI with comprehensive progress tracking.
        
        Args:
            num_episodes (int): Number of training episodes
            verbose (bool): Whether to print detailed progress
        
        Returns:
            dict: Training progress statistics
        """
        start_time = time.time()
        self.training_progress['total_episodes'] = num_episodes
        
        for episode in range(num_episodes):
            # Reset board and game state
            self.board = board_and_fields.Board()
            turn = 'w'
            total_episode_reward = 0
            move_count = 0
            max_moves = 200
            
            while move_count < max_moves:
                # Get possible moves
                possible_moves = self.get_possible_moves(turn)
                
                if not possible_moves:
                    if verbose:
                        self.logger.warning(f"No moves possible for {turn} in episode {episode}")
                    break
                
                # Store current state before move
                current_state = self.get_board_state()
                
                # Choose and execute move
                move = self.choose_move(turn)
                move_result = engine.tryMove(turn, self.board, *move)
                
                if not move_result:
                    continue
                
                # Get next state and reward
                next_state = self.get_board_state()
                reward = self.calculate_reward(turn)
                
                # Accumulate episode reward
                total_episode_reward += reward
                
                # Update Q-table
                self.update_q_table(current_state, move, reward, next_state)
                
                # Check game end conditions
                result = engine.afterMove(turn, self.board, *move)
                if result[0] in ['checkmate', 'stalemate']:
                    break
                
                # Switch turns
                turn = 'b' if turn == 'w' else 'w'
                move_count += 1
            
            # Update training progress
            self.training_progress['completed_episodes'] += 1
            self.training_progress['average_reward'] = (
                self.training_progress['average_reward'] * episode + total_episode_reward
            ) / (episode + 1)
            
            self.training_progress['best_reward'] = max(
                self.training_progress['best_reward'], 
                total_episode_reward
            )
            
            # Gradually reduce exploration rate
            self.exploration_rate = max(
                0.01, 
                self.exploration_rate * self.training_progress['exploration_decay_rate']
            )
            
            # Verbose output
            if verbose and episode % 100 == 0:
                self.logger.info(
                    f"Episode {episode}: "
                    f"Total Reward = {total_episode_reward}, "
                    f"Exploration Rate = {self.exploration_rate:.4f}"
                )
        
        # Calculate total training time
        total_time = time.time() - start_time
        self.training_progress['total_training_time'] = total_time
        
        return self.training_progress
    
    def evaluate_model(self, num_test_games=100):
        """
        Evaluate the trained model's performance.
        
        Args:
            num_test_games (int): Number of test games to play
        
        Returns:
            dict: Performance metrics
        """
        wins = 0
        draws = 0
        losses = 0
        
        for _ in range(num_test_games):
            # Placeholder for actual game result determination
            # You'll need to implement game simulation logic
            result = self.simulate_game()
            
            if result == 'win':
                wins += 1
            elif result == 'draw':
                draws += 1
            else:
                losses += 1
        
        return {
            'win_rate': wins / num_test_games,
            'draw_rate': draws / num_test_games,
            'loss_rate': losses / num_test_games
        }
    
    def simulate_game(self):
        """
        Simulate a single game to test model performance.
        
        Returns:
            str: Game result ('win', 'loss', 'draw')
        """
        # This is a placeholder. You'll need to implement actual game simulation
        # based on your specific chess engine and game rules
        return random.choice(['win', 'loss', 'draw'])

# Example usage
def main():
    # Initialize the AI
    ai = ChessQLearningAI(board_and_fields.Board())
    
    # Train the model
    print("Starting training...")
    training_progress = ai.train(num_episodes=50000)  # Reduced for testing
    print("Training completed. Progress:", training_progress)
    
    # Evaluate the model
    performance = ai.evaluate_model()
    print("Model Performance:", performance)

if __name__ == "__main__":
    main()