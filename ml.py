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
        """Enhanced reward calculation"""
        reward = 0
        
        # Material value
        piece_values = {
            'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
            'p': -100, 'n': -320, 'b': -330, 'r': -500, 'q': -900, 'k': -20000
        }
        
        # Calculate material balance
        material_reward = 0
        for row in self.board.board_state:
            for field in row:
                if field.figure:
                    material_reward += piece_values.get(field.figure.return_figure(), 0)
        
        # Position rewards
        position_reward = 0
        center_squares = [(3,3), (3,4), (4,3), (4,4)]
        for y, x in center_squares:
            field = self.board.board_state[y][x]
            if field.figure and field.figure.color == turn:
                position_reward += 50  # Bonus for controlling center
        
        # Game state rewards
        if self.board.incheck:
            reward -= 200 if turn == 'w' else 200  # Penalty for being in check
        
        # Normalize rewards
        total_reward = (material_reward + position_reward + reward) / 100.0
        
        return total_reward
    
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
    
    def train(self, num_episodes=500, verbose=True):
        """
        Train the AI with comprehensive progress tracking and proper reward accumulation.
        """
        start_time = time.time()
        self.training_progress['total_episodes'] = num_episodes
        
        for episode in range(num_episodes):
            # Reset board and game state
            self.board = board_and_fields.Board()
            turn = 'w'
            total_episode_reward = 0  # Reset episode reward
            move_count = 0
            max_moves = 200
            
            while move_count < max_moves:
                possible_moves = self.get_possible_moves(turn)
                
                if not possible_moves:
                    break
                
                current_state = self.get_board_state()
                move = self.choose_move(turn)
                
                # Store board state before move
                previous_board = copy.deepcopy(self.board)
                
                # Execute move
                move_result = engine.tryMove(turn, self.board, *move)
                
                if not move_result:
                    continue
                
                # Calculate immediate reward
                reward = self.calculate_reward(turn)
                total_episode_reward += reward  # Accumulate reward properly
                
                next_state = self.get_board_state()
                self.update_q_table(current_state, move, reward, next_state)
                
                # Check for game end and add final reward
                result = engine.afterMove(turn, self.board, *move)
                if result[0] == 'checkmate':
                    total_episode_reward += 1000 if turn == 'w' else -1000
                    break
                elif result[0] == 'stalemate':
                    total_episode_reward += 0  # Neutral reward for stalemate
                    break
                
                turn = 'b' if turn == 'w' else 'w'
                move_count += 1
            
            # Update training progress with proper reward averaging
            self.training_progress['completed_episodes'] += 1
            if episode == 0:
                self.training_progress['average_reward'] = total_episode_reward
            else:
                self.training_progress['average_reward'] = (
                    self.training_progress['average_reward'] * 0.95 + 
                    total_episode_reward * 0.05
                )
            
            self.training_progress['best_reward'] = max(
                self.training_progress['best_reward'], 
                total_episode_reward
            )
            
            # Update exploration rate
            self.exploration_rate = max(
                0.01, 
                self.exploration_rate * self.training_progress['exploration_decay_rate']
            )
            
            # Verbose output
            if verbose and episode % 100 == 0:
                self.logger.info(
                    f"Episode {episode}: "
                    f"Total Reward = {total_episode_reward:.2f}, "
                    f"Avg Reward = {self.training_progress['average_reward']:.2f}, "
                    f"Best = {self.training_progress['best_reward']:.2f}, "
                    f"Exploration = {self.exploration_rate:.4f}"
                )
        
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
    def play_interactive_game(self, human_color='w'):
        """
        Play an interactive chess game against the trained AI.
        
        Args:
            human_color (str): Color of the human player ('w' or 'b')
        """
        # Reset the board
        self.board = board_and_fields.Board()
        current_turn = 'w'
        
        print("Welcome to Chess AI Interaction!")
        print(f"You are playing as {human_color} (White or Black)")
        print("Enter moves in algebraic notation (e.g., 'e2e4')")
        
        while True:
            # Display current board state
            self.display_board()
            
            # Check if it's human's turn
            if current_turn == human_color:
                try:
                    # Get human move
                    human_move = self.get_human_move(current_turn)
                    
                    # Try to execute human move
                    move_result = engine.tryMove(current_turn, self.board, *human_move)
                    
                    if not move_result:
                        print("Invalid move. Try again.")
                        continue
                    
                    # Check game end conditions
                    result = engine.afterMove(current_turn, self.board, *human_move)
                    
                    if result[0] in ['checkmate', 'stalemate']:
                        print(f"Game over: {result[0]}")
                        break
                
                except Exception as e:
                    print(f"Error processing your move: {e}")
                    continue
            
            # AI's turn
            else:
                # Use trained model to choose move
                ai_move = self.choose_move(current_turn)
                
                print(f"AI moves: {self.format_move(ai_move)}")
                
                # Execute AI move
                move_result = engine.tryMove(current_turn, self.board, *ai_move)
                
                # Check game end conditions
                result = engine.afterMove(current_turn, self.board, *ai_move)
                
                if result[0] in ['checkmate', 'stalemate']:
                    print(f"Game over: {result[0]}")
                    break
            
            # Switch turns
            current_turn = 'b' if current_turn == 'w' else 'w'
    
    def get_human_move(self, turn):
        """
        Get a valid move from human input.
        
        Args:
            turn (str): Current player's turn
        
        Returns:
            tuple: Move as (start_y, start_x, target_y, target_x)
        """
        while True:
            move = input("Enter your move (e.g., 'e2e4'): ").lower().strip()
            
            # Convert algebraic notation to board coordinates
            try:
                start_x = ord(move[0]) - ord('a')
                start_y = 8 - int(move[1])
                target_x = ord(move[2]) - ord('a')
                target_y = 8 - int(move[3])
                
                # Validate move is in possible moves
                possible_moves = self.get_possible_moves(turn)
                
                # Check if the move is in possible moves
                if (start_y, start_x, target_y, target_x) in possible_moves:
                    return (start_y, start_x, target_y, target_x)
                else:
                    print("Invalid move. Try again.")
            
            except (IndexError, ValueError):
                print("Invalid move format. Use algebraic notation like 'e2e4'.")
    
    def display_board(self):
        """
        Display the current board state in a readable format.
        """
        print("\n  a b c d e f g h")
        for y, row in enumerate(self.board.board_state):
            row_display = [f"{8-y} "]
            for field in row:
                if field.figure:
                    row_display.append(field.figure.return_figure())
                else:
                    row_display.append('.')
            print(' '.join(row_display))
        print()
    
    def format_move(self, move):
        """
        Convert move tuple to algebraic notation.
        
        Args:
            move (tuple): Move as (start_y, start_x, target_y, target_x)
        
        Returns:
            str: Algebraic notation move
        """
        start_file = chr(move[1] + ord('a'))
        start_rank = 8 - move[0]
        target_file = chr(move[3] + ord('a'))
        target_rank = 8 - move[2]
        
        return f"{start_file}{start_rank}{target_file}{target_rank}"

    def save_model(self, filename='chess_model.pkl'):
        """Save the trained model to a file"""
        import pickle
        model_data = {
            'q_table': self.q_table,
            'best_moves_memory': self.best_moves_memory,
            'training_progress': self.training_progress
        }
        try:
            with open(filename, 'wb') as f:
                pickle.dump(model_data, f)
            print(f"Model successfully saved to {filename}")
        except Exception as e:
            print(f"Error saving model: {e}")

    def load_model(self, filename='chess_model.pkl'):
        """Load a previously trained model"""
        import pickle
        try:
            with open(filename, 'rb') as f:
                model_data = pickle.load(f)
                self.q_table = model_data['q_table']
                self.best_moves_memory = model_data['best_moves_memory']
                self.training_progress = model_data.get('training_progress', self.training_progress)
            print(f"Model successfully loaded from {filename}")
            return True
        except FileNotFoundError:
            print("No saved model found")
            return False
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

# Example usage
def main():
    ai = ChessQLearningAI(board_and_fields.Board())
    
    while True:
        print("\nChess AI Menu:")
        print("1. Train New Model")
        print("2. Load Existing Model")
        print("3. Play as White")
        print("4. Play as Black")
        print("5. Save Current Model")
        print("6. Exit")
        
        choice = input("Enter your choice (1-6): ")
        
        if choice == '1':
            print("Starting training...")
            training_progress = ai.train(num_episodes=500000)
            print("Training completed. Progress:", training_progress)
            # Auto-save after training
            ai.save_model()
        elif choice == '2':
            ai.load_model()
        elif choice == '3':
            ai.play_interactive_game(human_color='w')
        elif choice == '4':
            ai.play_interactive_game(human_color='b')
        elif choice == '5':
            ai.save_model()
        elif choice == '6':
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
# Test the Q-learning AI