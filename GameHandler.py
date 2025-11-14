import time

import Board
import Player
import tkinter as tk
import fileReading
import random as rd
import RandomStrategy
import GreedyStrategy


class GameHandler:
    def __init__(self,player1, player2, root=None):
        self.root = root if root is not None else tk.Tk()
        self.players = [player1, player2]   # 0 = P1, 1 = P2
        self.current_player = 0     # 0 = P1, 1 = P2
        self.score = [0,0]
        self.matrix = fileReading.load_board_until_ok()
        self.dimMat = len(self.matrix)
        self.last_move = None
        # Creating a Board and do a referral to this GameHandler
        self.board = Board.Board(self)

    def play(self):
        if  self.players[0].is_human==False:
            self.computer_turn()
        self.board.set_visible()
        print("the game has started")



        #if(not self.players[self.current_player].is_human):
            #self.board.disable_all_buttons()
            #row,col=self.players[0].move(self.matrix)
            #self.handle_cell_click(row,col)

    def computer_turn(self):
        self.board.disable_all_buttons()
        player = self.players[self.current_player]
        move_result = player.move(self.matrix, self.last_move, self.score)
        if move_result is None:
            print("Game Over: No moves left for computer.") 
            return
        row, col = move_result
        self.handle_cell_click(row, col)

    # Calling from Board when a player clicks on a cel
    def handle_cell_click(self, row, col):
        print(f"[DEBUG] Player {self.current_player+1} has clicked on the cell ({row}, {col})")

        # --- (not mandatory) Updating score or turn ---
        self.score[self.current_player] += self.matrix[row][col]
        self.board.update_scores()

        # --- Updating the matrix ---
        self.matrix[row][col] = "-"  # sets the cell as clicked

        # --- Updating the button on the Board ---
        button = self.board.grid_buttons[row][col]
        button.config(text="-", state="disabled", bg="#555")  # show the sign and disable

        self.last_move = (row, col)

        # --- Player switch ---
        self.current_player = 1 if self.current_player == 0 else 0
        self.board.highlight_current_player(self.current_player)

        self.board.update_active_buttons(row, col)
        
        if(not self.players[self.current_player].is_human):
            # self.players[self.current_player-1].move(self.matrix,[row,col])
            self.root.after(1000, self.computer_turn)