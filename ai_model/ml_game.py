'''import pygame
import sys
import time
from pathlib import Path
from engine.board_and_fields import Board
from engine.engine import tryMove, afterMove, promotion
from graphics import *
from ..engine.pieces_loader import load_pieces  # Adjusted to relative import
from ml import ChessQLearningAI

def get_possible_moves(board, turn):
    """Get all possible moves for a given color"""
    moves = []
    for y in range(8):
        for x in range(8):
            piece = board.board_state[y][x].figure
            if piece and piece.color == turn:
                piece_moves = piece.get_moves(board, y, x)
                if piece_moves:
                    moves.extend([(y, x, my, mx) for my, mx in piece_moves])
    return moves

def main(player_color='w'):
    pygame.init()
    config = load_config()
    resolution = config["resolution"]
    width, height = map(int, resolution.split('x'))
    SQUARE_SIZE = height // 8

    # Setup display
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Chess ML Game")
    icon_logo = pygame.image.load('program_logo.png')
    pygame.display.set_icon(icon_logo)

    # Initialize game
    board = Board()
    pieces = load_pieces(SQUARE_SIZE)
    selected_square = None
    possible_moves = []
    turn = 'w'
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and turn == player_color:
                x, y = pygame.mouse.get_pos()
                col = x // SQUARE_SIZE
                row = y // SQUARE_SIZE
                
                if selected_square:
                    if tryMove(turn, board, selected_square[0], selected_square[1], row, col):
                        whatAfter, yPromotion, xPromotion = afterMove(turn, board)
                        if whatAfter == "promotion":
                            promotion(yPromotion, xPromotion, board, '10')
                        turn = 'b' if turn == 'w' else 'w'
                    selected_square = None
                    possible_moves = []
                else:
                    piece = board.board_state[row][col].figure
                    if piece and piece.color == player_color:
                        selected_square = (row, col)
                        possible_moves = get_possible_moves(board, turn)

        # AI move
        if turn != player_color and running:
            moves = get_possible_moves(board, turn)
            if moves:
                y1, x1, y2, x2 = moves[0]  # For now just take first move
                if tryMove(turn, board, y1, x1, y2, x2):
                    whatAfter, yPromotion, xPromotion = afterMove(turn, board)
                    if whatAfter == "promotion":
                        promotion(yPromotion, xPromotion, board, '10')
                    turn = 'b' if turn == 'w' else 'w'

        # Draw game state
        screen.fill((0, 0, 0))
        draw_board(screen, SQUARE_SIZE, board)
        draw_pieces(screen, board, SQUARE_SIZE, pieces)
        
        if selected_square:
            highlight_moves(screen, selected_square, possible_moves, SQUARE_SIZE)
            
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()'''