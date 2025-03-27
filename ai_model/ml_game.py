import pygame
import time
import engine.board_and_fields as board_and_fields
import engine.engine as engine
import engine.figures as figures
import graphics as graphics
import ai_model.ml as ml
import json 

def load_config():
    try:
        with open("config.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"volume": 0.5, "resolution": "1260x960", "icons": "default"}

def main():
    pygame.init()
    config = load_config()
    resolution = config["resolution"]
    width, height = map(int, resolution.split('x'))
    SQUARE_SIZE = height // 8

    # Setup display
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Chess vs ML AI")
    icon_logo = pygame.image.load('program_logo.png')
    pygame.display.set_icon(icon_logo)

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (100, 100, 100)
    YELLOW = pygame.Color("yellow")
    HIGHLIGHT_MOVES = (100, 200, 100)
    HIGHLIGHT_TAKES = (147, 168, 50)

    # Font and pieces setup
    font = pygame.font.Font(None, 36)
    icon_type = config["icons"]
    pieces_short = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    pieces = {}
    for piece in pieces_short:
        pieces[piece] = pygame.transform.scale(
            pygame.image.load(f"pieces/{icon_type}/{piece}.png"), 
            (SQUARE_SIZE-10, SQUARE_SIZE-10)
        )
    
    # Game state initialization
    running = True
    main_board = board_and_fields.Board()
    turn = 'w'
    selected_piece = None
    clock = pygame.time.Clock()
    player_turn = graphics.choose_color_dialog(screen, SQUARE_SIZE)

    # Interface texts
    texts = (
        (font.render("Turn: White", True, WHITE), (8 * SQUARE_SIZE + 10, 10)),
        (font.render("Turn: Black", True, WHITE), (8 * SQUARE_SIZE + 10, 10)),
        (font.render("Exit", True, GRAY), (8 * SQUARE_SIZE + 10, height - 50)),
        (font.render("Undo", True, GRAY), (8 * SQUARE_SIZE + 10, height - 100)),
    )
    check_text = font.render("Check!", True, pygame.Color("red"))

    # Time tracking
    start_time = time.time()
    black_time = white_time = 0
    in_check = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN and turn == player_turn:
                pos = pygame.mouse.get_pos()
                if pos[0] > SQUARE_SIZE * 8:
                    if pos[1] >= height - 80:  # Exit button
                        running = False
                    elif height - 130 <= pos[1] < height - 80:  # Undo button
                        if graphics.confirm_undo_dialog(screen, SQUARE_SIZE):
                            if engine.undoMove(main_board):
                                turn = 'w' if turn == 'b' else 'b'
                                start_time = time.time()
                    continue

                col = pos[0] // SQUARE_SIZE
                row = pos[1] // SQUARE_SIZE
                
                if selected_piece:
                    if engine.tryMove(turn, main_board, selected_piece[0], selected_piece[1], row, col):
                        if turn == 'w':
                            white_time += time.time() - start_time
                        else:
                            black_time += time.time() - start_time
                        
                        turn = 'b' if turn == 'w' else 'w'
                        whatAfter, yForPromotion, xForPromotion = engine.afterMove(turn, main_board, 
                                                                                 selected_piece[0], 
                                                                                 selected_piece[1], row, col)
                        
                        if whatAfter == "promotion":
                            engine.promotion(yForPromotion, xForPromotion, main_board, '10')
                            whatAfter, _, _ = engine.afterMove(turn, main_board, selected_piece[0], 
                                                             selected_piece[1], row, col)
                        
                        if whatAfter in ["checkmate", "stalemate"]:
                            running = False
                        elif whatAfter == "check":
                            in_check = turn
                        else:
                            in_check = None
                        
                        start_time = time.time()
                    selected_piece = None
                else:
                    selected_piece = (row, col)

        # AI move
        if turn != player_turn and running:
            ai_move = ml.get_ai_move(main_board, turn)
            if ai_move:
                from_row, from_col, to_row, to_col = ai_move
                if engine.tryMove(turn, main_board, from_row, from_col, to_row, to_col):
                    if turn == 'w':
                        white_time += time.time() - start_time
                    else:
                        black_time += time.time() - start_time
                    
                    turn = 'w' if turn == 'b' else 'b'
                    whatAfter, yForPromotion, xForPromotion = engine.afterMove(turn, main_board, 
                                                                             from_row, from_col, 
                                                                             to_row, to_col)
                    
                    if whatAfter == "promotion":
                        engine.promotion(yForPromotion, xForPromotion, main_board, '10')
                        whatAfter, _, _ = engine.afterMove(turn, main_board, from_row, from_col, 
                                                         to_row, to_col)
                    
                    if whatAfter in ["checkmate", "stalemate"]:
                        running = False
                    elif whatAfter == "check":
                        in_check = turn
                    else:
                        in_check = None
                    
                    start_time = time.time()

        # Update display
        screen.fill(BLACK)
        graphics.draw_board(screen, SQUARE_SIZE, main_board, in_check)
        
        if selected_piece:
            graphics.highlight_moves(screen, main_board.board_state[selected_piece[0]][selected_piece[1]], 
                                  SQUARE_SIZE, main_board, HIGHLIGHT_MOVES, HIGHLIGHT_TAKES)

        graphics.draw_pieces(screen, main_board, SQUARE_SIZE, pieces)
        current_time = time.time()
        times = ((font.render(graphics.format_time(white_time), True, YELLOW if turn == 'w' else GRAY),
                 (8 * SQUARE_SIZE + 10, height - 150)),
                (font.render(graphics.format_time(black_time), True, YELLOW if turn == 'b' else GRAY),
                 (8 * SQUARE_SIZE + 10, 80)))
        
        graphics.draw_interface(screen, turn, SQUARE_SIZE, BLACK, texts, times, in_check, check_text)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
