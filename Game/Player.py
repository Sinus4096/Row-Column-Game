from Strategies.Strategy import Strategy

class Player:
    """ The Player class serves as a data structure and interface to represent a participant
        in the game, whether human or computer. It stores the player's identity and
        enables the execution of moves.

        Key features:
        1. Identity: Stores the player's `name` and whether they are a `is_human`.
        2. Score Tracking: Although the score is primarily managed by the `GameHandler`,
           the player object includes a placeholder for its individual score.
        3. AI Integration: For computer players (`is_human=False`), it holds a reference
           to a specific `Strategy` object (e.g., GreedyStrategy, MCTS).
        4. Move Delegation: The `move` method is the core interface for the `GameHandler`.
           For computer players, this method delegates the decision-making process—determining
           the next row and column to click—to the associated `strategy` object. Human
           player moves are handled directly by the GUI (`Board`) and processed by the
           `GameHandler`.
        """

    def __init__(self, name="Player", is_human=True, strategy=None):
        self.name = name
        self.is_human = is_human
        self.score = 0
        self.strategy=strategy

    def getName(self):
        return self.name

    def move(self, matrix, last_move=None, scores=(0, 0)):
        return self.strategy.move(matrix, last_move, scores)