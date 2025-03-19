'''Nie mówie Ai bo szopen tak kazał'''

import random
import sys
import os
#szybki randomowy bot do testów pygame 

import engine.board_and_fields as board_and_fields
from engine.engine import *
import engine.figures as figures
import algorithms.evaluation as evaluation



def randombot(board, color):
    all_moves = board.get_legal_moves(board, color)
    if all_moves == []:
        return None
    move = random.choice(all_moves)
    return move
