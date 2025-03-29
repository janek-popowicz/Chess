import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ai_model.ml as ml
import ai_model.ml_game as ml_game
from engine.board_and_fields import Board  # Direct import of Board
from pathlib import Path

def main():
    """
    Enhanced launcher for Chess AI with training, playing, and model management options.
    """
    ai = None
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)

    while True:
        print("\nChess AI Launcher Menu:")
        print("1. Train New Model (Multi-phase)")
        print("2. Load Existing Model")
        print("3. Play as White")
        print("4. Play as Black")
        print("5. Play Chess Game (Pygame)")
        print("6. Evaluate Model")
        print("7. Save Current Model")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ")
        
        if choice == '1':
            print("\nStarting intensive training (this may take a while)...")
            
            # Training phases configuration
            phases = [
                {"episodes": 1500, "learning_rate": 0.001, "message": "Phase 1: Basic patterns and openings..."},
                {"episodes": 4000, "learning_rate": 0.0001, "message": "Phase 4: Fine-tuning..."},
                {"episodes": 5000, "learning_rate": 0.00005, "message": "Phase 5: Mastering endgames..."},
                {"episodes": 15000, "learning_rate": 0.00001, "message": "Phase 6: Advanced strategies..."},
            ]
            
            ai = ml.ChessQLearningAI(Board())  # Fixed instantiation
            
            for i, phase in enumerate(phases, 1):
                print(f"\n{phase['message']}")
                ai.learning_rate = phase["learning_rate"]
                training_progress = ai.train(num_episodes=phase["episodes"])
                
                # Save checkpoint after each phase
                checkpoint_name = f"model_phase_{i}"
                ai.save_model(checkpoint_name)
                print(f"Phase {i} completed and saved as '{checkpoint_name}'")
                
            print("\nTraining completed successfully!")
            
        elif choice == '2':
            model_files = list(models_dir.glob("*.pt"))
            if not model_files:
                print("\nNo saved models found! Please train a model first.")
                continue
                
            print("\nAvailable models:")
            for i, model_file in enumerate(model_files, 1):
                print(f"{i}. {model_file.stem}")
                
            try:
                model_idx = int(input("\nEnter model number to load: ")) - 1
                model_path = model_files[model_idx]
                ai = ml.ChessQLearningAI(Board())
                ai.load_model(str(model_path))
                print(f"\nModel '{model_path.stem}' loaded successfully!")
            except (ValueError, IndexError):
                print("\nInvalid selection!")
                
        elif choice in ['3', '4']:
            if ai is None:
                print("\nPlease load or train a model first!")
                continue
                
            human_color = 'w' if choice == '3' else 'b'
            print("\nStarting game... (Ctrl+C to exit)")
            try:
                ai.play_interactive_game(human_color=human_color)
            except KeyboardInterrupt:
                print("\nGame interrupted!")
                
        elif choice == '5':
            if ai is None:
                print("\nPlease load or train a model first!")
                continue
            ml_game.main(ai)  # Pass the AI instance to the game
            
        elif choice == '6':
            if ai is None:
                print("\nPlease load or train a model first!")
                continue
                
            print("\nEvaluating model performance...")
            results = ai.evaluate_model(num_games=50)
            print("\nEvaluation Results:")
            print(f"Games played: {results['games']}")
            print(f"Win rate: {results['win_rate']:.1f}%")
            print(f"Draw rate: {results['draw_rate']:.1f}%")
            print(f"Average move quality: {results['avg_move_quality']:.2f}")
            
        elif choice == '7':
            if ai is None:
                print("\nNo model to save! Please train or load a model first.")
                continue
                
            filename = input("\nEnter filename for the model: ")
            if not filename.endswith('.pt'):
                filename += '.pt'
            ai.save_model(filename)
            print(f"\nModel saved as '{filename}'")
            
        elif choice == '8':
            print("\nThanks for using Chess AI!")
            break
            
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()