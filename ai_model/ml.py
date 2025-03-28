import numpy as np
import random
import copy
import logging
import time
import engine.board_and_fields as board_and_fields
import engine.engine as engine

class ChessQLearningAI:
    def __init__(self, board, learning_rate=0.2, discount_factor=0.95, exploration_rate=1.0):
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
        self.position_memory = {}  # Add position memory
        
        # Training tracking
        self.training_progress = {
            'total_episodes': 0,
            'completed_episodes': 0,
            'average_reward': 0,
            'best_reward': float('-inf'),
            'exploration_decay_rate': 0.995  # Wolniejszy spadek eksploracji
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
                    state.append((field.figure.return_figure(), y, x))
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
        """Enhanced reward calculation with better position evaluation"""
        reward = 0
        
        # Improved piece values
        piece_values = {
            'P': 100, 'N': 350, 'B': 350, 'R': 525, 'Q': 1000, 'K': 10000,
            'p': -100, 'n': -350, 'b': -350, 'r': -525, 'q': -1000, 'k': -10000
        }
        
        # Positional bonuses for pieces
        position_bonus = {
            'P': [[0,  0,  0,  0,  0,  0,  0,  0],
                  [50, 50, 50, 50, 50, 50, 50, 50],
                  [10, 10, 20, 30, 30, 20, 10, 10],
                  [5,  5, 10, 25, 25, 10,  5,  5],
                  [0,  0,  0, 20, 20,  0,  0,  0],
                  [5, -5,-10,  0,  0,-10, -5,  5],
                  [5, 10, 10,-20,-20, 10, 10,  5],
                  [0,  0,  0,  0,  0,  0,  0,  0]],
            'N': [[-50,-40,-30,-30,-30,-30,-40,-50],
                  [-40,-20,  0,  0,  0,  0,-20,-40],
                  [-30,  0, 10, 15, 15, 10,  0,-30],
                  [-30,  5, 15, 20, 20, 15,  5,-30],
                  [-30,  0, 15, 20, 20, 15,  0,-30],
                  [-30,  5, 10, 15, 15, 10,  5,-30],
                  [-40,-20,  0,  5,  5,  0,-20,-40],
                  [-50,-40,-30,-30,-30,-30,-40,-50]]
        }

        # Calculate material and positional values
        material_reward = 0
        position_reward = 0
        
        for y, row in enumerate(self.board.board_state):
            for x, field in enumerate(row):
                if field.figure:
                    piece = field.figure.return_figure()
                    # Material value
                    material_reward += piece_values.get(piece, 0)
                    
                    # Positional value
                    if piece.upper() in position_bonus:
                        if piece.isupper():  # white
                            position_reward += position_bonus[piece.upper()][y][x]
                        else:  # black
                            position_reward += -position_bonus[piece.upper()][7-y][x]

        # Penalties for bad positions
        if self.board.incheck:
            reward -= 300  # Higher penalty for being in check
        
        # Center control
        center_squares = [(3,3), (3,4), (4,3), (4,4)]
        for y, x in center_squares:
            field = self.board.board_state[y][x]
            if field.figure and field.figure.color == turn:
                position_reward += 30
        
        # Combine all reward components
        total_reward = (material_reward + position_reward + reward) / 100.0
        
        # Add position memory
        state = self.get_board_state()
        if state in self.position_memory:
            total_reward -= 50  # Penalty for repeating positions
        
        self.position_memory[state] = self.position_memory.get(state, 0) + 1
        
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
        
        # Determine next turn based on current board state
        start_square = self.board.board_state[move[0]][move[1]]
        if start_square and start_square.figure:
            next_turn = 'b' if start_square.figure.color == 'w' else 'w'
        else:
            # If no figure found, alternate based on reward
            next_turn = 'b' if reward > 0 else 'w'
        
        # Find maximum Q-value for next state
        next_moves = self.get_possible_moves(next_turn)
        max_next_q_value = max(
            [self.q_table.get((next_state, nm), 0) for nm in next_moves] or [0]
        )
        
        # Q-learning update rule with adaptive learning
        new_q_value = old_q_value + self.learning_rate * (
            reward + self.discount_factor * max_next_q_value - old_q_value
        )
        
        self.q_table[(state, move)] = new_q_value
        
        # Update best moves memory if positive reward
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
        print("Enter moves in algebraic notation (e.g., 'e2e4')\n")
        
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
                        self.display_board()
                        break
                
                except Exception as e:
                    print(f"Error processing your move: {e}")
                    continue
            else:
                # AI's turn
                ai_move = self.choose_move(current_turn)
                print(f"AI moves: {self.format_move(ai_move)}")
                
                # Execute AI move
                move_result = engine.tryMove(current_turn, self.board, *ai_move)
                
                # Check game end conditions
                result = engine.afterMove(current_turn, self.board, *ai_move)
                if result[0] in ['checkmate', 'stalemate']:
                    print(f"Game over: {result[0]}")
                    self.display_board()
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
                if (start_y, start_x, target_y, target_x) in possible_moves:
                    return (start_y, start_x, target_y, target_x)
                else:
                    print("Invalid move. Try again.")
            except (IndexError, ValueError):
                print("Invalid move format. Use algebraic notation like 'e2e4'.")
    
    def display_board(self):
        """
        Display the chess board in a style similar to the provided screenshot.
        White is always at the bottom (ranks 1 -> 8 bottom to top).
        """
        print("\n   Current Board Position:\n")
        
        # Top file letters
        files_header = "     a    b    c    d    e    f    g    h"
        print(files_header)
        
        # Górna linia
        print("   +----+----+----+----+----+----+----+----+")
        
        # Rysowanie rzędów od 8 do 1
        for rank in range(8, 0, -1):
            row_str = f" {rank} |"
            for file in range(8):
                field = self.board.board_state[8 - rank][file]
                if field.figure:
                    color = 'w' if field.figure.color == 'w' else 'b'
                    # np. 'wP', 'bR', 'wK' itp.
                    piece_str = color + field.figure.return_figure()
                    row_str += f" {piece_str:2} |"
                else:
                    row_str += "    |"
            row_str += f" {rank}"
            print(row_str)
            print("   +----+----+----+----+----+----+----+----+")
        
        # Dolna linia z oznaczeniem kolumn
        print(files_header + "\n")
        
        # Jeśli jest check, wyświetl komunikat
        if self.board.incheck:
            print(" * CHECK! *")
        
        print("-" * 45)
    
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

def get_ai_move(board, color):
    """
    Get a move from the trained AI for the given board state and color.
    
    Args:
        board: The current chess board
        color (str): Color to play ('w' or 'b')
    
    Returns:
        tuple: Move as (start_y, start_x, target_y, target_x) or None if no move found
    """
    try:
        # Create AI instance
        ai = ChessQLearningAI(board)
        
        # Try to load trained model
        if not ai.load_model():
            print("No trained model found. Cannot make a move.")
            return None
            
        # Get move from AI
        move = ai.choose_move(color)
        return move
        
    except Exception as e:
        print(f"Error getting AI move: {e}")
        return None

# Example usage:
# move = get_ai_move(my_board, 'w')
# if move:
#     start_y, start_x, target_y, target_x = move
#     # Make the move on your board

def main():
    ai = ChessQLearningAI(board_and_fields.Board())
    
    while True:
        print("\nChess AI Menu:")
        print("1. Train New Model (Intensive)")
        print("2. Load Existing Model")
        print("3. Play as White")
        print("4. Play as Black")
        print("5. Save Current Model")
        print("6. Exit")
        
        choice = input("Enter your choice (1-6): ")
        
        if choice == '1':
            print("Starting intensive training (this may take a while)...")
            # Trening w fazach z rosnącą złożonością
            phases = [
                {"episodes": 1000, "learning_rate": 0.3, "message": "Phase 1: Basic patterns..."},
                {"episodes": 2000, "learning_rate": 0.2, "message": "Phase 2: Intermediate strategies..."},
                {"episodes": 3000, "learning_rate": 0.1, "message": "Phase 3: Advanced tactics..."},
                {"episodes": 4000, "learning_rate": 0.05, "message": "Phase 4: Fine-tuning..."}
            ]
            
            for phase in phases:
                print(phase["message"])
                ai.learning_rate = phase["learning_rate"]
                training_progress = ai.train(num_episodes=phase["episodes"], verbose=True)
                ai.save_model(f'chess_model_phase_{phases.index(phase)+1}.pkl')
            
            # Załaduj najlepszy model
            best_model = None
            best_reward = float('-inf')
            
            for i in range(len(phases)):
                ai.load_model(f'chess_model_phase_{i+1}.pkl')
                eval_results = ai.evaluate_model(num_test_games=100)
                if eval_results['win_rate'] > best_reward:
                    best_reward = eval_results['win_rate']
                    best_model = f'chess_model_phase_{i+1}.pkl'
            
            # Użyj najlepszego modelu
            if best_model:
                ai.load_model(best_model)
                ai.save_model('chess_model_best.pkl')
                print(f"Best model saved as chess_model_best.pkl (Win rate: {best_reward*100:.1f}%)")
        
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
