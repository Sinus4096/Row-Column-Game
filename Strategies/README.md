# Strategies

This folder contains all decision-making strategies used by the Computer Player.  
Each strategy inherits from `Strategy.py` and implements its own method for selecting actions.

Below you will find detailed descriptions of each strategy, including methodology,
use-cases, and implementation details.

- [Strategies](#strategies)
  - [Strategy Overview](#strategy-overview)
  - [Detailed Strategy Descriptions](#detailed-strategy-descriptions)
    - [Greedy Strategy](#1-greedy-strategy)
    - [Random Strategy](#2-random-strategy)
    - [Monte Carlo Tree Search (MCTS)](#3-monte-carlo-tree-search-mcts)
    - [Minimax Strategy](#4minimax-strategy)
    - [Safe Choice Strategy](#5-safe-choice-strategy)
  - [Adding a New Strategy](#adding-a-new-strategy)

---

# Strategy Overview

| Strategy Name           | File                      | Short Summary                                      |
|-------------------------|---------------------------|----------------------------------------------------|
| Greedy Strategy         | `GreedyStrategy.py`       | Chooses highest immediate reward                   |
| Random Strategy         | `RandomStrategy.py`       | Picks a random legal move                          |
| Monte Carlo Tree Search | `MCTS.py`                 | Monte Carlo Tree Search with rollouts              |
| Minimax Strategy        | `minimax_f.py`            | Depth-limited minimax with alpha–beta pruning      |
| Safe Choice Strategy    | `safe_choice_strategy.py` | Greedy strategy enhanced with defensive heuristics |

---

# Detailed Strategy Descriptions

## 1. Greedy Strategy
**File:** `GreedyStrategy.py`

**Summary:**  
Selects the move that maximizes the immediate score gain without considering future consequences.

**Characteristics:**
- No look-ahead
- Fast, baseline heuristic
- Useful for debugging or comparisons

---

## 2. Random Strategy
**File:** `RandomStrategy.py`

**Summary:**  
Chooses uniformly from all legal moves.

**Characteristics:**
- Strong baseline for benchmarking
- Helps evaluate whether smarter strategies are actually improving performance

---

## 3. Monte Carlo Tree Search (MCTS)
**File:** `MCTS.py`

**Summary:**  
This strategy applies Monte Carlo Tree Search, a simulation-based decision method that evaluates moves by repeatedly exploring possible future sequences 
of the game. Instead of computing a full search tree in advance, it incrementally builds and updates a tree based on statistical feedback from many 
simulated plays. The approach is well suited for game states with unpredictable structure, because it automatically focuses computational effort on the most 
promising moves as evidence accumulates. 

Algorithm reference:  
[Monte Carlo Tree Search — GeeksForGeeks](https://www.geeksforgeeks.org/monte-carlo-tree-search-mcts-in-machine-learning/)


**Key Components:**
- Selection (UCT)
- Expansion
- Simulation
- Backpropagation

### **Description of Individual Steps**

#### **1. Selection (UCB1-Guided Search)**
During search, the algorithm traverses the current tree using the Upper Confidence Bound (UCB1) formula:

$$
\text{UCB1}(i) = \bar{X}_i + c \sqrt{\frac{\ln(N)}{n_i}}
$$

Where:

* $\bar{X}_i$ — average simulation outcome
* $n_i$ — visits to this move
* $N$ — total visits to the parent
* $c = \sqrt{2}$ — exploration constant 

This balances *exploitation* of strong-performing moves with *exploration* of lesser-tested moves.

#### **2. Expansion**
When a state still has unexplored legal moves, one is selected and added as a new child node.  
The tree grows only where necessary, minimizing wasted computation.

#### **3. Simulation (Rollout)**
From the expanded node, the strategy plays out a fast simulated game until no moves remain.  
Rollouts use an $\epsilon$-greedy policy with ( $\epsilon= 0.5$):

- 50% random move  
- 50% highest-value move  

This provides a mixture of exploration and efficient scoring.  
The final score difference (normalized by the board total) represents the rollout outcome.

#### **4. Backpropagation**
The simulation result is propagated back to the root:

- visit counts are increased  
- accumulated rollout values are updated  

Nodes on well-performing paths become more attractive in future selections.

#### **5. Final Move Decision**
MCTS repeats the four phases until one of these limits is reached:

- maximum 100,000 iterations, or  
- maximum 5 seconds compute time, whichever comes first.

The strategy then chooses the child of the root with the highest visit count.

**Strengths** 
- Naturally balances exploration vs. exploitation  
- Does not require fixed-depth search or heuristics  


---

## 4.Minimax Strategy
**File:** `minimax_f.py`

**Summary:** This strategy implements a depth-limited minimax algorithm enhanced with alpha–beta pruning and dynamic depth control. It is designed specifically for the Row–Column Game, where
each move restricts the next move to the same row or column of the previously chosen cell.

### Description  

#### 1. Node Representation:
Each AlphaBetaNode is an immutable snapshot of the game state, containing:
* board configuration,
* last move coordinate,
* player to move,
* accumulated scores for both players.

Children are generated only once and cached.

#### 2. Move Generation:
Legal moves follow the Row–Column restriction:
* If no move has been played yet: any non-zero cell.
* Otherwise: any non-zero cell in the last move’s row or column.

This rule shapes the branching factor of the game tree.

#### 3. Search Depth Selection (Dynamic):
The available search depth is computed from:
* estimated branching factor $b \approx 2n - 1$
* a global node budget (`max_nodes_budget`)
* remaining possible moves (`nonzero`)
* a safety hard cap (`hard_depth_cap`)

The depth $d$ is chosen so that: `b^d <= max_nodes_budget`
and clamped to avoid overly deep search. Small boards ($3 \times 3$, $4 \times 4$) receive special-case deeper search.

#### 4. Alpha–Beta Minimax Search:
The strategy explores the game tree recursively:
* maximizing nodes choose the move best for the ROOT player,
* minimizing nodes simulate the opponent’s reply.

Alpha–beta pruning discards branches that cannot affect the final decision (none of the players would ever let the game to reach that state, node), 
dramatically improving performance. Move ordering (sorting children by score potential) makes pruning more effective.

#### 5. Evaluation Function (Heuristic at Depth Cutoff):
When the search reaches a terminal state or depth limit, the node is evaluated using:
* exact score difference ($\text{me - opp}$),
* mobility (legal move count advantage),
* "row/col potential" (remaining sum in the current row and column).

These components provide a fast approximation of the position's quality for the root player when full search is computationally infeasible.

#### 6. Final Move Selection:
The root examines all possible first moves, evaluates each via alpha–beta minimax, and returns the move that yields the highest evaluation score. 
A fallback greedy rule is used only if all evaluations fail (highly unlikely).


#### Overall:
This strategy combines selective deep searching (minimax), aggressive pruning (alpha–beta), and informed cutoff evaluation to create a strong but 
computationally feasible decision-making agent. It performs full decision tree search on very small boards and adopts heuristic-limited search on larger 
boards, achieving a balance between performance and speed.

**Strengths**
- Greatly reduces number of explored nodes  
- Allows deeper search within the same runtime  
- Preserves optimal decision quality  

---

## 5. Safe Choice Strategy
**File:** `safe_choice_strategy.py`

**Summary:**  An optimized greedy strategy that evaluates each legal move using a composite scoring function.  
It combines immediate gain, a 1-play opponent look-ahead, and row/column parity heuristics.  
Safer and smarter than pure greedy, but still extremely fast (no tree search).

**Characteristics**
- Greedy with opponent-penalty  
- 1-ply look-ahead (opponent’s best reply)  
- Parity features from row/column maxima  
- Deterministic tie-breaking with optional jitter


### Description

#### Core Idea
For each legal move (i,j), the strategy computes a composite score:

$$
\text{score}(i,j)
= \alpha\,v(i,j)
- \beta\,\text{opp\_best}(i,j)
+ \gamma\,\#\{a(i,j), b(i,j)=+1\}
+ \delta\,a(i,j)
+ \epsilon\,b(i,j)
$$

where:

- $v(i,j)$ — value of the chosen cell  
- $\text{opp\_best}(i,j)$ — opponent’s best immediate reply in row $i$ or column $j$  
- $a(i,j), b(i,j)$ — parity features from the row/column after hypothetically removing $(i,j)$  


Default conservative weights:

$$
\alpha = 1.0,\quad
\beta = 1.0,\quad
\gamma = 0.15,\quad
\delta = 0.05,\quad
\epsilon = 0.05
$$


#### Components

**1. Your Value**
The immediate gain:
$$
v(i,j) = \text{matrix}[i][j].
$$

**2. Opponent’s Best Reply (1-ply Safety Check)**
After taking (i,j), the opponent must play in row i or column j.  
Define:

$$
\text{opp\_best}(i,j)
= \max\Big( \{\,v(i,k)\mid k\neq j\,\}
\cup
\{\,v(k,j)\mid k\neq i\,\} \Big)
$$
If no reply exists, $\text{opp\_best}=0$.

This heavily penalizes moves that open large rewards to the opponent.

**3. Parity Features**
For each row and column, the strategy keeps track of the largest values and how many times they appear:

$$
(\text{top1},\,\text{cnt}_1,\,\text{top2},\,\text{cnt}_2)
$$

When we consider taking a cell (i,j), the strategy pretends that this value is removed and checks whether the remaining largest value in that row or column appears an even or odd number of times.

This gives the parity features:

$$
a(i,j)=
\begin{cases}
+1 & \text{if the row’s new max-count is even} \\
-1 & \text{if it is odd}
\end{cases}
$$

and the same rule defines $b(i,j)$ for the column.

Intuition:  
Rows/columns with an even number of maximum values are considered a bit “safer,” so the score gives small bonuses when a or b) equals +1.


#### Final Move Decision

After scoring all legal moves, the strategy picks the best one using this order of preference:

1. highest composite score  
2. more +1 parity signals  
3. better row parity a, then column parity b  
4. bottom-right position (using -i,-j as a tiebreaker)  
5. tiny random jitter (optional)  

The move with the best overall key is selected.


**Strengths**
- Significantly safer than greedy   
- Avoids obvious traps by accounting for opponent gain  
- Adds structural awareness via parity heuristics
- Very lightweight compared to Minimax or MCTS  

---

# Adding a New Strategy

To add a new strategy:

1. Create a new file in this folder, e.g. `MyStrategy.py`
2. Inherit from the base class:

```python
from Strategy import Strategy

class MyStrategy(Strategy):
    def choose_action(self, state):
        #new strategy here logic here
        pass
```
