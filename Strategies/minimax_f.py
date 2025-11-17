import math
from copy import deepcopy
import sys
import os
from typing import List, Optional, Tuple

# Look for "Strategy" in the parent directory (your original structure)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Strategy import Strategy


class AlphaBetaNode:
    """
    A node representing a specific Row-Column game state.
    Nodes are treated as immutable snapshots: board, last_move, whose turn, scores.
    """
    def __init__(
        self,
        board: List[List[int]],
        last_move: Optional[Tuple[int, int]],
        player_id: int,
        parent: Optional["AlphaBetaNode"] = None,
        move: Optional[Tuple[int, int]] = None,
        scores: Tuple[int, int] = (0, 0),
    ):
        # Board uses 0 to denote "taken" cells. Only non-zero cells are available.
        # This node does not mutate its board (children get deep copies).
        self.board = board
        self.last_move = last_move
        self.player_id = player_id          # 1 or 2: whose turn at THIS node
        self.parent = parent
        self.move = move                    # move taken from parent to reach this node
        self.scores = scores                # (score_p1, score_p2)
        self.children: List["AlphaBetaNode"] = []
        self._cached_moves: Optional[List[Tuple[int, int]]] = None  # avoid recompute

    def get_available_moves(self) -> List[Tuple[int, int]]:
        """
        Return all valid moves from the current state.
        Caches the result since nodes are immutable snapshots.
        """
        if self._cached_moves is not None:
            return self._cached_moves

        if self.last_move is None:
            moves = [(r, c)
                     for r, row in enumerate(self.board)
                     for c, val in enumerate(row) if val != 0]
            self._cached_moves = moves
            return moves

        last_r, last_c = self.last_move
        moves: List[Tuple[int, int]] = []

        # Same row
        for c, val in enumerate(self.board[last_r]):
            if val != 0:
                moves.append((last_r, c))

        # Same column (avoid duplicating the (last_r, last_c) intersection)
        for r, row in enumerate(self.board):
            if r != last_r and row[last_c] != 0:
                moves.append((r, last_c))

        self._cached_moves = moves
        return moves

    def is_terminal(self) -> bool:
        """No valid moves remain in the current row/column band."""
        return len(self.get_available_moves()) == 0

    def generate_children(self) -> List["AlphaBetaNode"]:
        """
        Create child nodes for all possible moves from this state.
        Results are cached in self.children to avoid regeneration.
        """
        if self.children:
            return self.children

        next_player_id = 3 - self.player_id  # swap 1 <-> 2
        for move in self.get_available_moves():
            r, c = move
            val = self.board[r][c]

            # Copy board and mark the move as taken
            new_board = [row[:] for row in self.board]
            new_board[r][c] = 0

            # Update scores (current node's player collects the value)
            s1, s2 = self.scores
            if self.player_id == 1:
                s1 += val
            else:
                s2 += val

            child = AlphaBetaNode(
                board=new_board,
                last_move=move,
                player_id=next_player_id,
                parent=self,
                move=move,
                scores=(s1, s2),
            )
            self.children.append(child)
        return self.children


class AlphaBetaStrategy(Strategy):
    def __init__(self, max_nodes_budget: int = 60_000, hard_depth_cap: int = 12):
        """
        max_nodes_budget: target upper bound on nodes per move (rough heuristic).
        hard_depth_cap: never search deeper than this (safety).
        """
        self.max_nodes_budget = max_nodes_budget
        self.hard_depth_cap = hard_depth_cap
        self.player_id = 1  # set in move()

    def _dynamic_depth(self, board, last_move) -> int:
        """
        Pick a depth that fits the board size and remaining moves,
        assuming effective branching ~ min(2N-1, 10). Then solve b^d ≈ budget.
        """
        n = len(board)
        nonzero = sum(1 for r in board for v in r if v != 0)
        # effective branching after the first move; clamp for sanity
        b = max(2, min(2 * n - 1, 10))

        # solve b^d <= budget  ->  d <= log(budget)/log(b)
        import math
        d = int(math.floor(math.log(max(self.max_nodes_budget, 2), b)))
        # never exceed remaining plies or the hard cap
        d = min(d, nonzero, self.hard_depth_cap)

        # small boards can afford more depth
        if n <= 3:
            d = min(nonzero, 9)  # full search on 3x3
        elif n == 4:
            d = min(d + 1, nonzero)  # a gentle boost
        return max(1, d)

    def move(self, board, last_move, scores):
        # normalize "-" -> 0
        internal_board = [[0 if cell == "-" else cell for cell in row] for row in board]

        # whose turn?
        moves_made = sum(row.count(0) for row in internal_board)
        player_id = 2 if moves_made % 2 else 1
        self.player_id = player_id

        root = AlphaBetaNode(internal_board, last_move, player_id, scores=scores)
        if root.is_terminal():
            return None

        # choose depth dynamically
        depth = self._dynamic_depth(internal_board, last_move)

        best_move, best_val = None, -math.inf
        children = root.generate_children()
        # root move ordering: try larger picks first (helps pruning)
        children.sort(key=lambda ch: ch.board[ch.move[0]][ch.move[1]], reverse=True)

        for ch in children:
            val = self.alpha_beta(ch, depth - 1, -math.inf, math.inf, False)
            if val > best_val:
                best_val, best_move = val, ch.move

        if best_move is None:
            # fallback: greedy
            avail = root.get_available_moves()
            best_move = max(avail, key=lambda m: internal_board[m[0]][m[1]])
        return best_move

    # ---------- Heuristic (root-player centric) ----------

    def evaluate(self, node: AlphaBetaNode) -> float:
        """
        Fast heuristic. Positive is better for the ROOT player (self.player_id).
        Terms:
          - score difference (me - opp)
          - mobility proxy (who is to move soon and how many options)
          - row/column potential around the last move (available totals)
        """
        p = self.player_id  # Root player id
        me  = node.scores[p - 1]
        opp = node.scores[2 - p]
        score_diff = me - opp

        # Mobility proxy: favor states where the ROOT will soon have many options
        my_moves = 0
        opp_moves = 0
        # If next player to move equals root, then mobility is about this node
        avail = node.get_available_moves()
        if node.player_id == p:
            my_moves = len(avail)
        else:
            opp_moves = len(avail)

        # Row/col potential based on last move band (remaining sums)
        row_col_potential = 0
        if node.last_move is not None:
            r, c = node.last_move
            n = len(node.board)
            # sum remaining values in row r and col c
            row_sum = sum(v for v in node.board[r] if v != 0)
            col_sum = sum(node.board[rr][c] for rr in range(n) if node.board[rr][c] != 0)
            row_col_potential = row_sum + col_sum

        # Tunable weights (kept small to maintain evaluation stability)
        return (
            1.0 * score_diff +
            0.25 * (my_moves - opp_moves) +
            0.05 * row_col_potential
        )

    # ---------- Alpha-Beta core with move ordering ----------

    def alpha_beta(self, node: AlphaBetaNode, depth: int, alpha: float, beta: float, maximizing_player: bool) -> float:
        # Terminal or cutoff
        if depth == 0 or node.is_terminal():
            return self.evaluate(node)

        children = node.generate_children()

        # Move ordering:
        # For maximizing (root's opponent False/True alternates), order using the
        # root-player's current score seen in child to bias toward promising branches.
        root_pid = self.player_id
        if maximizing_player:
            # MAX node: try children that improve ROOT's score sooner
            children.sort(key=lambda ch: ch.scores[root_pid - 1], reverse=True)
            value = -math.inf
            for child in children:
                value = max(value, self.alpha_beta(child, depth - 1, alpha, beta, False))
                alpha = max(alpha, value)
                if beta <= alpha:
                    break  # Beta cut
            return value
        else:
            # MIN node: try children that hurt ROOT's score sooner
            children.sort(key=lambda ch: ch.scores[root_pid - 1])
            value = math.inf
            for child in children:
                value = min(value, self.alpha_beta(child, depth - 1, alpha, beta, True))
                beta = min(beta, value)
                if beta <= alpha:
                    break  # Alpha cut
            return value
