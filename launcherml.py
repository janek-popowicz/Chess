import sys
import os
from datetime import datetime  # Import for timestamp
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ai_model.ml as ml
import ai_model.ml_game as ml_game
from engine.board_and_fields import Board  # Direct import of Board
from pathlib import Path
import torch
import time
import psutil

def monitor_resources():
    """Monitor system resources during training"""
    process = psutil.Process()
    memory = process.memory_info().rss / 1024 / 1024  # MB
    cpu_percent = process.cpu_percent()
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.memory_allocated() / 1024 / 1024  # MB
        print(f"GPU Memory: {gpu_memory:.1f}MB | RAM: {memory:.1f}MB | CPU: {cpu_percent}%")
    else:
        print(f"RAM: {memory:.1f}MB | CPU: {cpu_percent}%")

def load_model_menu(models_dir):
    """Handle model loading with better error handling and feedback"""
    # Get all model files with absolute paths
    model_files = list(models_dir.glob("*.pt")) + list(models_dir.glob("*.pth"))
    
    if not model_files:
        print("\nNo saved models found in the 'models' directory!")
        return None
        
    # Display available models
    print("\nAvailable models:")
    for i, model_file in enumerate(model_files, 1):
        print(f"{i}. {model_file.name}")
        
    while True:
        try:
            choice = input("\nEnter model number to load (or 'q' to cancel): ")
            if choice.lower() == 'q':
                return None
                
            model_idx = int(choice) - 1
            if 0 <= model_idx < len(model_files):
                model_path = model_files[model_idx].absolute()  # Get absolute path
                ai = ml.ChessQLearningAI(Board())
                
                try:
                    if ai.load_model(str(model_path)):
                        print(f"\nModel '{model_path.name}' loaded successfully!")
                        return ai
                    else:
                        print(f"\nFailed to load model '{model_path.name}'.")
                        return None
                except Exception as e:
                    print(f"\nError loading model: {e}")
                    return None
            else:
                print("\nInvalid model number. Please try again.")
        except ValueError:
            print("\nPlease enter a valid number.")
        except Exception as e:
            print(f"\nError loading model: {e}")
            return None

def main():
    """
    Enhanced launcher for Chess AI with training, playing, and model management options.
    """
    ai = None
    # Create models directory in project root
    models_dir = Path(__file__).parent / "models"
    models_dir.mkdir(exist_ok=True)

    while True:
        print("\nChess AI Launcher Menu:")
        print("1. Train New Model (Test training for 500 episodes)")
        print("2. Load Existing Model")
        print("3. Play as White")
        print("4. Play as Black")
        print("5. Play Chess Game (Pygame)")
        print("6. Evaluate Model")
        print("7. Save Current Model")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ")
        
        if choice == '1':
            print("\nStarting test training (500 episodes)...")
            
            # Single phase training configuration for testing
            phases = [
                {"episodes": 500, "learning_rate": 0.001, "message": "Test training phase..."}
            ]
            
            ai = ml.ChessQLearningAI(Board())
            
            for i, phase in enumerate(phases, 1):
                print(f"\n{phase['message']}")
                ai.learning_rate = phase["learning_rate"]
                training_progress = ai.train(num_episodes=phase["episodes"])
                
                # Save model with correct path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                checkpoint_name = models_dir / f"model_test_{timestamp}.pt"
                ai.save_model(str(checkpoint_name))
                print(f"\nTraining completed and saved as '{checkpoint_name.name}'")
                print(f"Episodes trained: {phase['episodes']}")
            
            print("\nTest training completed successfully!")
            
        elif choice == '2':
            if not models_dir.exists():
                print("\nModels directory not found! Creating one...")
                models_dir.mkdir(exist_ok=True)
                print("\nNo saved models found! Please train a model first.")
                continue
                
            ai = load_model_menu(models_dir)
            if ai is None:
                print("\nModel loading cancelled or failed.")
                continue
                
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
            print("\nSelect AI type:")
            print("1. Machine Learning")
            print("2. Minimax")
            print("3. Monte Carlo Tree Search")
            ai_choice = input("\nEnter choice (1-3): ")
            
            human_color = input("\nChoose your color (w/b): ").lower()
            if human_color not in ['w', 'b']:
                human_color = 'w'
            
            from algorithms.algorithms_game import main as start_game
            
            if ai_choice == '1':
                if ai is None:
                    print("\nPlease load or train a model first!")
                    continue
                start_game('ml', ai_instance=ai, human_color=human_color)
            elif ai_choice == '2':
                start_game('minimax', human_color=human_color)
            elif ai_choice == '3':
                start_game('mcts', human_color=human_color)
            else:
                print("\nInvalid choice!")
            
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
                
            filename = input("\nEnter filename for the model (leave blank for timestamped name): ")
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"model_{timestamp}.pt"
            elif not filename.endswith('.pt'):
                filename += '.pt'
            ai.save_model(filename)
            print(f"\nModel saved as '{filename}'")
            
        elif choice == '8':
            print("\nThanks for using Chess AI!")
            break
            
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    # Set up optimal PyTorch settings
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True

    # Training configuration
    EPISODES_PER_EPOCH = 1000
    TOTAL_EPOCHS = 50  # Total 50,000 episodes
    VALIDATE_EVERY = 1000
    SAVE_EVERY = 5000
    
    # Initialize board and AI
    board = Board()
    ai = ml.ChessQLearningAI(board, learning_rate=0.0001)  # Lower learning rate for stability
    
    try:
        # Load existing model if available
        if ai.load_model("latest_model.pt"):
            print("Loaded existing model, continuing training...")
        
        best_win_rate = 0.0
        start_time = time.time()
        
        for epoch in range(TOTAL_EPOCHS):
            print(f"\nEpoch {epoch + 1}/{TOTAL_EPOCHS}")
            print("-" * 50)
            
            # Train for one epoch
            ai.train(EPISODES_PER_EPOCH)
            
            # Monitor system resources
            monitor_resources()
            
            # Validate and save progress
            if (epoch + 1) % (VALIDATE_EVERY // EPISODES_PER_EPOCH) == 0:
                win_rate = ai.validate(num_games=50)
                
                # Save if improved
                if win_rate > best_win_rate:
                    best_win_rate = win_rate
                    ai.save_model(f"best_model_winrate_{win_rate:.2f}.pt")
                
            # Regular checkpoint save
            if (epoch + 1) % (SAVE_EVERY // EPISODES_PER_EPOCH) == 0:
                ai.save_model(f"checkpoint_epoch_{epoch+1}.pt")
                ai.save_model("latest_model.pt")
            
            # Print progress
            elapsed = time.time() - start_time
            print(f"Time elapsed: {elapsed/3600:.1f}h")
            print(f"Best win rate so far: {best_win_rate:.2%}")
            
    except KeyboardInterrupt:
        print("\nTraining interrupted by user. Saving final model...")
        ai.save_model("interrupted_model.pt")
    except Exception as e:
        print(f"\nError during training: {e}")
        ai.save_model("emergency_save.pt")
    finally:
        # Always save final model
        ai.save_model("final_model.pt")
        print("\nTraining completed!")