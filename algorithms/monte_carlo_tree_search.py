import copy
import math
import algorithms.evaluation as evaluation
import engine.engine as engine
import random
import engine.fen_operations as fen_operations

class Mcts_optimized: #Niedokończone
    def __init__(self, color):
        """
        Klasa odpowiadająca za AI posługujące się algorytmem Monte Carlo Tree Search, wariant zmodyfikowany:
        w fazie symulacji zamiast rozgrywać pełną symulację, ruch jest ewaluowany, a następnie porównywany z wynikiem dla poprzedniego węzła, jeśli jest większy daje to zwycięstwo, jeśli nie, przegraną

        color - kolor, którym będzie grało AI
        """
        self.root = Node(0, 0, "root",(0,0,0,0), color) #Korzeń drzewa
    def expand_tree(self, board):
        new_board = copy(board)
        # Wybór (selection) 
        current_node = self.root
        while len(current_node.children) > 0:
            max_choice_factor = 0
            chosen_node = self.root
            for child in current_node.children:
                choice_factor = (child.wins / child.games) + math.sqrt(2) * math.sqrt(math.log(child.parent.games) / child.games)
                if choice_factor > max_choice_factor:
                   choice_factor = max_choice_factor
                   chosen_node = child
                   new_board.make_move(*child.move)
            if current_node == chosen_node:
                break
            current_node = chosen_node
        if current_node.parent != "root":
            new_board.make_move(*current_node.move)
        # Rozrost (expansion)
        moves=new_board.get_all_moves('b' if current_node.color == "w" else "w")
        key = random.sample(moves)
        new_node = Node(0,0,current_node, *key,*moves[key],)
        current_node.children += new_node
        # Symulacja (playout)
        old_score = evaluation.Evaluation(new_board) 
        fen = fen_operations.board_to_fen_inverted(new_board,current_node.color)
        new_board.make_move(new_node.move)
        new_score = evaluation.Evaluation(new_board) 
        new_board.board_state = fen_operations.fen_to_board_state(fen)
        new_node.games +=1
        if new_score > old_score:
            new_node.wins += 1
        # Propagacja wsteczna (backpropagation)
        node = new_node
        while node.parent != "root":
            node.parent.games += node.parent.games - node.games
            node.parent.wins += node.parent.wins - node.wins
            node = node.parent

class Mcts:
    def __init__(self, color):
        """
        Klasa odpowiadająca za AI posługujące się algorytmem Monte Carlo Tree Search

        color - kolor, którym będzie grało AI
        """
        self.root = Node(0, 0, "root", (0,0,0,0), "w" if color == "b" else "b") #Korzeń drzewa (kolor korzenia musi być odwrotny, ponieważ zmienia sie on co ruch)
    def expand_tree(self, board, max_depth):
        new_board = copy.deepcopy(board)
        # Wybór (selection) 
        current_node = self.root
        while len(current_node.children) > 0:
            max_choice_factor = -1
            chosen_node = self.root
            depth = 0
            for child in current_node.children:
                # Liczymy wzór UCT 
                if child.games > 0 and child.parent.games > 0: 
                    choice_factor = ((child.wins) / (child.games)) + math.sqrt(2) * math.sqrt(math.log(child.parent.games) / (child.games))
                else:
                    choice_factor = float("inf")
                if choice_factor > max_choice_factor:
                    choice_factor = max_choice_factor
                    chosen_node = child
            engine.tryMove(chosen_node.color, new_board, *chosen_node.move)
            current_node = chosen_node
            depth += 1
            if depth >= max_depth:
                current_node = self.root
        # Rozrost (expansion)
        if current_node.games == 0:
            self.random_expand(new_board,current_node)
            current_node = current_node.children[1]
        # Symulacja (playout)
        result = (1,1,1)
        move_color = self.root.color
        counter = 0
        while result[0] not in  ["checkmate","stalemate"]:
            moves = new_board.get_all_moves(move_color)
            key = random.sample(sorted(moves),1)
            move = random.sample(moves[key[0]],1)
            cords = (*key[0], move[0][0],move[0][1])
            new_board.print_board()
            engine.tryMove(move_color, new_board, *cords)
            move_color = 'b' if move_color == "w" else "w"
            result = engine.afterMove(move_color, new_board, *cords)
            if result[0] == "promotion":
                engine.promotion(move[0][0],move[0][1],new_board,random.randint(1,4))
            counter += 1
        current_node.games +=1
        if result == "checkmate" and move_color == self.root.color:
            current_node.wins +=1  
        # Propagacja wsteczna (backpropagation)
        while current_node.parent != "root":
            current_node.parent.games += current_node.games - current_node.parent.games 
            current_node.parent.wins += current_node.wins - current_node.parent.wins
            current_node = current_node.parent
    def pick_best_move(self,board,limit, max_depth):
        counter = 0
        while limit > counter:
            self.expand_tree(board, max_depth)
            counter += 1
        max_played_games = 0
        for child in self.root.children:
            if child.games > max_played_games:
                chosen_child = child
        return chosen_child.move
    def random_expand(self, board, node):
        """
        Funkcja powiększająca drzewo, wariant losujący 8 z możliwych dzieci, dzięki czemu znacznie szybszy
        """
        for i in range (random.randint(1,8)):
            moves=board.get_all_moves('b' if node.color == "w" else "w")
            key = random.sample(sorted(moves), 1)
            move = random.sample(moves[key[0]], 1) 
            new_node = Node(0,0,node, (*key[0],*move[0]),'b' if node.color == "w" else "w")
            node.children += [new_node]
    def whole_expand(self, board, node):
        """
        Funkcja powiększająca drzewo, wariant uwzględniający wszystkie możliwości UWAGA: Bardzo obciąża komputer
        """
        moves = board.get_all_moves('b' if node.color == "w" else "w")
        for key in moves:
            for move in moves[key]:
                new_node = Node(0,0,node, (*key,*move),'b' if node.color == "w" else "w")
                node.children += [new_node]
                
class Node:
    def __init__(self, games:int, wins:int, parent, move:tuple, color:str, ):
        """
            Klasa reprezentująca węzły drzewa \n
            Args:
                games(int) - zmienna przechowująca ilość rozegranych symulacji w poddrzewie danego węzła.
                wins(int) - zmienna przechowująca ilość wygranych symulacji w poddrzewie danego węzła.
                parent - rodzic danego węzła.
                move(tuple) - ruch, który dany węzeł przechowuje.
                children - lista dzieci danego węzła.
                color - kolor ruchu, który przechowuje węzęł
        """
        self.games = games
        self.wins = wins
        self.parent = parent
        self.move = move
        self.children = []
        self.color = color

