import engine.board_and_fields as board_and_fields
import engine.figures as figures

# Ustawienia globalne
player_color = "white"

def rotate_pst(white_pst):
    """
    Obraca planszę (listę list) o 180 stopni,
    co umożliwia wygenerowanie tablicy PST dla czarnych.
    """
    return white_pst[::-1]

# PST dla białych (wartości przeskalowane – oryginalne liczby dzielone przez 100)
PAWN_DOWN = [
    [0.0,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0],
    [0.2,  0.20,  0.20,  0.20,  0.20,  0.20,  0.20, 0.20],
    [0.5, -0.05, -0.10,  0.0,   0.0,  -0.10, -0.05, 0.05],
    [0.10, 0.10,  0.10,  0.20,  0.20,  0.10,  0.10, 0.10],
    [0.1,  0.1,   0.10,  0.25,  0.25,  0.10,  0.1,  0.1],
    [0.10, 0.10,  0.20,  0.30,  0.30,  0.20,  0.10, 0.10],
    [0.2,  0.25,  0.25,  0.15,  0.15,  0.25,  0.25, 0.2],
    [0.0,  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  0.0]
]

KNIGHT = [
    [-0.50, -0.40, -0.30, -0.30, -0.30, -0.30, -0.40, -0.50],
    [-0.40, -0.20,  0.00,  0.05,  0.05,  0.00, -0.20, -0.40],
    [-0.30,  0.05,  0.10,  0.15,  0.15,  0.10,  0.05, -0.30],
    [-0.30,  0.00,  0.15,  0.20,  0.20,  0.15,  0.00, -0.30],
    [-0.30,  0.05,  0.15,  0.20,  0.20,  0.15,  0.05, -0.30],
    [-0.30,  0.00,  0.10,  0.15,  0.15,  0.10,  0.00, -0.30],
    [-0.40, -0.20,  0.00,  0.00,  0.00,  0.00, -0.20, -0.40],
    [-0.50, -0.40, -0.30, -0.30, -0.30, -0.30, -0.40, -0.50]
]

BISHOP = [  # mnożnik razy 3
    [-0.20, -0.10, -0.10, -0.10, -0.10, -0.10, -0.10, -0.20],
    [-0.10,  0.05,  0.00,  0.00,  0.00,  0.00,  0.05, -0.10],
    [-0.10,  0.10,  0.10,  0.10,  0.10,  0.10,  0.10, -0.10],
    [-0.10,  0.00,  0.10,  0.10,  0.10,  0.10,  0.00, -0.10],
    [-0.10,  0.05,  0.05,  0.10,  0.10,  0.05,  0.05, -0.10],
    [-0.10,  0.00,  0.05,  0.10,  0.10,  0.05,  0.00, -0.10],
    [-0.10,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.10],
    [-0.20, -0.10, -0.10, -0.10, -0.10, -0.10, -0.10, -0.20]
]

ROOK = [  # mnożnik razy 4
    [ 0.00,  0.00,  0.05,  0.10,  0.10,  0.05,  0.00,  0.00],
    [-0.05,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.05],
    [-0.05,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.05],
    [-0.05,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.05],
    [-0.05,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.05],
    [-0.05,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.05],
    [ 0.05,  0.10,  0.10,  0.10,  0.10,  0.10,  0.10,  0.05],
    [ 0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00]
]

QUEEN = [  # mnożnik razy 10
    [-0.20, -0.10, -0.10, -0.05, -0.05, -0.10, -0.10, -0.20],
    [-0.10,  0.00,  0.05,  0.00,  0.00,  0.00,  0.00, -0.10],
    [-0.10,  0.05,  0.05,  0.05,  0.05,  0.05,  0.00, -0.10],
    [ 0.00,  0.00,  0.05,  0.05,  0.05,  0.05,  0.00, -0.05],
    [-0.05,  0.00,  0.05,  0.05,  0.05,  0.05,  0.00, -0.05],
    [-0.10,  0.00,  0.05,  0.05,  0.05,  0.05,  0.00, -0.10],
    [-0.10,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00, -0.10],
    [-0.20, -0.10, -0.10, -0.05, -0.05, -0.10, -0.10, -0.20]
]

KING_UP = [  # razy 20
    [ 0.20,  0.30,  0.10,  0.00,  0.00,  0.10,  0.30,  0.20],
    [ 0.20,  0.20,  0.00,  0.00,  0.00,  0.00,  0.20,  0.20],
    [-0.10, -0.20, -0.20, -0.20, -0.20, -0.20, -0.20, -0.10],
    [-0.20, -0.30, -0.30, -0.40, -0.40, -0.30, -0.30, -0.20],
    [-0.30, -0.40, -0.40, -0.50, -0.50, -0.40, -0.40, -0.30],
    [-0.30, -0.40, -0.40, -0.50, -0.50, -0.40, -0.40, -0.30],
    [-0.30, -0.40, -0.40, -0.50, -0.50, -0.40, -0.40, -0.30],
    [-0.30, -0.40, -0.40, -0.50, -0.50, -0.40, -0.40, -0.30]
]

# Generujemy PST dla czarnych przez obrócenie tablic białych:
PAWN_UP = rotate_pst(PAWN_DOWN)
KING_DOWN = rotate_pst(KING_UP)


def ocena_materiału(board):
    """
    Oblicza wartość materiału na planszy.
    Zwraca listę: [waga_białych, waga_czarnych].
    """
    waga_białych = 0
    waga_czarnych = 0
    figures_values = {
        'p': 1,
        'N': 3,
        'B': 3,
        'R': 5,
        'Q': 9,
        'K': 0
    }
    for i in range(8):
        for j in range(8):
            field = board.board_state[i][j]
            if field.figure is None:
                continue
            figure = field.figure.return_figure()
            if len(figure) < 2:
                continue
            piece_type = figure[1]
            piece_color = figure[0]
            if piece_color == 'w':
                waga_białych += figures_values.get(piece_type, 0)
            else:
                waga_czarnych += figures_values.get(piece_type, 0)
    return [waga_białych, waga_czarnych]


def bonus_squares(board):
    """
    Oblicza bonus pozycyjny według tablic PST.
    Zwraca listę: [bonus_białych, bonus_czarnych].
    """
    bonus_białych = 0
    bonus_czarnych = 0
    for i in range(8):
        for j in range(8):
            field = board.board_state[i][j]
            if field.figure is None:
                continue
            color = field.figure.color
            piece_type = field.figure.type
            if player_color == "white":
                if color == 'w':
                    if piece_type == 'p':
                        bonus_białych += PAWN_DOWN[i][j]
                    elif piece_type == 'N':
                        bonus_białych += KNIGHT[i][j]
                    elif piece_type == 'B':
                        bonus_białych += BISHOP[i][j] * 3
                    elif piece_type == 'R':
                        bonus_białych += ROOK[i][j] * 4
                    elif piece_type == 'Q':
                        bonus_białych += QUEEN[i][j] * 10
                    elif piece_type == 'K':
                        bonus_białych += KING_DOWN[i][j] * 20
                else:
                    if piece_type == 'p':
                        bonus_czarnych += PAWN_UP[i][j]
                    elif piece_type == 'N':
                        bonus_czarnych += KNIGHT[i][j]
                    elif piece_type == 'B':
                        bonus_czarnych += BISHOP[i][j] * 3
                    elif piece_type == 'R':
                        bonus_czarnych += ROOK[i][j] * 4
                    elif piece_type == 'Q':
                        bonus_czarnych += QUEEN[i][j] * 10
                    elif piece_type == 'K':
                        bonus_czarnych += KING_UP[i][j] * 20
            else:
                if color == 'b':
                    if piece_type == 'p':
                        bonus_białych += PAWN_DOWN[i][j]
                    elif piece_type == 'N':
                        bonus_białych += KNIGHT[i][j]
                    elif piece_type == 'B':
                        bonus_białych += BISHOP[i][j] * 3
                    elif piece_type == 'R':
                        bonus_białych += ROOK[i][j] * 4
                    elif piece_type == 'Q':
                        bonus_białych += QUEEN[i][j] * 10
                    elif piece_type == 'K':
                        bonus_białych += KING_DOWN[i][j] * 20
                else:
                    if piece_type == 'p':
                        bonus_czarnych += PAWN_UP[i][j]
                    elif piece_type == 'N':
                        bonus_czarnych += KNIGHT[i][j]
                    elif piece_type == 'B':
                        bonus_czarnych += BISHOP[i][j] * 3
                    elif piece_type == 'R':
                        bonus_czarnych += ROOK[i][j] * 4
                    elif piece_type == 'Q':
                        bonus_czarnych += QUEEN[i][j] * 10
                    elif piece_type == 'K':
                        bonus_czarnych += KING_UP[i][j] * 20
    return [bonus_białych, bonus_czarnych]


def count_pieces(board):
    """
    Zlicza wszystkie figury na planszy.
    Zwraca sumaryczną liczbę figur.
    """
    count = 0
    for i in range(8):
        for j in range(8):
            if board.board_state[i][j].figure is not None:
                count += 1
    return count


def king_to_edge(board):
    """
    Oblicza sumaryczną odległość królów od krawędzi planszy.
    Dla białych zwraca dystans króla czarnego od krawędzi,
    a dla czarnych dystans króla białego.
    Zwraca listę: [ocena_białych, ocena_czarnych].
    """
    evaluation_white = 0
    evaluation_black = 0
    white_king_position = None
    black_king_position = None

    for i in range(8):
        for j in range(8):
            field = board.board_state[i][j]
            if field.figure is not None and field.figure.type == 'K':
                if field.figure.color == 'w':
                    white_king_position = (i, j)
                else:
                    black_king_position = (i, j)
                    
    if white_king_position is not None:
        rank, file = white_king_position
        # Obliczamy dystans króla białego do najbliższej krawędzi
        white_dst = min(rank, 7 - rank) + min(file, 7 - file)
        evaluation_black += white_dst
    if black_king_position is not None:
        rank, file = black_king_position
        # Obliczamy dystans króla czarnego do najbliższej krawędzi
        black_dst = min(rank, 7 - rank) + min(file, 7 - file)
        evaluation_white += black_dst

    return [evaluation_white, evaluation_black]

#color to color który ma ruch 
def get_evaluation(board, color = 'b'):
    """
    Łączy ocenę materiałową, bonus pozycyjny i premię za pozycję królów.
    Wprowadza dodatkowy modyfikator zależny od liczby figur na planszy.
    Zwraca listę: [ocena_białych, ocena_czarnych].
    """
    material = ocena_materiału(board)
    bonus = bonus_squares(board)
    king_bonus = king_to_edge(board)
    pieces_count = count_pieces(board)
    
    # Modyfikator zależny od liczby figur – im mniej figur, tym większy wpływ oceny pozycji króla
    modifier = 1 + (32 - pieces_count) / 100
    modifier *= 2
    #jezeli wszytkie listy dla danego koloru and szach to plus infinity jezeli pat to 

    if board_and_fields.Board.get_all_moves(board, color) == {} and board.is_check(color):
        if color == 'w':
            return [-1000000, 1000000]
        else:
            return [1000000, -1000000]
    elif board_and_fields.Board.get_all_moves(board, color) == {} and board.is_check(color) == False:
        if color == 'w' and  (material[0] + bonus[0] + (king_bonus[0] * modifier)) > (material[1] + bonus[1] + (king_bonus[1] * modifier)):
           return [-1000000, 1000000]
        else:
            return [1000000, -1000000]


    # .is_check (bierze kolor) 
    eval_white = material[0] + bonus[0] + (king_bonus[0] * modifier)
    eval_black = material[1] + bonus[1] + (king_bonus[1] * modifier)
    return [eval_white, eval_black]


# Przykładowe użycie (dla testów):
if __name__ == "__main__":
    board = board_and_fields.Board()  # plansza startowa
    evaluation_result = get_evaluation(board)
    print("Ocena białych:", evaluation_result[0])
    print("Ocena czarnych:", evaluation_result[1])

