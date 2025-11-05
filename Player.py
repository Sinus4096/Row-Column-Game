import Strategy

class Player:
    def __init__(self, name="Player", is_human=True, strategy=None):
        self.name = name
        self.is_human = is_human
        self.score = 0
        self.strategy=strategy

    def getName(self):
        return self.name

    def move(self,matrix,last_move=None):
        return self.strategy.move(matrix,last_move)