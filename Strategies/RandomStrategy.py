import random as rd
from Strategies.Strategy import Strategy


class RandomStrategy(Strategy):
    """ The RandomStrategy class implements a basic strategy for the game
        by inheriting from the abstract `Strategy` class. Its sole purpose is to determine
        the computer player's next move by choosing a randomly selected valid cell
        on the game board.

        The `move` method determines the set of available cells based on the game rules:
        1. First Turn: If it is the first move of the game (`last_move` is `None`),
           any unoccupied cell on the board is considered available.
        2. Subsequent Turns: Otherwise, only unoccupied cells that share the same
           row or the same column as the `last_move` are available.

        From this filtered list of valid moves, the strategy uses Python's `random` module
        to make an unbiased, non-optimal selection, ensuring the move adheres to the game's constraints.
        It returns the chosen `(row, col)` tuple, or `None` if no legal moves remain.
        """

    def move(self, matrix,last_move, scores):
        """
        Parameters
        matrix : list of lists
            The current board.
        last_move : tuple or None
            The (row, col) of the previous move.
            If None (first turn), pick any available cell.
        """

        n = len(matrix)

        # case 1: first move, without restrictions
        if last_move is None:
            print("first turn")
            available = [
                (r, c)
                for r in range(n)
                for c in range(n)
                if matrix[r][c] != '-'
            ]
        else:
            r0, c0 = last_move
            # case 2 : only pick in the same row or column
            available = [
                (r, c)
                for r in range(n)
                for c in range(n)
                if matrix[r][c] != '-' and (r == r0 or c == c0)
            ]

        if not available:
            return None  # no valid move left

        # Pick a random valid cell
        out=rd.choice(available)
        return out
    

