import engine
import board_and_fields as bf
import random_ai

class TestModeAI:
    def __init__(self):
        """
        Inicjalizuje tryb testowy z AI.
        """
        self.board = None
        self.ai = None
        self.turn = 'w'  # Gracz (białe) zaczyna
        self.running = False

    def initialize_game(self):
        """
        Inicjalizuje nową grę z pustą planszą.
        """
        self.board = bf.Board()
        self.ai = random_ai.RandomAI(self.board)
        self.turn = 'w'
        self.running = True
        return self.board

    def player_move(self, y1, x1, y2, x2):
        """
        Wykonuje ruch gracza (białe).
        """
        if not engine.tryMove(self.turn, self.board, y1, x1, y2, x2):
            return False, "", 0, 0
            
        whatAfter, yForPromotion, xForPromotion = engine.afterMove(self.turn, self.board, y1, x1, y2, x2)
        return True, whatAfter, yForPromotion, xForPromotion
    
    def handle_promotion(self, y, x, choice="4"):
        """
        Obsługuje promocję pionka.
        """
        engine.promotion(self.turn, y, x, self.board, choice)
        return True
        
    def ai_move(self):
        """
        Wykonuje ruch AI (czarne).
        """
        ai_move = self.ai.get_random_move()
        
        if ai_move is None:
            return False, None, "stalemate", 0, 0
            
        src_x, src_y, dst_x, dst_y = ai_move
        
        if not engine.tryMove(self.turn, self.board, src_y, src_x, dst_y, dst_x):
            return False, ai_move, "", 0, 0
        
        whatAfter, yForPromotion, xForPromotion = engine.afterMove(self.turn, self.board, src_y, src_x, dst_y, dst_x)
        
        if whatAfter == "promotion":
            self.handle_promotion(yForPromotion, xForPromotion, "4")  # AI zawsze promuje na królową
            
        return True, ai_move, whatAfter, yForPromotion, xForPromotion
    
    def change_turn(self):
        """
        Zmienia turę z białych na czarne lub odwrotnie.
        """
        self.turn = 'w' if self.turn == 'b' else 'b'
    
    def is_game_over(self, status):
        """
        Sprawdza, czy gra się zakończyła.
        """
        if status in ["checkmate", "stalemate"]:
            message = "Szach Mat!" if status == "checkmate" else "Pat"
            return True, message
        return False, ""
    
    def process_player_input(self):
        """
        Pobiera i przetwarza dane wejściowe od gracza.
        """
        try:
            y1 = int(input("Wprowadź rząd figury, którą chcesz przesunąć: "))
            x1 = int(input("Wprowadź kolumnę figury, którą chcesz przesunąć: "))
            y2 = int(input("Wprowadź rząd, na który chcesz przesunąć figurę: "))
            x2 = int(input("Wprowadź kolumnę, na którą chcesz przesunąć figurę: "))
            return True, y1, x1, y2, x2
        except ValueError:
            print("Podaj poprawne liczby!")
            return False, 0, 0, 0, 0
    
    def handle_player_turn(self):
        """
        Obsługuje turę gracza (białe).
        """
        moving = True
        while moving:
            valid_input, y1, x1, y2, x2 = self.process_player_input()
            if not valid_input:
                continue

            success, whatAfter, yForPromotion, xForPromotion = self.player_move(y1, x1, y2, x2)
            moving = not success
        
        if whatAfter == "promotion":
            self.board.print_board()
            choiceOfPromotion = input(f"Pionek w kolumnie {xForPromotion} dotarł do końca planszy. Wpisz:\n"
                                     "1 - Aby zmienić go w Skoczka\n"
                                     "2 - Aby zmienić go w Gońca\n"
                                     "3 - Aby zmienić go w Wieżę\n"
                                     "4 - Aby zmienić go w Królową\n")
            self.handle_promotion(yForPromotion, xForPromotion, choiceOfPromotion)
        
        return whatAfter
    
    def handle_ai_turn(self):
        """
        Obsługuje turę AI (czarne).
        """
        success, move, whatAfter, yForPromotion, xForPromotion = self.ai_move()
        
        if not success:
            if move is None:
                print("AI nie może wykonać ruchu. Koniec gry.")
            else:
                print("Błąd przy wykonywaniu ruchu AI.")
            self.running = False
            return whatAfter
        
        src_x, src_y, dst_x, dst_y = move
        print(f"AI wykonuje ruch: [{src_x}][{src_y}] -> [{dst_x}][{dst_y}]")
        
        return whatAfter
    
    def display_game_status(self):
        """
        Wyświetla aktualny stan gry.
        """
        self.board.print_board()
        self.board.is_in_check(self.turn)
        if self.board.incheck:
            print("Szach!")
    
    def run_game(self):
        """
        Główna pętla gry w trybie testowym z AI.
        """
        self.initialize_game()
        
        while self.running:
            self.display_game_status()
            
            if self.turn == 'w':
                # Ruch gracza (białe)
                whatAfter = self.handle_player_turn()
            else:
                # Ruch AI (czarne)
                whatAfter = self.handle_ai_turn()
                
            if not self.running:
                break
                
            game_over, message = self.is_game_over(whatAfter)
            if game_over:
                print(message)
                break

            self.change_turn()

        print("Koniec gry.")


def main_test_ai():
    """
    Funkcja pomocnicza do uruchomienia trybu testowego.
    """
    
    #TestModeAI.run_game()


if __name__ == "__main__":
    TestModeAI().run_game()