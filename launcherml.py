import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ai_model.ml as ml
import ai_model.ml_game as ml_game

def main():
    """
    Launcher for Chess AI: Choose between training the model or playing the game.
    """
    while True:
        print("\nLauncher Menu:")
        print("1. Train New Model")
        print("2. Load Existing Model")
        print("3. Play Chess Game (Pygame)")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            print("Starting training...")
            ai = ml.ChessQLearningAI(ml.board_and_fields.Board())
            training_progress = ai.train(num_episodes=350)
            print("Training completed. Progress:", training_progress)
            ai.save_model()  # Auto-save after training
        elif choice == '2':
            ai = ml.ChessQLearningAI(ml.board_and_fields.Board())
            ai.load_model()
        elif choice == '3':
            ml_game.main()  # Launch the Pygame chess game
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()