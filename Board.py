import tkinter as tk

class Board:
    def __init__(self, game_handler):
        # === References ===
        # direct reference to GameHandler
        self.game_handler = game_handler

        self.root = game_handler.root


        # === Setup window ===
        self.root.geometry("600x600")
        self.root.config(bg="#222")

        # === Title ===
        title = tk.Label(
            self.root,
            text="RC GAME",
            font=("Helvetica", 20, "bold"),
            fg="white",
            bg="#222"
        )
        title.pack(pady=10)

        # === Scores ===
        score_frame = tk.Frame(self.root, bg="#222")
        score_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.player1_label = tk.Label(
            score_frame,
            text=f"{self.game_handler.players[0].getName()}: 0",
            font=("Helvetica", 14),
            bg="#444",
            fg="white",
            width=15
        )
        self.player1_label.pack(side=tk.LEFT, padx=20)

        self.player2_label = tk.Label(
            score_frame,
            text=f"{self.game_handler.players[1].getName()}: 0",
            font=("Helvetica", 14),
            bg="#444",
            fg="white",
            width=15
        )
        self.player2_label.pack(side=tk.RIGHT, padx=20)

        # === Grid ===
        self.grid_frame = tk.Frame(self.root, bg="#222")
        self.grid_frame.pack(expand=True)

        self.grid_buttons = []
        self.create_grid(self.game_handler.dimMat)

        # Highlights the first player
        self.highlight_current_player(self.game_handler.current_player)

    # === Grid creation ===
    def create_grid(self, size):
        for r in range(size):
            row_buttons = []
            for c in range(size):
                btn = tk.Button(
 self.grid_frame,
    text=f"{self.game_handler.matrix[r][c]}",
    width=8,
    height=3,
    bg="#ddd",         # light gray background
    fg="black",        # black numbers
    font=("Helvetica", 16, "bold"),  # makes numbers stand out more
    command=lambda row=r, col=c: self.cell_clicked(row, col)
)

                btn.grid(row=r, column=c, padx=5, pady=5)
                row_buttons.append(btn)
            self.grid_buttons.append(row_buttons)

    # === When it is clicked ===
    def cell_clicked(self, row, col):
        # Notifies the GameHandler that a cell has been clicked
        self.game_handler.handle_cell_click(row, col)

    # === Score update ===
    def update_scores(self):
        s1, s2 = self.game_handler.score
        self.player1_label.config(text=f"{self.game_handler.players[0].getName()}: {s1}")
        self.player2_label.config(text=f"{self.game_handler.players[1].getName()}: {s2}")

    # === Highlight the current player ===
    def highlight_current_player(self, current):
        if current == 0:
            self.player1_label.config(bg="#666")
            self.player2_label.config(bg="#444")
        else:
            self.player1_label.config(bg="#444")
            self.player2_label.config(bg="#666")

    # === Starting the window ===
    def set_visible(self):
        self.root.mainloop()

    def update_active_buttons(self, active_row, active_col):
        """
        Turns off all buttons except for those in the same row or column
        of the clicked cell (if not disabled or marked.
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

    def disable_all_buttons(self):
        for r in range(self.game_handler.dimMat):
            for c in range(self.game_handler.dimMat):
                button = self.grid_buttons[r][c]
                button.config(state="disabled")
