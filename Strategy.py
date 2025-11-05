import random as rd

class Strategy:
    """
    Base class for game strategies
    Every substrategy has to implement the method move
    """
    def move(self, matrix,last_move):
        raise NotImplementedError("You must implement the method move()")
