from Strategies.Strategy import Strategy


class GreedyStrategy(Strategy):
    """
    Strategy that picks the highest number
    """

    def move(self, matrix, last_move, scores):
        """
        Parameters
        matrix : list of lists
            The current board.
        last_move : tuple or None
            The (row, col) of the previous move.
            If None (first turn), pick any available cell.
        """

        n= len(matrix)

        #Case 1: first move (no restrictions)
        if last_move is None:
            print("first turn")
            available= [(r, c)
                for r in range(n)
                for c in range(n)
                if matrix[r][c] != '-']
        else:
            r0, c0 = last_move
            #Case 2: only pick in the same row or column
            available= [(r, c)
                for r in range(n)
                for c in range(n)
                if matrix[r][c] != '-' and (r == r0 or c == c0)]

        if not available:
            return None  #no valid move left

        #Pick a random valid cell

        out= max(available, key=lambda pos: float(matrix[pos[0]][pos[1]]))
        return out


