import algorithms.minimax as minimax

import sys
import os

# Dodaj katalog główny do sys.path, jeśli nie jest już w nim zawarty
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

minimax_object = minimax.Minimax()
move = minimax_object.get_best_move()