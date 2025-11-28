import time
import tkinter as tk
from tkinter import messagebox
from Game import Board, fileReading


class GameHandler:
    """ The GameHandler class is the central control unit for the "RC GAME," a two-player,
        turn-based board game. It manages the game's state, enforces the rules, and coordinates
        the interaction between the game logic and the graphical user interface (GUI) provided
        by the `Board` class.

        Responsibilities include:
        1. Initializing the game board (matrix) by reading data from a file.
        2. Tracking and updating the scores for the two players (human or computer).
        3. Handling both human clicks and computer moves.
        4. Switching turns and enabling/disabling the correct buttons based on the last move
            (limiting moves to the same row or column).
        5. Detecting the end of the game and announcing the winner.
        """

    def __init__(self, player1, player2, root=None):
        self.root = root if root is not None else tk.Tk()
        self.players = [player1, player2] # 0 = P1, 1 = P2
        self.current_player = 0 # 0 = P1, 1 = P2
        self.score = [0, 0]
        self.matrix = fileReading.load_board_until_ok()
        self.dimMat = len(self.matrix)
        self.last_move = None

        # create Board and link this handler
        self.board = Board.Board(self)

    def play(self):
        # If P1 is a computer, let it start
        if not self.players[0].is_human:
            self.computer_turn()

        self.board.set_visible()
        print("the game has started")

    #helpers for ending the game
    def has_any_legal_moves(self) -> bool:
        """
        Returns True if at least one button is currently clickable (state='normal').
        Assumes Board.update_active_buttons(...) has set button states correctly.
        """
        for row_btns in self.board.grid_buttons:
            for btn in row_btns:
                if str(btn['state']) == 'normal':
                    return True
        return False

    def end_game_and_announce(self):
        """Disable the board and pop up a winner dialog with player names."""
        self.board.disable_all_buttons()

        # Use chosen names instead of generic "Player 1/2"
        name1 = self.players[0].getName()
        name2 = self.players[1].getName()
        p1, p2 = self.score

        if p1 > p2:
            winner_name = name1
        elif p2 > p1:
            winner_name = name2
        else:
            winner_name = None  # tie

        if winner_name:
            message = f"🎉 {winner_name} wins!\n\nScores:\n{name1}: {p1}\n{name2}: {p2}"
        else:
            message = f"🤝 It's a tie!\n\nScores:\n{name1}: {p1}\n{name2}: {p2}"

        messagebox.showinfo("Game Over", message)


    # Computer turn
    def computer_turn(self):
        player = self.players[self.current_player]
        move_result = player.move(self.matrix, self.last_move, self.score)
        if move_result is None:
            # No legal moves for this player means game over
            self.end_game_and_announce()
            return
        row, col = move_result
        self.handle_cell_click(row, col)

    #Handle a click from the board (human or AI)
    def handle_cell_click(self, row, col):
        print(f"[DEBUG] Player {self.current_player+1} clicked ({row}, {col})")

        # update score for the current player
        self.score[self.current_player] += self.matrix[row][col]
        self.board.update_scores()

        # update matrix (mark cell as taken)
        self.matrix[row][col] = "-"

        #update the button on the board
        button = self.board.grid_buttons[row][col]
        button.config(text="-", state="disabled", bg=self.board.COLOR_CLICKED)

        self.last_move = (row, col)

        # Switch player
        self.current_player = 1 if self.current_player == 0 else 0
        self.board.highlight_current_player(self.current_player)

        #enable legal buttons for the NEXT player based on the last move
        self.board.update_active_buttons(row, col)

        # If the next player has no legal moves, end now
        if not self.has_any_legal_moves():
            # Small delay so UI shows the last click before the dialog
            self.root.after(100, self.end_game_and_announce)
            return

        # If the next player is a computer, schedule its move
        if not self.players[self.current_player].is_human:
            self.board.disable_all_buttons()
            self.root.after(1000, self.computer_turn)

