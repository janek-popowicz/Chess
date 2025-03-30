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
    # Initialize board and AI
    board = Board()
    ai = ml.ChessQLearningAI(board)
    
    # Run test training first
    print("Starting test training (200 episodes)...")
    if ai.test_training():
        print("Test training successful!")
        
        # Ask user if they want to continue with full training
        response = input("Continue with full training (50K episodes)? [y/N]: ")
        if response.lower() == 'y':
            print("Starting full training...")
            ai.full_training()
        else:
            print("Training stopped after test phase")
    else:
        print("Test training failed!")

if __name__ == "__main__":
    main()