import random as rd
from Strategy import Strategy


class RandomStrategy(Strategy):
    """
    Strategy that picks a random cell (not already picked)
    """
    def move(self, matrix,last_move):
        """
        Parameters
        ----------
        matrix : list of lists
            The current board.
        last_move : tuple or None
            The (row, col) of the previous move.
            If None (first turn), pick any available cell.
        """

        n = len(matrix)

        # --- CASE 1: first move (no restrictions) ---
        if last_move is None:
            available = [
                (r, c)
                for r in range(n)
                for c in range(n)
                if matrix[r][c] != '-'
            ]
        else:
            r0, c0 = last_move

            # --- CASE 2: only pick in the same row or column ---
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
    

