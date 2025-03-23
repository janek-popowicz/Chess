import sys
import os

# Add the project root to the path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import algorithms.minimax as minimax

def main():
    # Create a Minimax instance
    minimax_object = minimax.Minimax()
    
    # Get the best move
    best_move = minimax_object.get_best_move()
    
    # Print the result
    print(f"The best move is: {best_move}")
    
    return best_move

if __name__ == "__main__":
    main()