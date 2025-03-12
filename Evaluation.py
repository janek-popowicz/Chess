import board_and_fields
import figures
import engine

class Evaluation:
    def __init__(self, main_board):
        self.main_board = main_board
        self.waga_czarnych = 0
        self.waga_białych = 0
        self.figures_values = {
            'p': 1,
            'N': 3,
            'B': 3,
            'R': 5,
            'Q': 9,
            'K': 1000
        }

    def ocena_materiału(self): 
        for i in range(8):
            for j in range(8):
                field = self.main_board.board_state[i][j]
                if field.figure is None:
                    continue  # Skip if the field does not have a piece
                
                figure = field.figure.return_figure()
                #print(figure)
                
                if len(figure) < 2:
                    continue  # Skip if the figure representation is invalid
                
                piece_type = figure[1]
                piece_color = figure[0]
                
                if piece_color == 'w':
                    self.waga_białych += self.figures_values.get(piece_type, 0)
                else:
                    self.waga_czarnych += self.figures_values.get(piece_type, 0)

        print(f"Final weights - White: {self.waga_białych}, Black: {self.waga_czarnych}")  # Debugging print statement
        return [self.waga_białych, self.waga_czarnych]

