class Figure:
    def __init__(self, x, y, color, type):
        self.x = x
        self.y = y
        self.type = type
        self.color = color
        self.isAlive = True
    #types: 
    def checkIfMoveIsPossible(self, x, y):
    

    def moveForPawn(self, x, y):
        pass
    def moveForRook(self, x, y):
        pass
    def moveForKnight(self, x, y):
        pass
    def moveForBishop(self, x, y):
        pass
    def moveForQueen(self, x, y):
        moveForRook(x, y)
        moveForBishop(x, y)
    def moveForKing(self, x, y):
        pass