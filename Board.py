import tkinter as tk

class Board:
    def __init__(self, game_handler):
        # === Riferimenti ===
        # collegamento diretto al GameHandler
        self.game_handler = game_handler

        self.root = game_handler.root


        # === Setup finestra ===
        self.root.geometry("600x600")
        self.root.config(bg="#222")

        # === Titolo ===
        title = tk.Label(
            self.root,
            text="RC GAME",
            font=("Helvetica", 20, "bold"),
            fg="white",
            bg="#222"
        )
        title.pack(pady=10)

        # === Punteggi ===
        score_frame = tk.Frame(self.root, bg="#222")
        score_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.player1_label = tk.Label(
            score_frame,
            text=f"{self.game_handler.player1.getName()}: 0",
            font=("Helvetica", 14),
            bg="#444",
            fg="white",
            width=15
        )
        self.player1_label.pack(side=tk.LEFT, padx=20)

        self.player2_label = tk.Label(
            score_frame,
            text=f"{self.game_handler.player2.getName()}: 0",
            font=("Helvetica", 14),
            bg="#444",
            fg="white",
            width=15
        )
        self.player2_label.pack(side=tk.RIGHT, padx=20)

        # === Griglia ===
        self.grid_frame = tk.Frame(self.root, bg="#222")
        self.grid_frame.pack(expand=True)

        self.grid_buttons = []
        self.create_grid(self.game_handler.dimMat)

        # Evidenzia chi gioca per primo
        self.highlight_current_player(self.game_handler.current_player)

    # === Creazione della griglia ===
    def create_grid(self, size):
        for r in range(size):
            row_buttons = []
            for c in range(size):
                btn = tk.Button(
                    self.grid_frame,
                    text=f"{self.game_handler.matrix[r][c]}",
                    width=8,
                    height=3,
                    bg="#333",
                    fg="white",
                    command=lambda row=r, col=c: self.cell_clicked(row, col)
                )
                btn.grid(row=r, column=c, padx=5, pady=5)
                row_buttons.append(btn)
            self.grid_buttons.append(row_buttons)

    # === Quando una cella viene cliccata ===
    def cell_clicked(self, row, col):
        # Notifica il GameHandler che una cella è stata cliccata
        self.game_handler.handle_cell_click(row, col)

    # === Aggiornamento punteggi ===
    def update_scores(self):
        s1, s2 = self.game_handler.score
        self.player1_label.config(text=f"{self.game_handler.player1.getName()}: {s1}")
        self.player2_label.config(text=f"{self.game_handler.player2.getName()}: {s2}")

    # === Evidenzia il giocatore attuale ===
    def highlight_current_player(self, current):
        if current == 1:
            self.player1_label.config(bg="#666")
            self.player2_label.config(bg="#444")
        else:
            self.player1_label.config(bg="#444")
            self.player2_label.config(bg="#666")

    # === Avvia la finestra ===
    def set_visible(self):
        self.root.mainloop()

    def update_active_buttons(self, active_row, active_col):
        """
        Disattiva tutti i bottoni tranne quelli nella stessa riga o colonna
        della cella cliccata (se non sono già disabilitati o marcati).
        """
        for r in range(self.game_handler.dimMat):
            for c in range(self.game_handler.dimMat):
                button = self.grid_buttons[r][c]

                # se la cella è già cliccata, resta disabilitata
                if self.game_handler.matrix[r][c] == "-":
                    button.config(state="disabled")
                # se è nella stessa riga o colonna, la lasciamo attiva
                elif r == active_row or c == active_col:
                    button.config(state="normal")
                # altrimenti la disattiviamo
                else:
                    button.config(state="disabled")
