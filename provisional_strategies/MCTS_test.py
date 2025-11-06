import random
import math

class RCGame:
    def __init__(self, board, board_size=None):
        if board_size is None:
            self.board_size = len(board)
        else:
            self.board_size = board_size
        
        # Ensure the board is a deep copy to avoid modifying the original list passed in
        self.board = [row[:] for row in board]
        
        self.scores = {'A': 0, 'B': 0}
        self.last_choice = None # (row, col) of the last chosen number
        self.current_player = 'A'
        self.history = [] # To store (player, chosen_number, board_state, scores, last_choice)

    def is_game_over(self):
        # Game ends if no more numbers are available to choose
        return not any(cell is not None for row in self.board for cell in row)

    def get_available_moves(self):
        moves = []
        if self.last_choice is None:
            # First player can choose any available number
            for r in range(self.board_size):
                for c in range(self.board_size):
                    if self.board[r][c] is not None:
                        moves.append((r, c))
        else:
            # Subsequent players choose from the same row or column as the last choice
            last_row, last_col = self.last_choice
            for c in range(self.board_size): # Same row
                if self.board[last_row][c] is not None:
                    moves.append((last_row, c))
            for r in range(self.board_size): # Same column
                # Make sure to not add the same move twice if the last_choice cell
                # is both in the row and column (and not None)
                if self.board[r][last_col] is not None and (r, last_col) not in moves:
                    moves.append((r, last_col))
        return moves

    def make_move(self, row, col):
        if self.board[row][col] is None:
            raise ValueError(f"Invalid move: Cell ({row}, {col}) is empty.")
        if (row, col) not in self.get_available_moves():
            raise ValueError(f"Invalid move: ({row}, {col}) not in available moves.")

        chosen_number = self.board[row][col]
        self.scores[self.current_player] += chosen_number
        self.board[row][col] = None # Remove the number from the board
        self.last_choice = (row, col)

        self.history.append({
            'player': self.current_player,
            'chosen_number': chosen_number,
            'board_state': [row[:] for row in self.board], # Deep copy
            'scores': self.scores.copy(),
            'last_choice': self.last_choice
        })

        self.current_player = 'B' if self.current_player == 'A' else 'A' # Switch player

    def get_winner(self):
        if not self.is_game_over():
            return None # Game not over yet
        if self.scores['A'] > self.scores['B']:
            return 'A'
        elif self.scores['B'] > self.scores['A']:
            return 'B'
        else:
            return 'Draw'

    def display_board(self):
        print("Board:")
        for r in range(self.board_size):
            for c in range(self.board_size):
                val = self.board[r][c]
                print(f"{val if val is not None else '-':>2}", end=" ")
            print()
        print(f"Scores: A={self.scores['A']}, B={self.scores['B']}")
        if self.last_choice:
            print(f"Last choice: {self.last_choice} (value {self.history[-1]['chosen_number'] if self.history else 'N/A'})")
        print(f"Current Player: {self.current_player}")
        print("-" * (self.board_size * 3))

    def get_state(self):
        return {
            'board': [row[:] for row in self.board],
            'scores': self.scores.copy(),
            'last_choice': self.last_choice,
            'current_player': self.current_player
        }

    def set_state(self, state):
        self.board = [row[:] for row in state['board']]
        self.scores = state['scores'].copy()
        self.last_choice = state['last_choice']
        self.current_player = state['current_player']

class MCTSNode:
    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move # The move that led to this state
        self.children = []
        self.visits = 0
        self.wins = 0 # Wins for the player *who just made the move to reach this state*

    def uct(self, exploration_constant=math.sqrt(2)):
        if self.visits == 0:
            return float('inf') # Prioritize unvisited nodes
        
        if self.parent is None or self.parent.visits == 0: # Avoid division by zero if parent not visited
             return float('inf')

        exploitation_term = self.wins / self.visits
        exploration_term = exploration_constant * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation_term + exploration_term

    def is_fully_expanded(self):
        game_board_from_state = self.state['board']
        game = RCGame(game_board_from_state)
        game.set_state(self.state)
        return len(self.children) == len(game.get_available_moves())

    def is_terminal_node(self):
        game_board_from_state = self.state['board']
        game = RCGame(game_board_from_state)
        game.set_state(self.state)
        return game.is_game_over()

class MCTS:
    def __init__(self, game_state, iterations=1000, exploration_constant=math.sqrt(2)):
        self.root = MCTSNode(game_state)
        self.iterations = iterations
        self.exploration_constant = exploration_constant

    def _select(self, node):
        while not node.is_terminal_node():
            if not node.is_fully_expanded():
                return self._expand(node)
            else:
                if not node.children: # If fully expanded but no children (e.g., all moves are invalid/game over)
                    return node # This node itself is effectively a leaf for selection
                node = max(node.children, key=lambda child: child.uct(self.exploration_constant))
        return node

    def _expand(self, node):
        game_board_from_state = node.state['board']
        game = RCGame(game_board_from_state)
        game.set_state(node.state)
        
        tried_moves = [child.move for child in node.children]
        available_moves = game.get_available_moves()
        
        untried_moves = [move for move in available_moves if move not in tried_moves]
        
        if not untried_moves:
            return node # No more moves to expand, return the current node as a leaf
        
        move = random.choice(untried_moves)
        
        # Create a new game state for the child node
        new_game = RCGame(game_board_from_state) # Pass the board config
        new_game.set_state(node.state)
        
        try:
            new_game.make_move(move[0], move[1])
            child_node = MCTSNode(new_game.get_state(), parent=node, move=move)
            node.children.append(child_node)
            return child_node
        except ValueError: # Catch invalid moves that might slip through get_available_moves due to race conditions or subtle logic
            # If a move is invalid during expansion, just return the current node
            # and let the next iteration try another untried move.
            # This is a defensive measure and ideally get_available_moves should prevent this.
            return node

    def _simulate(self, node):
        game_board_from_state = node.state['board']
        game = RCGame(game_board_from_state) # Pass the board config
        game.set_state(node.state)

        while not game.is_game_over():
            available_moves = game.get_available_moves()
            if not available_moves:
                break # No moves left
            move = random.choice(available_moves)
            try:
                game.make_move(move[0], move[1])
            except ValueError:
                # This should ideally not happen if get_available_moves is correct,
                # but it's a safeguard for simulations. If an invalid move is chosen,
                # it means the available_moves were incorrect or the state became inconsistent.
                # In simulation, we can just break and let the current scores be the outcome.
                break 
        
        winner = game.get_winner()
        return winner, game.scores # Return winner and final scores

    def _backpropagate(self, node, winner, final_scores):
        while node is not None:
            node.visits += 1
            if node.parent is not None: # Root has no parent
                # Determine whose 'win' this is for. The 'wins' count for a node
                # represents wins for the player who made the move *to reach* that node.
                # The current_player in node.state is the player *whose turn it is next*.
                # So, the player who *just played* to get to 'node.state' is the opposite.
                player_who_made_move_to_node = 'B' if node.state['current_player'] == 'A' else 'A'
                
                if winner == player_who_made_move_to_node:
                    node.wins += 1
                elif winner == 'Draw':
                    node.wins += 0.5 # For draws, split the win credit
                # If winner is the other player, node.wins remains unchanged
            node = node.parent

    def get_best_move(self):
        for _ in range(self.iterations):
            leaf = self._select(self.root)
            if not leaf.is_terminal_node():
                # If leaf is not fully expanded, _select would have returned an expanded child.
                # If leaf is fully expanded but has no children, it's treated as a leaf.
                # So we simulate from the leaf directly if it's not a terminal node.
                winner, final_scores = self._simulate(leaf)
                self._backpropagate(leaf, winner, final_scores)
            else:
                # If the selected node is terminal, backpropagate its result directly
                game_board_from_state = leaf.state['board']
                game = RCGame(game_board_from_state) # Pass the board config
                game.set_state(leaf.state)
                winner = game.get_winner()
                self._backpropagate(leaf, winner, game.scores)

        # After all iterations, choose the child of the root with the highest visit count
        if not self.root.children:
            # This happens if the root state is terminal, or no valid moves from root,
            # or all moves lead to immediate terminal states and no children were properly developed.
            game = RCGame(self.root.state['board'])
            game.set_state(self.root.state)
            if not game.get_available_moves():
                print("MCTS: No available moves from the root state. Game likely over or stalled.")
            return None # No possible moves from the root

        # Choose the move with the highest visit count
        best_child = max(self.root.children, key=lambda child: child.visits)
        return best_child.move

def play_game_with_mcts(initial_board, mcts_iterations=1000):
    game = RCGame(initial_board)
    print("Initial Game State:")
    game.display_board()

    # Player A (first player) chooses randomly as per the problem
    print("Player A (first player) choosing randomly...")
    available_moves_A = game.get_available_moves()
    if available_moves_A:
        first_move_A = random.choice(available_moves_A)
        game.make_move(first_move_A[0], first_move_A[1])
        print(f"Player A chose: {game.history[-1]['chosen_number']} at {first_move_A}")
        game.display_board()
    else:
        print("No moves available for Player A. Game ends immediately.")
        print("Game Over!")
        winner = game.get_winner()
        print(f"Final Scores: A={game.scores['A']}, B={game.scores['B']}")
        if winner:
            print(f"Winner: {winner}")
        else:
            print("It's a draw!")
        return

    while not game.is_game_over():
        print(f"Player {game.current_player}'s turn (MCTS)..")
        mcts = MCTS(game.get_state(), iterations=mcts_iterations)
        best_move = mcts.get_best_move()

        if best_move:
            game.make_move(best_move[0], best_move[1])
            print(f"Player {game.history[-1]['player']} chose: {game.history[-1]['chosen_number']} at {best_move}")
        else:
            print(f"Player {game.current_player} has no available moves. Game ends.")
            break # Exit the loop if MCTS finds no best move (meaning no available moves)
        game.display_board()

    print("Game Over!")
    winner = game.get_winner()
    print(f"Final Scores: A={game.scores['A']}, B={game.scores['B']}")
    if winner:
        print(f"Winner: {winner}")
    else:
        print("It's a draw!")

# --- Example Usage with a Given Matrix ---
if __name__ == "__main__":
    # Example 3x3 board from the problem description
    given_matrix = [
        [2, 4, 6],
        [3, 5, 7],
        [5, 1, 3]
    ]

    print("Playing with a 3x3 given matrix:")
    play_game_with_mcts(given_matrix, mcts_iterations=2000) # Increased iterations for better performance

    print("\n" + "="*30 + "\n")

    # Another example with a different 3x3 matrix
    another_matrix = [
        [9, 1, 8],
        [2, 7, 3],
        [4, 6, 5]
    ]
    print("Playing with another 3x3 given matrix:")
    play_game_with_mcts(another_matrix, mcts_iterations=2000)

    print("\n" + "="*30 + "\n")
