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

def play_menu(ai=None):
    """Menu for playing against AI"""
    while True:
        print("\n=== Chess AI Game Menu ===")
        print("1. Play against AI")
        print("2. Watch AI vs AI")
        print("3. Load different model")
        print("4. Return to main menu")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1":
            if not ai:
                print("\nNo AI model loaded! Please load a model first.")
                ai = load_model_menu(Path("models"))
                if not ai:
                    continue
            ml_game.play_against_ai(ai)
        elif choice == "2":
            if not ai:
                print("\nNo AI model loaded! Please load a model first.")
                ai = load_model_menu(Path("models"))
                if not ai:
                    continue
            ml_game.watch_ai_game(ai)
        elif choice == "3":
            ai = load_model_menu(Path("models"))
        elif choice == "4":
            break
        else:
            print("\nInvalid choice. Please try again.")

def main():
    while True:
        print("\n=== Chess AI Training System ===")
        print("1. Start new training (4M episodes)")
        print("2. Run test training (200 episodes)")
        print("3. Load and play with trained model")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1":
            # Initialize board and AI
            board = Board()
            ai = ml.ChessQLearningAI(board)
            
            print("\nStarting full training (4M episodes)...")
            start_time = time.time()
            total_episodes = 4_000_000
            checkpoint_interval = 100_000
            batch_size = 32
            report_interval = 1000
            
            try:
                episode_count = 0
                total_loss = 0
                valid_episodes = 0
                
                while episode_count < total_episodes:
                    batch_start = time.time()
                    
                    # Train in smaller batches
                    for _ in range(checkpoint_interval // batch_size):
                        loss = ai.train(batch_size)
                        if loss > 0:
                            total_loss += loss
                            valid_episodes += 1
                        episode_count += batch_size
                        
                        # Show detailed progress regularly
                        if episode_count % report_interval == 0:
                            avg_loss = total_loss / valid_episodes if valid_episodes > 0 else 0
                            print(f"\nEpisodes: {episode_count:,}")
                            print(f"Average Loss: {avg_loss:.4f}")
                            print(f"Valid Episodes: {valid_episodes}")
                            total_loss = 0
                            valid_episodes = 0
                    
                    # Checkpoint saving and validation
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    checkpoint_name = f"model_checkpoint_{episode_count}_{timestamp}.pt"
                    ai.save_model(checkpoint_name)
                    
                    # Progress statistics
                    progress = episode_count / total_episodes
                    elapsed = time.time() - start_time
                    eta = (elapsed / progress) * (1 - progress) if progress > 0 else 0
                    batch_time = time.time() - batch_start
                    
                    print(f"\n{'='*20} Training Progress {'='*20}")
                    print(f"Progress: {progress:.1%}")
                    print(f"Episodes: {episode_count:,}/{total_episodes:,}")
                    print(f"Time Elapsed: {elapsed/3600:.1f}h")
                    print(f"Estimated Time Remaining: {eta/3600:.1f}h")
                    print(f"Last Batch Time: {batch_time/60:.1f}m")
                    
                    # Resource monitoring
                    monitor_resources()
                    
                    # Validation with detailed metrics
                    print("\nRunning validation...")
                    win_rate = ai.validate(num_games=50)
                    print(f"Current Win Rate: {win_rate:.1%}")
                    print(f"{'='*50}\n")
                    
                print("\nFull training completed successfully!")
                
                # Save final model with metadata
                final_name = f"final_model_4M_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
                ai.save_model(final_name)
                
            except KeyboardInterrupt:
                print("\nTraining interrupted by user!")
                interrupt_name = f"interrupted_{episode_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
                ai.save_model(interrupt_name)
            except Exception as e:
                print(f"\nTraining error: {e}")
                backup_name = f"emergency_{episode_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
                ai.save_model(backup_name)
                
        elif choice == "2":
            board = Board()
            ai = ml.ChessQLearningAI(board)
            print("\nStarting test training (200 episodes)...")
            if ai.test_training():
                print("\nTest training successful!")
                response = input("Continue with full training? [y/N]: ")
                if response.lower() == 'y':
                    print("\nStarting full training (4M episodes)...")
                    start_time = time.time()
                    total_episodes = 4_000_000
                    checkpoint_interval = 100_000
                    batch_size = 32
                    report_interval = 1000
                    
                    try:
                        episode_count = 0
                        total_loss = 0
                        valid_episodes = 0
                        
                        while episode_count < total_episodes:
                            batch_start = time.time()
                            
                            # Train in smaller batches
                            for _ in range(checkpoint_interval // batch_size):
                                loss = ai.train(batch_size)
                                if loss > 0:
                                    total_loss += loss
                                    valid_episodes += 1
                                episode_count += batch_size
                                
                                # Show detailed progress regularly
                                if episode_count % report_interval == 0:
                                    avg_loss = total_loss / valid_episodes if valid_episodes > 0 else 0
                                    print(f"\nEpisodes: {episode_count:,}")
                                    print(f"Average Loss: {avg_loss:.4f}")
                                    print(f"Valid Episodes: {valid_episodes}")
                                    total_loss = 0
                                    valid_episodes = 0
                            
                            # Checkpoint saving and validation
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            checkpoint_name = f"model_checkpoint_{episode_count}_{timestamp}.pt"
                            ai.save_model(checkpoint_name)
                            
                            # Progress statistics
                            progress = episode_count / total_episodes
                            elapsed = time.time() - start_time
                            eta = (elapsed / progress) * (1 - progress) if progress > 0 else 0
                            batch_time = time.time() - batch_start
                            
                            print(f"\n{'='*20} Training Progress {'='*20}")
                            print(f"Progress: {progress:.1%}")
                            print(f"Episodes: {episode_count:,}/{total_episodes:,}")
                            print(f"Time Elapsed: {elapsed/3600:.1f}h")
                            print(f"Estimated Time Remaining: {eta/3600:.1f}h")
                            print(f"Last Batch Time: {batch_time/60:.1f}m")
                            
                            # Resource monitoring
                            monitor_resources()
                            
                            # Validation with detailed metrics
                            print("\nRunning validation...")
                            win_rate = ai.validate(num_games=50)
                            print(f"Current Win Rate: {win_rate:.1%}")
                            print(f"{'='*50}\n")
                            
                        print("\nFull training completed successfully!")
                        
                        # Save final model with metadata
                        final_name = f"final_model_4M_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
                        ai.save_model(final_name)
                        
                    except KeyboardInterrupt:
                        print("\nTraining interrupted by user!")
                        interrupt_name = f"interrupted_{episode_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
                        ai.save_model(interrupt_name)
                    except Exception as e:
                        print(f"\nTraining error: {e}")
                        backup_name = f"emergency_{episode_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
                        ai.save_model(backup_name)
                else:
                    print("Training stopped after test phase")
            else:
                print("\nTest training failed!")
                
        elif choice == "3":
            ai = load_model_menu(Path("models"))
            if ai:
                play_menu(ai)
            
        elif choice == "4":
            print("\nExiting...")
            break
            
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    # Create models directory if it doesn't exist
    Path("models").mkdir(exist_ok=True)
    main()