import Board
import Player
import tkinter as tk


class GameHandler:
    def __init__(self,root=tk.Tk(),player1=Player.Player("Player 1",),player2=Player.Player("Player 2")):
        self.root = root
        self.player1 = player1
        self.player2 = player2
        self.current_player = 1
        self.score = [0,0]
        self.dimMat=4
        self.matrix=[
                     [1, 5, 7, 2],
                     [3, 6, 9, 8],
                     [4, 4, 2, 1],
                     [9, 6, 3, 6]
                    ]
        # Creiamo la Board e le passiamo un riferimento a questo GameHandler
        self.board = Board.Board(self)

    def play(self):
        self.board.set_visible()

    # Chiamato da Board quando un giocatore clicca su una cella
    def handle_cell_click(self, row, col):
        print(f"[DEBUG] Player {self.current_player} ha cliccato sulla cella ({row}, {col})")

        # --- (facoltativo) Aggiorna punteggio o turno ---
        if self.current_player == 1:
            self.score[0] += self.matrix[row][col]

        if self.current_player == 2:
            self.score[1] += self.matrix[row][col]

        self.board.update_scores()
        # --- Aggiorna la matrice logica ---
        self.matrix[row][col] = "-"  # segna la cella come cliccata

        # --- Aggiorna il bottone nella Board ---
        button = self.board.grid_buttons[row][col]
        button.config(text="-", state="disabled", bg="#555")  # mostra il segno e disattiva



        # --- Cambia giocatore ---
        self.current_player = 2 if self.current_player == 1 else 1
        self.board.highlight_current_player(self.current_player)

        self.board.update_active_buttons(row, col)
