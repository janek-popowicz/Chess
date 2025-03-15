import random
import engine
import board_and_fields as bf

class RandomAI:
    def __init__(self, board, board_size=8, bad_sources=None, bad_destinations=None):
        """
        Inicjalizuje instancję RandomAI.
        """
        if bad_sources is None:
            bad_sources = [(1, 2)]
        if bad_destinations is None:
            bad_destinations = []
        self.board = board
        self.board_size = board_size
        self.bad_sources = bad_sources
        self.bad_destinations = bad_destinations

    def get_random_move(self):
        """
        Losuje legalny ruch dla AI.
        Zamiast losować całkowicie losowe pozycje, najpierw znajduje wszystkie czarne bierki,
        a następnie dla każdej z nich sprawdza dostępne ruchy.
        
        Returns:
            Krotka (src_x, src_y, dst_x, dst_y) reprezentująca legalny ruch.
        """
        # Znajdź wszystkie czarne bierki na planszy
        black_pieces = []
        for y in range(self.board_size):
            for x in range(self.board_size):
                # Używamy board_state oraz sprawdzamy atrybut figure
                field = self.board.board_state[y][x]
                if field.figure is not None and field.figure.color == 'b':
                    if (x, y) not in self.bad_sources:
                        black_pieces.append((x, y))
        
        random.shuffle(black_pieces)
        
        # Sprawdź każdą bierkę, aż znajdziesz legalny ruch
        for src_x, src_y in black_pieces:
            possible_destinations = []
            for dst_y in range(self.board_size):
                for dst_x in range(self.board_size):
                    if (dst_x, dst_y) not in self.bad_destinations:
                        if engine.tryMove('b', self.board, src_y, src_x, dst_y, dst_x):
                            possible_destinations.append((dst_x, dst_y))
            
            if possible_destinations:
                dst_x, dst_y = random.choice(possible_destinations)
                return (src_x, src_y, dst_x, dst_y)
        
        # Jeśli nie znaleziono legalnego ruchu (pat lub mat)
        return None

# Funkcja pomocnicza dla kompatybilności z istniejącym kodem
def get_random_move():
    """
    Funkcja kompatybilności z istniejącym kodem.
    W rzeczywistości powinna zostać zastąpiona właściwym wywołaniem metody
    get_random_move() z instancji klasy RandomAI.
    
    Returns:
        Przykładowy ruch (src_x, src_y, dst_x, dst_y).
    """
    ruch = RandomAI(None).get_random_move()
    if ruch is not None:
        src_x, src_y, dst_x, dst_y = ruch
    return(src_x, src_y, dst_x, dst_y)
    

