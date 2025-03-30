# engine/ml_chess_ai.py
import os
import time
import numpy as np
import copy
import random
from engine.board_and_fields import Board

class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size, load_path=None):
        if load_path and os.path.exists(load_path):
            self.load(load_path)
        else:
            self.W1 = np.random.randn(input_size, hidden_size) * 0.01
            self.b1 = np.zeros(hidden_size)
            self.W2 = np.random.randn(hidden_size, output_size) * 0.01
            self.b2 = np.zeros(output_size)
    
    def forward(self, X):
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = np.tanh(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        return self.z2
    
    def backward(self, X, y_true, learning_rate=0.001):
        m = X.shape[0]
        delta2 = (self.z2 - y_true) / m
        dW2 = np.dot(self.a1.T, delta2)
        db2 = np.sum(delta2, axis=0)
        delta1 = np.dot(delta2, self.W2.T) * (1 - np.square(self.a1))
        dW1 = np.dot(X.T, delta1)
        db1 = np.sum(delta1, axis=0)
        
        self.W1 -= learning_rate * dW1
        self.b1 -= learning_rate * db1
        self.W2 -= learning_rate * dW2
        self.b2 -= learning_rate * db2
    
    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        np.savez(path, W1=self.W1, b1=self.b1, W2=self.W2, b2=self.b2)
    
    def load(self, path):
        data = np.load(path)
        self.W1 = data['W1']
        self.b1 = data['b1']
        self.W2 = data['W2']
        self.b2 = data['b2']

class ChessAI:
    def __init__(self, model_name="ml"):
        self.model_path = f"ai_model/{model_name}.npz"
        self.nn = NeuralNetwork(768, 256, 1, load_path=self.model_path)
        self.memory = []
        self.time_limit = 10
    
    def board_to_input(self, board):
        piece_encoding = {
            None: [0]*12,
            'wP': [1,0,0,0,0,0,0,0,0,0,0,0],
            'wN': [0,1,0,0,0,0,0,0,0,0,0,0],
            'wB': [0,0,1,0,0,0,0,0,0,0,0,0],
            'wR': [0,0,0,1,0,0,0,0,0,0,0,0],
            'wQ': [0,0,0,0,1,0,0,0,0,0,0,0],
            'wK': [0,0,0,0,0,1,0,0,0,0,0,0],
            'bP': [0,0,0,0,0,0,1,0,0,0,0,0],
            'bN': [0,0,0,0,0,0,0,1,0,0,0,0],
            'bB': [0,0,0,0,0,0,0,0,1,0,0,0],
            'bR': [0,0,0,0,0,0,0,0,0,1,0,0],
            'bQ': [0,0,0,0,0,0,0,0,0,0,1,0],
            'bK': [0,0,0,0,0,0,0,0,0,0,0,1]
        }
        
        input_vector = []
        for row in board.board_state:
            for field in row:
                piece_code = field.figure.return_figure() if field.figure else None
                input_vector.extend(piece_encoding.get(piece_code, [0]*12))
        return np.array(input_vector).reshape(1, -1)
    
    def get_best_move(self, board, color):
        start_time = time.time()
        best_move = None
        best_score = -np.inf
        
        for move in self.get_all_moves(board, color):
            if time.time() - start_time > self.time_limit:
                break
                
            new_board = self.simulate_move(board, move)
            X = self.board_to_input(new_board)
            score = self.nn.forward(X)[0][0]
            
            self.memory.append((X, score))
            
            if score > best_score:
                best_score = score
                best_move = move
                
        return best_move or random.choice(self.get_all_moves(board, color))
    
    def train(self, game_result):
        if not self.memory:
            return
            
        X = np.vstack([x for x, _ in self.memory])
        y = np.array([game_result]*len(self.memory)).reshape(-1, 1)
        self.nn.backward(X, y)
        self.save_model()
        self.memory = []
    
    def save_model(self):
        self.nn.save(self.model_path)
    
    def get_all_moves(self, board, color):
        moves = []
        legal_moves = board.get_all_moves(color)
        for start, targets in legal_moves.items():
            for target in targets:
                moves.append((start[0], start[1], target[0], target[1]))
        return moves
    
    def simulate_move(self, board, move):
        new_board = copy.deepcopy(board)
        y1, x1, y2, x2 = move
        new_board.make_move(y1, x1, y2, x2)
        return new_board