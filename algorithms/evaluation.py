import engine.board_and_fields as board_and_fields
import engine.figures as figures
import copy

# Ustawienia globalne
domyśly_color = "white"

def get_color(color):
    return color 

player_color = get_color(domyśly_color)

def rotate_pst(white_pst):
    """
    Obraca planszę (listę list) o 180 stopni,
    co umożliwia wygenerowanie tablicy PST dla czarnych.
    """
    return white_pst[::-1]

# PST dla białych (wartości przeskalowane – oryginalne liczby dzielone przez 100)
KING_DOWN = [
    [-15.0, -20.0, -20.0, -25.0, -25.0, -20.0, -20.0, -15.0],
    [-15.0, -20.0, -20.0, -25.0, -25.0, -20.0, -20.0, -15.0],
    [-15.0, -20.0, -20.0, -25.0, -25.0, -20.0, -20.0, -15.0],
    [-15.0, -20.0, -20.0, -25.0, -25.0, -20.0, -20.0, -15.0],
    [-10.0, -15.0, -15.0, -20.0, -20.0, -15.0, -15.0, -10.0],
    [ -5.0, -10.0, -10.0, -15.0, -15.0, -10.0, -10.0,  -5.0],
    [ 10.0,  10.0,   0.0,   0.0,   0.0,   0.0,  10.0,  10.0],
    [ 10.0,  15.0,   5.0,   0.0,   0.0,   5.0,  15.0,  10.0]
]

QUEEN = [
    [-10.0,  -5.0,  -5.0,  -2.5,  -2.5,  -5.0,  -5.0, -10.0],
    [ -5.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  -5.0],
    [ -5.0,   0.0,   2.5,   2.5,   2.5,   2.5,   0.0,  -5.0],
    [ -2.5,   0.0,   2.5,   2.5,   2.5,   2.5,   0.0,  -2.5],
    [  0.0,   0.0,   2.5,   2.5,   2.5,   2.5,   0.0,  -2.5],
    [ -5.0,   2.5,   2.5,   2.5,   2.5,   2.5,   0.0,  -5.0],
    [ -5.0,   0.0,   2.5,   0.0,   0.0,   0.0,   0.0,  -5.0],
    [-10.0,  -5.0,  -5.0,  -2.5,  -2.5,  -5.0,  -5.0, -10.0]
]

ROOK = [
    [  0.0,   0.0,   0.0,   5.0,   5.0,   0.0,   0.0,   0.0],
    [  0.0,   0.0,   0.0,  10.0,  10.0,   0.0,   0.0,   0.0],
    [  0.0,   0.0,   0.0,  10.0,  10.0,   0.0,   0.0,   0.0],
    [  5.0,  10.0,  10.0,  20.0,  20.0,  10.0,  10.0,   5.0],
    [  5.0,  10.0,  10.0,  20.0,  20.0,  10.0,  10.0,   5.0],
    [  0.0,   0.0,   0.0,  10.0,  10.0,   0.0,   0.0,   0.0],
    [  0.0,   0.0,   0.0,  10.0,  10.0,   0.0,   0.0,   0.0],
    [  0.0,   0.0,   0.0,   5.0,   5.0,   0.0,   0.0,   0.0]
]


BISHOP = [
    [-10.0,  -5.0,  -5.0,  -5.0,  -5.0,  -5.0,  -5.0, -10.0],
    [ -5.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,  -5.0],
    [ -5.0,   0.0,   2.5,   5.0,   5.0,   2.5,   0.0,  -5.0],
    [ -5.0,   2.5,   2.5,   5.0,   5.0,   2.5,   2.5,  -5.0],
    [ -5.0,   0.0,   5.0,   5.0,   5.0,   5.0,   0.0,  -5.0],
    [ -5.0,   5.0,   5.0,   5.0,   5.0,   5.0,   5.0,  -5.0],
    [ -5.0,   2.5,   0.0,   0.0,   0.0,   0.0,   2.5,  -5.0],
    [-10.0,  -5.0,  -5.0,  -5.0,  -5.0,  -5.0,  -5.0, -10.0]
]

KNIGHT = [
    [-25.0, -20.0, -15.0, -15.0, -15.0, -15.0, -20.0, -25.0],
    [-20.0, -10.0,   0.0,   0.0,   0.0,   0.0, -10.0, -20.0],
    [-15.0,   0.0,   5.0,   7.5,   7.5,   5.0,   0.0, -15.0],
    [-15.0,   2.5,   7.5,  10.0,  10.0,   7.5,   2.5, -15.0],
    [-15.0,   0.0,   7.5,  10.0,  10.0,   7.5,   0.0, -15.0],
    [-15.0,   2.5,   5.0,   7.5,   7.5,   5.0,   2.5, -15.0],
    [-20.0, -10.0,   0.0,   2.5,   2.5,   0.0, -10.0, -20.0],
    [-25.0, -20.0, -15.0, -15.0, -15.0, -15.0, -20.0, -25.0]
]

PAWN_DOWN = [
    [  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0],
    [ 25.0,  25.0,  25.0,  25.0,  25.0,  25.0,  25.0,  25.0],
    [  5.0,   5.0,  10.0,  15.0,  15.0,  10.0,   5.0,   5.0],
    [  2.5,   2.5,   5.0,  12.5,  12.5,   5.0,   2.5,   2.5],
    [  2.5,   5,   10.0,  15.0,  15.0,   10.0,   5,   2.5],
    [  2.5,  -2.5,  -5.0,   0.0,   0.0,  -5.0,  -2.5,   2.5],
    [  2.5,   5.0,   5.0, -10.0, -10.0,   5.0,   5.0,   2.5],
    [  0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0]
]

# Generujemy PST dla czarnych przez obrócenie tablic białych:
PAWN_UP = rotate_pst(PAWN_DOWN)
KING_UP = rotate_pst(KING_DOWN)

# Stałe do oceny fazy gry
OPENING_MATERIAL_SUM = 7600  # Przybliżona suma wartości wszystkich figur na początku gry
ENDGAME_MATERIAL_SUM = 1200  # Przybliżona suma wartości figur w końcówce

# Wartości figur
PIECE_VALUES = {
    'p': 100,
    'N': 320,
    'B': 330,
    'R': 500,
    'Q': 900,
    'K': 20000
}

def ocena_materiału(board):
    """
    Oblicza wartość materiału na planszy.
    Zwraca listę: [waga_białych, waga_czarnych].
    """
    waga_białych = 0
    waga_czarnych = 0
    
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
                waga_białych += PIECE_VALUES.get(piece_type, 0)
            else:
                waga_czarnych += PIECE_VALUES.get(piece_type, 0)
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
            if color == 'w':
                if piece_type == 'p':
                    bonus_białych += PAWN_DOWN[i][j] 
                elif piece_type == 'N':
                    bonus_białych += KNIGHT[i][j] 
                elif piece_type == 'B':
                    bonus_białych += BISHOP[i][j] 
                elif piece_type == 'R':
                    bonus_białych += ROOK[i][j] 
                elif piece_type == 'Q':
                    bonus_białych += QUEEN[i][j] 
                elif piece_type == 'K':
                    bonus_białych += KING_DOWN[i][j] 
            else:
                if piece_type == 'p':
                    bonus_czarnych += PAWN_UP[i][j] 
                elif piece_type == 'N':
                    bonus_czarnych += KNIGHT[i][j] 
                elif piece_type == 'B':
                    bonus_czarnych += BISHOP[i][j]
                elif piece_type == 'R':
                    bonus_czarnych += ROOK[i][j]
                elif piece_type == 'Q':
                    bonus_czarnych += QUEEN[i][j]
                elif piece_type == 'K':
                    bonus_czarnych += KING_UP[i][j]
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


def rook_on_open_file(board):
    """
    Przyznaje bonus za wieże na otwartych i półotwartych liniach.
    Zwraca listę: [bonus_białych, bonus_czarnych].
    """
    bonus_białych = 0
    bonus_czarnych = 0
    
    # Znajdź wszystkie pionki i ich kolumny
    white_pawn_files = [False] * 8
    black_pawn_files = [False] * 8
    
    for i in range(8):
        for j in range(8):
            field = board.board_state[i][j]
            if field.figure is not None and field.figure.type == 'p':
                if field.figure.color == 'w':
                    white_pawn_files[j] = True
                else:
                    black_pawn_files[j] = True
    
    # Sprawdź wieże
    for i in range(8):
        for j in range(8):
            field = board.board_state[i][j]
            if field.figure is not None and field.figure.type == 'R':
                # Otwarta linia: brak pionków obu kolorów
                if not white_pawn_files[j] and not black_pawn_files[j]:
                    if field.figure.color == 'w':
                        bonus_białych += 20.0  # Większy bonus za całkowicie otwartą linię
                    else:
                        bonus_czarnych += 20.0
                # Półotwarta linia: brak własnych pionków, ale są pionki przeciwnika
                elif field.figure.color == 'w' and not white_pawn_files[j]:
                    bonus_białych += 10.0
                elif field.figure.color == 'b' and not black_pawn_files[j]:
                    bonus_czarnych += 10.0
    
    return [bonus_białych, bonus_czarnych]


def bishop_pair_bonus(board):
    """
    Przyznaje bonus za posiadanie pary gońców.
    Zwraca listę: [bonus_białych, bonus_czarnych].
    """
    white_bishops = 0
    black_bishops = 0
    
    for i in range(8):
        for j in range(8):
            field = board.board_state[i][j]
            if field.figure is not None and field.figure.type == 'B':
                if field.figure.color == 'w':
                    white_bishops += 1
                else:
                    black_bishops += 1
    
    bonus_białych = 50.0 if white_bishops >= 2 else 0.0
    bonus_czarnych = 50.0 if black_bishops >= 2 else 0.0
    
    return [bonus_białych, bonus_czarnych]


def development_bonus(board, move_number=None):
    """
    Przyznaje bonus za rozwój figur w otwarciu i wczesnym midgame.
    Zwraca listę: [bonus_białych, bonus_czarnych].
    """
    bonus_białych = 0
    bonus_czarnych = 0
    
    # Jeśli nie znamy numeru ruchu, szacujemy fazę gry na podstawie materiału
    if move_number is None:
        material = ocena_materiału(board)
        total_material = material[0] + material[1]
        # Jeśli mamy ponad 80% początkowego materiału, to jest to otwarcie lub wczesne midgame
        if total_material > 0.8 * (OPENING_MATERIAL_SUM):
            # Sprawdź rozwój figur
            white_developed_minors = 0
            black_developed_minors = 0
            white_castled = False
            black_castled = False
            
            # Sprawdź rozwój skoczków i gońców (czy wyszły z pozycji początkowych)
            for j in range(8):
                # Sprawdź czy skoczki wyszły z pozycji początkowych
                if board.board_state[7][1].figure is None or board.board_state[7][1].figure.type != 'N':
                    white_developed_minors += 1
                if board.board_state[7][6].figure is None or board.board_state[7][6].figure.type != 'N':
                    white_developed_minors += 1
                if board.board_state[0][1].figure is None or board.board_state[0][1].figure.type != 'N':
                    black_developed_minors += 1
                if board.board_state[0][6].figure is None or board.board_state[0][6].figure.type != 'N':
                    black_developed_minors += 1
                
                # Sprawdź czy gońce wyszły z pozycji początkowych
                if board.board_state[7][2].figure is None or board.board_state[7][2].figure.type != 'B':
                    white_developed_minors += 1
                if board.board_state[7][5].figure is None or board.board_state[7][5].figure.type != 'B':
                    white_developed_minors += 1
                if board.board_state[0][2].figure is None or board.board_state[0][2].figure.type != 'B':
                    black_developed_minors += 1
                if board.board_state[0][5].figure is None or board.board_state[0][5].figure.type != 'B':
                    black_developed_minors += 1
            
            # Sprawdź czy król wykonał roszadę (uproszczone)
            # Krótkiej roszady
            if (board.board_state[7][6].figure is not None and 
                board.board_state[7][6].figure.type == 'K' and 
                board.board_state[7][6].figure.color == 'w'):
                white_castled = True
            # Długiej roszady
            elif (board.board_state[7][2].figure is not None and 
                  board.board_state[7][2].figure.type == 'K' and 
                  board.board_state[7][2].figure.color == 'w'):
                white_castled = True
            
            # Analogicznie dla czarnych
            if (board.board_state[0][6].figure is not None and 
                board.board_state[0][6].figure.type == 'K' and 
                board.board_state[0][6].figure.color == 'b'):
                black_castled = True
            elif (board.board_state[0][2].figure is not None and 
                  board.board_state[0][2].figure.type == 'K' and 
                  board.board_state[0][2].figure.color == 'b'):
                black_castled = True
            
            # Dodaj bonusy za rozwój figur lekkich
            bonus_białych += white_developed_minors * 5.0
            bonus_czarnych += black_developed_minors * 5.0
            
            # Dodaj bonus za roszadę
            if white_castled:
                bonus_białych += 15.0
            if black_castled:
                bonus_czarnych += 15.0
    
    return [bonus_białych, bonus_czarnych]


def knight_bishop_situational(board):
    """
    Dostosowuje wartość skoczków i gońców w zależności od struktury pionków.
    Zwraca listę: [bonus_białych, bonus_czarnych].
    """
    bonus_białych = 0
    bonus_czarnych = 0
    
    # Liczba pionków dla obu stron
    white_pawns = 0
    black_pawns = 0
    # Liczba skoczków i gońców dla obu stron
    white_knights = 0
    white_bishops = 0
    black_knights = 0
    black_bishops = 0
    
    # Policz figury
    for i in range(8):
        for j in range(8):
            field = board.board_state[i][j]
            if field.figure is None:
                continue
            
            if field.figure.type == 'p':
                if field.figure.color == 'w':
                    white_pawns += 1
                else:
                    black_pawns += 1
            elif field.figure.type == 'N':
                if field.figure.color == 'w':
                    white_knights += 1
                else:
                    black_knights += 1
            elif field.figure.type == 'B':
                if field.figure.color == 'w':
                    white_bishops += 1
                else:
                    black_bishops += 1
    
    # Określ, czy pozycja jest zamknięta czy otwarta na podstawie liczby pionków
    total_pawns = white_pawns + black_pawns
    is_closed_position = total_pawns >= 12  # Jeśli jest dużo pionków, pozycja jest zamknięta
    
    # Przyznaj bonusy w zależności od typu pozycji
    if is_closed_position:
        # W zamkniętej pozycji skoczki są lepsze
        bonus_białych += white_knights * 10.0 - white_bishops * 5.0
        bonus_czarnych += black_knights * 10.0 - black_bishops * 5.0
    else:
        # W otwartej pozycji gońce są lepsze
        bonus_białych += white_bishops * 10.0 - white_knights * 5.0
        bonus_czarnych += black_bishops * 10.0 - black_knights * 5.0
    
    return [bonus_białych, bonus_czarnych]


def piece_activity(board):
    """
    Ocenia aktywność figur na podstawie ich mobilności i wpływu na planszę.
    Zwraca listę: [bonus_białych, bonus_czarnych].
    """
    bonus_białych = 0
    bonus_czarnych = 0
    
    # Iterujemy po wszystkich polach
    for i in range(8):
        for j in range(8):
            field = board.board_state[i][j]
            if field.figure is None:
                continue
            
            # Pobierz listę dostępnych ruchów dla figury
            # To jest uproszczone, w rzeczywistości potrzebujemy funkcji z silnika szachowego
            # która zwraca wszystkie dostępne ruchy figury
            moves_count = count_available_moves(board, i, j)
            
            # Dodaj bonus za mobilność
            mobility_bonus = moves_count * 2.0  # Za każdy możliwy ruch dodajemy 2 punkty
            
            if field.figure.color == 'w':
                bonus_białych += mobility_bonus
            else:
                bonus_czarnych += mobility_bonus
    
    return [bonus_białych, bonus_czarnych]


def count_available_moves(board, rank, file):
    """
    Pomocnicza funkcja do policzenia dostępnych ruchów figury.
    W rzeczywistym silniku szachowym należałoby użyć istniejącej funkcji.
    """
    # To jest znacznie uproszczone - w praktyce musielibyśmy używać funkcji
    # z silnika szachowego, które generują legalne ruchy
    field = board.board_state[rank][file]
    if field.figure is None:
        return 0
    
    # Uproszczone szacowanie mobilności na podstawie typu figury i pozycji
    piece_type = field.figure.type
    
    # Skoczek ma zazwyczaj od 2 do 8 ruchów
    if piece_type == 'N':
        # Na brzegu szachownicy skoczek ma mniej ruchów
        if rank in [0, 7] or file in [0, 7]:
            return 4
        else:
            return 6
    
    # Goniec ma zazwyczaj od 7 do 13 ruchów
    elif piece_type == 'B':
        # Sprawdź, czy goniec jest blokowany przez własne pionki
        blocked = 0
        for i in range(8):
            for j in range(8):
                if abs(i - rank) == abs(j - file) and board.board_state[i][j].figure is not None:
                    if board.board_state[i][j].figure.color == field.figure.color:
                        blocked += 1
        return 10 - min(blocked, 5)  # Mniej ruchów, jeśli zablokowany
    
    # Wieża ma zazwyczaj od 10 do 14 ruchów
    elif piece_type == 'R':
        # Wieża na otwartej linii ma więcej ruchów
        has_own_pawns_in_file = False
        for i in range(8):
            if (board.board_state[i][file].figure is not None and 
                board.board_state[i][file].figure.type == 'p' and
                board.board_state[i][file].figure.color == field.figure.color):
                has_own_pawns_in_file = True
                break
        
        return 12 if not has_own_pawns_in_file else 10
    
    # Hetman ma zazwyczaj od 20 do 27 ruchów
    elif piece_type == 'Q':
        return 22  # Średnia wartość
    
    # Król ma zazwyczaj od 3 do 8 ruchów
    elif piece_type == 'K':
        return 5  # Średnia wartość
    
    # Pionek ma zazwyczaj 1-2 ruchy
    elif piece_type == 'p':
        return 1  # Uproszczone
    
    return 0


def checks_and_threats(board):
    """
    Ocenia pozycję na podstawie szachów i gróźb.
    Zwraca listę: [bonus_białych, bonus_czarnych].
    """
    bonus_białych = 0
    bonus_czarnych = 0
    
    # Sprawdź czy król jest szachowany
    # W rzeczywistym silniku szachowym należałoby wykorzystać istniejącą funkcję
    # board.is_in_check(color)
    
    # Uproszczone sprawdzenie kontrolowanych pól wokół króla przeciwnika
    white_king_pos = None
    black_king_pos = None
    
    # Znajdź pozycje królów
    for i in range(8):
        for j in range(8):
            field = board.board_state[i][j]
            if field.figure is not None and field.figure.type == 'K':
                if field.figure.color == 'w':
                    white_king_pos = (i, j)
                else:
                    black_king_pos = (i, j)
    
    # Sprawdź pola wokół króla przeciwnika
    if white_king_pos:
        i, j = white_king_pos
        threatened_squares = 0
        
        # Sprawdź 8 pól wokół króla
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue  # Pomijamy pozycję króla
                
                ni, nj = i + di, j + dj
                if 0 <= ni < 8 and 0 <= nj < 8:  # Sprawdź czy pole jest na szachownicy
                    # W rzeczywistym silniku szachowym sprawdzilibyśmy, czy pole jest atakowane
                    # przez czarne figury
                    threatened_squares += 1
        
        bonus_czarnych += threatened_squares * 5.0  # 5 punktów za każde atakowane pole
    
    if black_king_pos:
        i, j = black_king_pos
        threatened_squares = 0
        
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                
                ni, nj = i + di, j + dj
                if 0 <= ni < 8 and 0 <= nj < 8:
                    threatened_squares += 1
        
        bonus_białych += threatened_squares * 5.0
    
    return [bonus_białych, bonus_czarnych]


def connected_rooks(board):
    """
    Przyznaje bonus za połączone wieże (wieże, które się nawzajem bronią).
    Zwraca listę: [bonus_białych, bonus_czarnych].
    """
    bonus_białych = 0
    bonus_czarnych = 0
    
    # Znajdź pozycje wież
    white_rooks = []
    black_rooks = []
    
    for i in range(8):
        for j in range(8):
            field = board.board_state[i][j]
            if field.figure is not None and field.figure.type == 'R':
                if field.figure.color == 'w':
                    white_rooks.append((i, j))
                else:
                    black_rooks.append((i, j))
    
    # Sprawdź, czy wieże są połączone (na tej samej linii lub kolumnie)
    if len(white_rooks) >= 2:
        for idx1, (r1, c1) in enumerate(white_rooks):
            for idx2, (r2, c2) in enumerate(white_rooks[idx1+1:], idx1+1):
                # Sprawdź, czy wieże są w tej samej linii lub kolumnie
                if r1 == r2 or c1 == c2:
                    # Sprawdź, czy nie ma figur między wieżami
                    is_connected = True
                    if r1 == r2:  # Wieże w tej samej linii
                        start, end = min(c1, c2), max(c1, c2)
                        for c in range(start + 1, end):
                            if board.board_state[r1][c].figure is not None:
                                is_connected = False
                                break
                    else:  # Wieże w tej samej kolumnie
                        start, end = min(r1, r2), max(r1, r2)
                        for r in range(start + 1, end):
                            if board.board_state[r][c1].figure is not None:
                                is_connected = False
                                break
                    
                    if is_connected:
                        bonus_białych += 15.0  # Bonus za połączone wieże
                        break  # Wystarczy znaleźć jedną połączoną parę
    
    # Analogicznie dla czarnych wież
    if len(black_rooks) >= 2:
        for idx1, (r1, c1) in enumerate(black_rooks):
            for idx2, (r2, c2) in enumerate(black_rooks[idx1+1:], idx1+1):
                if r1 == r2 or c1 == c2:
                    is_connected = True
                    if r1 == r2:
                        start, end = min(c1, c2), max(c1, c2)
                        for c in range(start + 1, end):
                            if board.board_state[r1][c].figure is not None:
                                is_connected = False
                                break
                    else:
                        start, end = min(r1, r2), max(r1, r2)
                        for r in range(start + 1, end):
                            if board.board_state[r][c1].figure is not None:
                                is_connected = False
                                break
                    
                    if is_connected:
                        bonus_czarnych += 15.0
                        break
    
    return [bonus_białych, bonus_czarnych]

def get_evaluation(board, current_color=None):
    """
    Zwraca ocenę pozycji w formie listy [wartość_białych, wartość_czarnych]
    oraz wykrywa sytuacje matowe i patowe.

    Args:
        board: Plansza do oceny
        current_color: Kolor gracza wykonującego ruch ('w' lub 'b')
    """
    if current_color:
        # Sprawdź warunki końca gry
        legal_moves = board.get_all_moves(current_color)
        
        if not legal_moves:
            if board.is_in_check(current_color):
                # Mat - zwróć ogromną wartość z perspektywy przeciwnika
                return [float('-inf'), float('inf')] if current_color == 'w' else [float('inf'), float('-inf')]
            else:
                # Pat
                return [0.0, 0.0]

    # Oblicz wartość materiału
    material = ocena_materiału(board)
    
    # Oblicz bonus pozycyjny
    position_bonus = bonus_squares(board)
    
    # Oblicz dodatkowe składniki oceny
    king_edge = king_to_edge(board)
    rook_open = rook_on_open_file(board)
    bishop_bonus = bishop_pair_bonus(board)
    development = development_bonus(board)
    situational = knight_bishop_situational(board)
    activity = piece_activity(board)
    threats = checks_and_threats(board)
    rooks_connected = connected_rooks(board)
    
    # Suma wszystkich składników oceny dla białych
    white_eval = (material[0] + 
                 position_bonus[0] + 
                 king_edge[0] + 
                 rook_open[0] + 
                 bishop_bonus[0] + 
                 development[0] + 
                 situational[0] + 
                 activity[0] + 
                 threats[0] + 
                 rooks_connected[0])
    
    # Suma wszystkich składników oceny dla czarnych
    black_eval = (material[1] + 
                 position_bonus[1] + 
                 king_edge[1] + 
                 rook_open[1] + 
                 bishop_bonus[1] + 
                 development[1] + 
                 situational[1] + 
                 activity[1] + 
                 threats[1] + 
                 rooks_connected[1])
    
    return [white_eval, black_eval]