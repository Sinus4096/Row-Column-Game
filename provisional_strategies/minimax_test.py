import math
import random

class RCGame:
    def __init__(self, board):
        self.initial_board = [row[:] for row in board] # Deep copy
        self.board = [row[:] for row in board]
        self.rows = len(board)
        self.cols = len(board[0])
        self.player_scores = {'A': 0, 'B': 0}
        self.current_player = 'A'
        self.last_chosen_pos = None # (row, col) of the last chosen number
        self.moves_made = 0
        self.taken_numbers = set() # Store (value, row, col) of taken numbers for clarity in printing

    def reset_game(self):
        self.board = [row[:] for row in self.initial_board]
        self.player_scores = {'A': 0, 'B': 0}
        self.current_player = 'A'
        self.last_chosen_pos = None
        self.moves_made = 0
        self.taken_numbers = set()

    def get_available_moves(self, last_pos):
        moves = []
        if last_pos is None: # First move, all numbers are available
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.board[r][c] is not None:
                        moves.append(((r, c), self.board[r][c]))
        else:
            r_last, c_last = last_pos
            # Numbers in the same row
            for c in range(self.cols):
                if self.board[r_last][c] is not None:
                    moves.append(((r_last, c), self.board[r_last][c]))
            # Numbers in the same column
            for r in range(self.rows):
                # Ensure we don't add duplicates if the number is at the intersection
                if self.board[r][c_last] is not None and (r, c_last) not in [m[0] for m in moves if m[0][0] == r_last]:
                    moves.append(((r, c_last), self.board[r][c_last]))
        return moves

    def make_move(self, pos):
        r, c = pos
        value = self.board[r][c]
        if value is None:
            raise ValueError(f"Invalid move: ({r}, {c}) is already taken.")

        self.player_scores[self.current_player] += value
        self.board[r][c] = None # Mark as taken
        self.last_chosen_pos = pos
        self.moves_made += 1
        self.taken_numbers.add((value, r, c))

        self.current_player = 'B' if self.current_player == 'A' else 'A' # Switch player
        return value

    def is_game_over(self):
        if self.moves_made == self.rows * self.cols:
            return True
        if self.last_chosen_pos is None and self.moves_made == 0: # Game just started, not over
            return False
        return not self.get_available_moves(self.last_chosen_pos)

    def print_board(self, highlight_pos=None):
        print("Board:")
        for r in range(self.rows):
            for c in range(self.cols):
                val = self.board[r][c]
                if val is None:
                    print(" X ", end=" ")
                elif highlight_pos == (r, c):
                    print(f"[{val}]", end=" ") # Highlight selected number
                else:
                    print(f"{val:2d} ", end=" ")
            print()
        print("-" * (self.cols * 4))

    def get_winner(self):
        if not self.is_game_over():
            return "Game not over"
        if self.player_scores['A'] > self.player_scores['B']:
            return "Player A wins!"
        elif self.player_scores['B'] > self.player_scores['A']:
            return "Player B wins!"
        else:
            return "It's a tie!"

    def get_state_copy(self):
        """Returns a deep copy of the current game state."""
        new_game = RCGame(self.initial_board) # Re-initialize with original board
        new_game.board = [row[:] for row in self.board] # Copy current board state
        new_game.player_scores = self.player_scores.copy()
        new_game.current_player = self.current_player
        new_game.last_chosen_pos = self.last_chosen_pos
        new_game.moves_made = self.moves_made
        new_game.taken_numbers = self.taken_numbers.copy()
        return new_game

class Heuristics:
    @staticmethod
    def calculate(game_state, maximizing_player):
        """
        Calculates a heuristic value for the given game_state from the perspective
        of the maximizing_player.
        """
        player_score = game_state.player_scores[maximizing_player]
        opponent_player = 'B' if maximizing_player == 'A' else 'A'
        opponent_score = game_state.player_scores[opponent_player]

        # Weights for heuristics (can be tuned)
        W_SCORE_DIFF = 100
        W_AVAILABLE_SELF = 5
        W_FUTURE_OPTIONS_OPPONENT = -8 # Penalize opening good options for opponent

        heuristic_value = 0

        # 1. Score Difference Heuristic
        heuristic_value += W_SCORE_DIFF * (player_score - opponent_score)

        # 2. Available Numbers Value Heuristic for the player whose turn it is
        # If it's the maximizing_player's turn, this is good. If it's the opponent's turn, this is bad for us.
        current_available_moves = game_state.get_available_moves(game_state.last_chosen_pos)
        current_available_value = sum(val for _, val in current_available_moves)

        if game_state.current_player == maximizing_player:
            heuristic_value += W_AVAILABLE_SELF * current_available_value
        else: # It's the opponent's turn, so current available moves are their advantage
            heuristic_value += W_FUTURE_OPTIONS_OPPONENT * current_available_value

        return heuristic_value

class AIPlayer:
    def __init__(self, player_id, depth):
        self.player_id = player_id
        self.max_depth = depth

    def get_best_move(self, game_state, is_first_move_of_game=False):
        # This parameter controls if *this specific move* should be random.
        # It's set to True *only* for the very first move of the entire game.
        if is_first_move_of_game:
            print(f"\n--- Player {self.player_id}'s Turn: First move of game (random) ---")
            available_moves = game_state.get_available_moves(None)
            if not available_moves:
                print("No moves available for AI (first move of game).")
                return None
            chosen_move = random.choice(available_moves)
            return chosen_move[0] # Return just the position

        best_value = -math.inf
        best_move = None
        
        possible_moves = game_state.get_available_moves(game_state.last_chosen_pos)

        print(f"\n--- Player {self.player_id}'s Turn: Evaluating Moves (Depth {self.max_depth}) ---")
        print(f"Possible moves for {self.player_id}: {[(pos, val) for pos, val in possible_moves]}")

        if not possible_moves:
            print("No moves available for AI.")
            return None # No moves possible

        # If there's only one move, just take it to avoid unnecessary minimax
        if len(possible_moves) == 1:
            print(f"  Only one move available: ({possible_moves[0][0][0]},{possible_moves[0][0][1]}) value {possible_moves[0][1]}")
            return possible_moves[0][0]

        for move_pos, move_value in possible_moves:
            temp_game = game_state.get_state_copy()
            temp_game.make_move(move_pos) # Make the hypothetical move

            value = self.minimax(temp_game, self.max_depth - 1, False, self.player_id)
            
            print(f"  Move ({move_pos[0]},{move_pos[1]}) value {move_value}: Evaluated minimax value = {value:.2f}")

            if value > best_value:
                best_value = value
                best_move = move_pos
        
        return best_move

    def minimax(self, game_state, depth, is_maximizing_player, original_maximizing_player):
        if depth == 0 or game_state.is_game_over():
            return Heuristics.calculate(game_state, original_maximizing_player)

        available_moves = game_state.get_available_moves(game_state.last_chosen_pos)
        if not available_moves: # If no moves are left for the current player in this hypothetical state
             return Heuristics.calculate(game_state, original_maximizing_player)

        if is_maximizing_player: # This player wants to maximize their score (original_maximizing_player's turn in simulation)
            max_eval = -math.inf
            for move_pos, _ in available_moves:
                temp_game = game_state.get_state_copy()
                temp_game.make_move(move_pos)
                eval = self.minimax(temp_game, depth - 1, False, original_maximizing_player)
                max_eval = max(max_eval, eval)
            return max_eval
        else: # This player wants to minimize original_maximizing_player's score (opponent's turn in simulation)
            min_eval = math.inf
            for move_pos, _ in available_moves:
                temp_game = game_state.get_state_copy()
                temp_game.make_move(move_pos)
                eval = self.minimax(temp_game, depth - 1, True, original_maximizing_player)
                min_eval = min(min_eval, eval)
            return min_eval

# --- Game Simulation ---
if __name__ == "__main__":
    matrix = [
        [2, 9, 3],
        [5, 1, 7],
        [8, 4, 6]
    ]

    game = RCGame(matrix)
    
    ai_a = AIPlayer('A', depth=2) 
    ai_b = AIPlayer('B', depth=2)

    print("--- Starting Row-Column Game ---")
    game.print_board()

    turn = 0
    while not game.is_game_over():
        turn += 1
        print(f"\n===== Turn {turn} =====")
        print(f"Current Player: {game.current_player}")
        print(f"Scores: A={game.player_scores['A']}, B={game.player_scores['B']}")

        current_player_obj = ai_a if game.current_player == 'A' else ai_b
        
        # Determine if this is the very first move of the entire game
        is_first_move = (game.moves_made == 0)

        # Pass this flag to the AI player's get_best_move method
        move_pos = current_player_obj.get_best_move(game, is_first_move_of_game=is_first_move)

        if move_pos is None:
            print(f"Player {game.current_player} has no available moves. Game Over.")
            break

        chosen_value = game.make_move(move_pos)
        print(f"\nPlayer {game.current_player} chose {chosen_value} at ({move_pos[0]},{move_pos[1]})")
        game.print_board(highlight_pos=move_pos)
        print(f"Scores after move: A={game.player_scores['A']}, B={game.player_scores['B']}")

    print("\n--- Game Over ---")
    print(f"Final Scores: A={game.player_scores['A']}, B={game.player_scores['B']}")
    print(game.get_winner())