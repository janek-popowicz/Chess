import pygame
import json

import sys
import os

# Dodaj katalog główny do sys.path, jeśli nie jest już w nim zawarty
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import normal_games.normal_game
import normal_games.test_mode_normal_game
import custom_board_game.board_maker
import custom_board_game.normal_game_custom_board
import settings
import grandmaster.pgn_to_fen as pgn_to_fen

pgn_to_fen.main()