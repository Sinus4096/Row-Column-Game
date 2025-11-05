import Board
import Player
import tkinter as tk
import fileReading
import random as rd
import RandomStrategy


class GameHandler:
    def __init__(self,root=tk.Tk(),player1=Player.Player("Player 1",),player2=Player.Player("Player 2")):
        self.root = root
        self.player[0] = player1
        self.player[1] = player2
        self.current_player = 1
        self.score = [0,0]
        self.matrix = fileReading.load_board_until_ok()
        self.dimMat = len(self.matrix)
        # Creating a Board and do a referral to this GameHandler
        self.board = Board.Board(self)

    def play(self):
        self.board.set_visible()
        if(self.player[0].is_human==False):
            self.board.disable_all_buttons()
            row,col=self.player[0].move(self.matrix)
            self.handle_cell_click(row,col)
            

    # Calling from Board when a player clicks on a cel
    def handle_cell_click(self, row, col):
        print(f"[DEBUG] Player {self.current_player} has clicked on the cell ({row}, {col})")

        # --- (not mandatory) Updating score or turn ---
        if self.current_player == 1:
            self.score[0] += self.matrix[row][col]

        if self.current_player == 2:
            self.score[1] += self.matrix[row][col]

        self.board.update_scores()
        # --- Updating the matrix ---
        self.matrix[row][col] = "-"  # sets the cell as clicked

        # --- Updating the button on the Board ---
        button = self.board.grid_buttons[row][col]
        button.config(text="-", state="disabled", bg="#555")  # show the sign and disable



        # --- Player switch ---
        self.current_player = 2 if self.current_player == 1 else 1
        self.board.highlight_current_player(self.current_player)

        self.board.update_active_buttons(row, col)
        
        if(self.player[self.current_player-1].is_human==False):
            self.player[self.current_player-1].move(self.matrix,[row,col])
