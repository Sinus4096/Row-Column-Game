import tkinter as tk

class Board:
    """ The Board class is responsible for creating and managing the Graphical User Interface (GUI)
        of the "RC GAME" using the tkinter library. It handles the visual layout, displays the
        game board grid, shows player scores, and captures user input.

        It establishes a direct connection with the GameHandler to:
        1. Retrieve game state information (like player names, scores, and the matrix values).
        2. Notify the GameHandler when a cell (button) is clicked.
        3. Update the visual elements based on game events, such as refreshing scores,
           highlighting the current player, and enabling/disabling buttons to enforce
           the game's move rules (limiting clicks to the same row or column as the last move).
        """

    def __init__(self, game_handler):
        # References
        # direct reference to GameHandler
        self.game_handler = game_handler
        self.root = game_handler.root

        # color palette
        self.COLOR_BG = "#F8C8DC"  # for board
        self.COLOR_BTN = "#FFF4F7"  # for buttons
        self.COLOR_TEXT = "#111111"  # for text
        self.ACCENT_P1 = "#E36BAE"  # player one
        self.ACCENT_P1_SOFT = "#F6C3DB"  # soft border p1
        self.ACCENT_P2 = "#B36DE3"  # player 2
        self.ACCENT_P2_SOFT = "#D9C3F6"  # soft border p2
        self.COLOR_CLICKED = "#D988B9"  # for clicked cells

        #  Setup window
        try:
            self.root.state("zoomed")  # Windows fullscreen
        except Exception:
            self.root.attributes("-fullscreen", True)


        self.root.config(bg=self.COLOR_BG)

        #  Title
        self.title_canvas = tk.Canvas(
            self.root, width=600, height=70, bg=self.COLOR_BG, highlightthickness=0
        )
        self.title_canvas.pack(pady=(8, 4))
        self._draw_outlined_title(self.title_canvas, "RC GAME", y=35)

        #  Scores
        score_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        score_frame.pack(side=tk.TOP, fill=tk.X, pady=6)


        # wrapper with colorful frame
        self.p1_wrap = tk.Frame(score_frame, bg=self.ACCENT_P1_SOFT)
        self.p1_wrap.pack(side=tk.LEFT, padx=20)

        self.player1_label = tk.Label(
            self.p1_wrap,
            text=f"{self.game_handler.players[0].getName()}: 0",
            font=("Helvetica", 14, "bold"),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT,
            width=16,
            padx=10, pady=4
        )
        self.player1_label.pack()

        # colorful wrapper for P2
        self.p2_wrap = tk.Frame(score_frame, bg=self.ACCENT_P2_SOFT)
        self.p2_wrap.pack(side=tk.RIGHT, padx=20)

        self.player2_label = tk.Label(
            self.p2_wrap,
            text=f"{self.game_handler.players[1].getName()}: 0",
            font=("Helvetica", 14, "bold"),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT,
            width=16,
            padx=10, pady=4
        )
        self.player2_label.pack()


        # Grid
        self.grid_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        self.grid_frame.pack(expand=True)

        self.grid_buttons = []
        self.create_grid(self.game_handler.dimMat)

        # Highlights the first player
        self.highlight_current_player(self.game_handler.current_player)

    def _draw_outlined_title(self, canvas, text, y=35):
        # border
        shadow_color = "#C75A9B"  # shadow
        main_color = "#FFFFFF"  # white
        font = ("Helvetica", 28, "bold")

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            canvas.create_text(300 + dx, y + dy, text=text, fill=shadow_color, font=font)
        canvas.create_text(300, y, text=text, fill=main_color, font=font)


    #  Grid creation
    def create_grid(self, size):
        #  dynamic sizing so big boards still fit on screen
        if size <= 5:
            btn_w, btn_h, fsize, pad = 8, 3, 16, 3
        elif size <= 8:
            btn_w, btn_h, fsize, pad = 6, 2, 14, 2
        else:  # for 9x9 or 10x10 boards
            btn_w, btn_h, fsize, pad = 4, 2, 12, 1

        for r in range(size):
            row_buttons = []
            for c in range(size):
                btn = tk.Button(
                    self.grid_frame,
                    text=f"{self.game_handler.matrix[r][c]}",
                    width=btn_w,
                    height=btn_h,
                    bg=self.COLOR_BTN,
                    fg=self.COLOR_TEXT,
                    activebackground=self.COLOR_BTN,
                    activeforeground=self.COLOR_TEXT,
                    relief="flat",
                    bd=1,
                    highlightthickness=0,
                    font=("Helvetica", fsize, "bold"),
                    command=lambda row=r, col=c: self.cell_clicked(row, col)
                )
                btn.grid(row=r, column=c, padx=pad, pady=pad)
                row_buttons.append(btn)
            self.grid_buttons.append(row_buttons)

    # === When it is clicked ===
    def cell_clicked(self, row, col):
        # Notify the GameHandler first (it will update game state and swap turns)
        self.game_handler.handle_cell_click(row, col)

        # Then refresh UI to reflect the new current player and scores
        self.root.after(0, lambda: self.highlight_current_player(self.game_handler.current_player))
        self.root.after(0, self.update_scores)


    # === Score update ===
    def update_scores(self):
        s1, s2 = self.game_handler.score
        self.player1_label.config(text=f"{self.game_handler.players[0].getName()}: {s1}")
        self.player2_label.config(text=f"{self.game_handler.players[1].getName()}: {s2}")

    # === Highlight the current player ===
    def highlight_current_player(self, current: int):
        """
        Visually highlight the active player using the strong accent color and bold label,
        and render the inactive player with the soft accent.
        """
        def _apply(active_wrap, active_label, active_color,
                   inactive_wrap, inactive_label, inactive_soft):
            # Active: strong accent + subtle outline; label "lifts" on COLOR_BTN and is bold
            active_wrap.config(bg=active_color, highlightbackground=active_color, highlightthickness=2, bd=0)
            active_label.config(bg=self.COLOR_BTN, fg=self.COLOR_TEXT, font=("Helvetica", 14, "bold"))

            # Inactive: soft accent; label returns to background and normal weight
            inactive_wrap.config(bg=inactive_soft, highlightthickness=0, bd=0)
            inactive_label.config(bg=self.COLOR_BG, fg=self.COLOR_TEXT, font=("Helvetica", 14, "normal"))

        if current == 0:
            _apply(self.p1_wrap, self.player1_label, self.ACCENT_P1,
                   self.p2_wrap, self.player2_label, self.ACCENT_P2_SOFT)
        else:
            _apply(self.p2_wrap, self.player2_label, self.ACCENT_P2,
                   self.p1_wrap, self.player1_label, self.ACCENT_P1_SOFT)


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

                # if the cell is already clicked, keep it disabled
                if self.game_handler.matrix[r][c] == "-":
                    button.config(state="disabled", bg=self.COLOR_CLICKED)

                # if it's in the same row or column, keep it active
                elif r == active_row or c == active_col:
                    button.config(state="normal")
                # otherwise, disable it
                else:
                    button.config(state="disabled")

    def disable_all_buttons(self):
        for r in range(self.game_handler.dimMat):
            for c in range(self.game_handler.dimMat):
                button = self.grid_buttons[r][c]
                button.config(state="disabled")
