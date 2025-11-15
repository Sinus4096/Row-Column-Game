from typing import List, Optional, Tuple, Dict
from Strategy import Strategy

Coord = Tuple[int, int]
Matrix = List[List[object]]  # numbers or '-' for used cells


class SafeChoiceStrategy(Strategy):
    """
    Strategy that picks a cell based on a composite scoring function

    Scoring for each legal move (i, j):
        my_val = matrix[i][j]
        opp_best = best value opponent can take next after we take (i,j)
        a(i,j), b(i,j) = parity features from row/col max multiplicities (as in your strategy)

        composite_score = α*my_val - β*opp_best + γ*(# of +1 among a,b) + δ*a + ε*b

    Default weights are conservative:
        α=1.0, β=1.0, γ=0.15, δ=0.05, ε=0.05

    Tie-break: higher composite_score, then more +1s, then a, then b, then bottom-rightmost cell.
    """

    def __init__(self,
                 alpha: float = 1.0,
                 beta: float = 1.0,
                 gamma: float = 0.15,
                 delta: float = 0.05,
                 epsilon: float = 0.05,
                 jitter: float = 0.0):
        """
        jitter: set to a tiny value (e.g., 1e-6) if you want to break deep ties non-deterministically.
        """
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.epsilon = epsilon
        self.jitter = jitter

        # simple caches to avoid recomputing summaries repeatedly in one move()
        self._row_summary_cache: Dict[int, Tuple[Optional[float], int, Optional[float], int]] = {}
        self._col_summary_cache: Dict[int, Tuple[Optional[float], int, Optional[float], int]] = {}

    # ---- public API ----
    def move(self, matrix: Matrix, last_move: Optional[Coord], scores) -> Optional[Coord]:
        n = len(matrix)
        if n == 0:
            return None

        # clear caches for this decision
        self._row_summary_cache.clear()
        self._col_summary_cache.clear()

        candidates = self._valid_moves(matrix, last_move)
        if not candidates:
            return None

        best = None
        best_key = None

        for (i, j) in candidates:
            v = self._cell_value(matrix, i, j)
            if v is None:
                # defensive: shouldn't happen due to _valid_moves filter
                continue

            # parity features from current board state
            a = self._parity_from_row_excluding(i, j, v, self._top2_summary_row(matrix, i))
            b = self._parity_from_col_excluding(i, j, v, self._top2_summary_col(matrix, j))
            ones = (1 if a == 1 else 0) + (1 if b == 1 else 0)

            # opponent's best immediate reply after we take (i, j)
            opp_best = self._opponent_best_after(matrix, i, j)

            composite = (
                self.alpha * v
                - self.beta * opp_best
                + self.gamma * ones
                + self.delta * a
                + self.epsilon * b
            )

            # build deterministic ordering key
            # (primary by composite, then parity richness, then a, then b, then bottom-rightmost)
            # add tiny jitter if requested to avoid always picking same path under deep ties
            jitter = 0.0
            if self.jitter:
                import random
                jitter = random.random() * self.jitter

            key = (composite + jitter, ones, a, b, -i, -j)

            if best_key is None or key > best_key:
                best_key = key
                best = (i, j)

        return best

    # ---- helpers: validity & primitive values ----
    @staticmethod
    def _is_free(val: object) -> bool:
        return val != '-'

    @staticmethod
    def _cell_value(matrix: Matrix, i: int, j: int) -> Optional[float]:
        val = matrix[i][j]
        return None if val == '-' else float(val)

    def _valid_moves(self, matrix: Matrix, last_move: Optional[Coord]) -> List[Coord]:
        n = len(matrix)
        if last_move is None:
            return [(i, j) for i in range(n) for j in range(n) if self._is_free(matrix[i][j])]
        r0, c0 = last_move
        out: List[Coord] = []
        seen = set()
        # same row
        for j in range(n):
            if self._is_free(matrix[r0][j]):
                out.append((r0, j))
                seen.add((r0, j))
        # same column
        for i in range(n):
            if self._is_free(matrix[i][c0]) and (i, c0) not in seen:
                out.append((i, c0))
        return out

    # ---- opponent look-ahead (1 ply) ----
    def _opponent_best_after(self, matrix: Matrix, i: int, j: int) -> float:
        """
        After we take (i, j), opponent must play in row i or column j on remaining cells.
        We don't need to mutate the board; just ignore (i, j) in the scan.
        """
        n = len(matrix)
        best_val = float("-inf")

        # row i excluding j
        for jj in range(n):
            if jj == j:
                continue
            v = self._cell_value(matrix, i, jj)
            if v is not None:
                if v > best_val:
                    best_val = v

        # column j excluding i
        for ii in range(n):
            if ii == i:
                continue
            v = self._cell_value(matrix, ii, j)
            if v is not None:
                if v > best_val:
                    best_val = v

        if best_val == float("-inf"):
            return 0.0  # no reply available
        return best_val

    # ---- summaries & parity (reuse your top-2 logic with caching) ----
    def _top2_summary_row(self, matrix: Matrix, i: int):
        if i not in self._row_summary_cache:
            vals = [self._cell_value(matrix, i, j) for j in range(len(matrix)) if self._is_free(matrix[i][j])]
            self._row_summary_cache[i] = self._top2_from_values([v for v in vals if v is not None])
        return self._row_summary_cache[i]

    def _top2_summary_col(self, matrix: Matrix, j: int):
        if j not in self._col_summary_cache:
            vals = [self._cell_value(matrix, i, j) for i in range(len(matrix)) if self._is_free(matrix[i][j])]
            self._col_summary_cache[j] = self._top2_from_values([v for v in vals if v is not None])
        return self._col_summary_cache[j]

    @staticmethod
    def _top2_from_values(vals: List[float]) -> Tuple[Optional[float], int, Optional[float], int]:
        if not vals:
            return (None, 0, None, 0)
        counts: Dict[float, int] = {}
        for x in vals:
            counts[x] = counts.get(x, 0) + 1
        distinct = sorted(counts.keys(), reverse=True)
        top1 = distinct[0]; cnt1 = counts[top1]
        if len(distinct) >= 2:
            top2 = distinct[1]; cnt2 = counts[top2]
        else:
            top2, cnt2 = None, 0
        return (top1, cnt1, top2, cnt2)

    @staticmethod
    def _parity_from_row_excluding(i: int, j: int, v_ij: float,
                                   row_summary: Tuple[Optional[float], int, Optional[float], int]) -> int:
        top1, cnt1, top2, cnt2 = row_summary
        if top1 is None:
            return 1
        if v_ij == top1:
            m = cnt1 - 1 if cnt1 > 1 else cnt2
        else:
            m = cnt1
        return 1 if (m % 2 == 0) else -1

    @staticmethod
    def _parity_from_col_excluding(i: int, j: int, v_ij: float,
                                   col_summary: Tuple[Optional[float], int, Optional[float], int]) -> int:
        top1, cnt1, top2, cnt2 = col_summary
        if top1 is None:
            return 1
        if v_ij == top1:
            m = cnt1 - 1 if cnt1 > 1 else cnt2
        else:
            m = cnt1
        return 1 if (m % 2 == 0) else -1
