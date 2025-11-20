import tkinter as tk
import os
import random

from Game import Player
from Game.GameHandler import GameHandler

from Strategies.Strategy import Strategy
from Strategies.RandomStrategy import RandomStrategy
from Strategies.safe_choice_strategy import SafeChoiceStrategy
from Strategies.GreedyStrategy import GreedyStrategy
from Strategies.MCTS import MCTSStrategy
from Strategies.minimax_f import AlphaBetaStrategy

CONSTANT_SEED = 12345

class GameSetup:
    """
        GUI setup wizard for RC GAME (visual restyle: candy/pastel palette).
        Logic unchanged; only styling and a small title helper added.
    """

    def __init__(self):
        self.root = tk.Tk()  # own set-up window
        self.root.title("Game Start")
        #Open fullscreen on any OS
        try:
            self.root.state("zoomed")  # Windows
        except Exception:
            self.root.attributes("-fullscreen", True)  # macOS/Linux fallback

        # palette
        self.COLOR_BG = "#F8C8DC"        # for background
        self.COLOR_BTN = "#FFF4F7"       # for buttons / inputs
        self.COLOR_TEXT = "#111111"      # for  text
        self.ACCENT = "#E36BAE"          # primary accent
        self.ACCENT_SOFT = "#F6C3DB"     # for outlines
        self.ACCENT_ALT = "#B36DE3"      # secondary accent

        # apply window background
        self.root.config(bg=self.COLOR_BG)

        # Hold optional strategy selections for p1/p2 (string names)
        self.p1_strategy_var = tk.StringVar(value="")  # empty means not selected yet
        self.p2_strategy_var = tk.StringVar(value="")

        # Variables for board size, reproducibility and board file
        self.board_size_var = tk.StringVar(value="5")
        self.reproducible_var = tk.BooleanVar(value=False)
        self.repro_checkbox = None
        self.board_file = None
        self.btn_manual = None

        # Frames that will host strategy buttons (created later)
        self.p1_strategy_frame = None
        self.p2_strategy_frame = None

        self.show_start_page()
        self.p1 = None
        self.p2 = None

    def _draw_outlined_title(self, parent, text, height=60, y=30):
        # create a canvas that stretches with the window
        canvas = tk.Canvas(parent, height=height, bg=self.COLOR_BG, highlightthickness=0)
        canvas.pack(fill="x", pady=(8, 6))

        def draw():
            canvas.delete("all")
            width = canvas.winfo_width() or parent.winfo_width() or 420
            shadow_color = "#C75A9B"
            main_color = "#FFFFFF"
            font = ("Helvetica", 22, "bold")
            cx = width // 2
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                canvas.create_text(cx + dx, y + dy, text=text, fill=shadow_color, font=font)
            canvas.create_text(cx, y, text=text, fill=main_color, font=font)

        # draw now and whenever the window resizes
        canvas.bind("<Configure>", lambda e: draw())
        parent.after(0, draw)
        return canvas
    
    def run(self):
        self.root.mainloop()
        return [self.p1, self.p2]

    # start page
    def show_start_page(self):
        self.clear_window()

        # Title (canvas with outlined text)
        self._draw_outlined_title(self.root, "Welcome to the Row-Column Game!")

        # START button (style)
        # Center a frame vertically and horizontally for buttons
        button_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        button_frame.pack(expand=True)

        # START button
        tk.Button(
            button_frame, text="START",
            width=20, height=3,
            font=("Helvetica", 14, "bold"),
            command=self.show_setup_page,
            bg=self.COLOR_BTN, fg="#E36BAE",
            activebackground=self.COLOR_BTN, activeforeground=self.COLOR_TEXT,
            relief="flat", bd=1, highlightthickness=0
        ).pack(pady=15)

        # Instructions button (larger and centered)
        tk.Button(
            button_frame, text="Instructions",
            width=20, height=3,
            font=("Helvetica", 14, "bold"),
            command=self.show_instructions,
            bg=self.COLOR_BTN, fg=self.COLOR_TEXT,
            activebackground=self.COLOR_BTN, activeforeground=self.COLOR_TEXT,
            relief="flat", bd=1, highlightthickness=0
        ).pack(pady=10)

    # switches to instruction page
    def show_instructions(self):
        self.clear_window()
        # Responsive title
        self._draw_outlined_title(self.root, "Row-Column Game Instructions")

        # Centered "card"
        card = tk.LabelFrame(
            self.root, bg=self.COLOR_BG, fg=self.COLOR_TEXT,
            text="", highlightthickness=2, labelanchor="n"
        )
        card.configure(highlightbackground=self.ACCENT_SOFT, highlightcolor=self.ACCENT_SOFT, highlightthickness=2)
        card.pack(padx=24, pady=8, fill="both", expand=True)

        # Inner area with padding
        body = tk.Frame(card, bg=self.COLOR_BG)
        body.pack(padx=16, pady=16, fill="both", expand=True)

        # Scrollable text (read-only), word-wrapped to a comfortable width
        import tkinter.scrolledtext as st
        instructions_text = (
            "Welcome to the Row-Column Game!\n\n"
            "Get ready to test your logic, prediction, and a bit of luck! The goal is simple: collect "
            "the highest score while moving through a grid of numbers, but the twist is that each move "
            "changes what you can play next.\n\n"
            "Rules:\n"
            "The game board is a square grid filled with numbers. Two players take turns clicking one of "
            "the cells to claim it, and the value in that cell is added to their score. Once a cell has "
            "been clicked, it becomes unavailable. The crucial twist lies in the movement rule: on your "
            "next turn, you can only choose a cell that is in the same row or the same column as the cell "
            "your opponent just chose. The game continues until there are no valid moves left. Once the "
            "game has ended, the player with the highest total score is the winner.\n\n"
            "Instructions:\n"
            "Before starting the game, you'll need to configure the following settings:\n\n"
            "1. Player Names: Enter the names for Player 1 and Player 2.\n"
            "2. Player Type: For each player, select whether they are a Human or a Computer.\n"
            "3. Computer Strategy: If a player is set to Computer, choose their AI strategy from: Random, "
            "Greedy, Safe Choice, or Monte Carlo Tree Search.\n"
            "4. Board Size: Select the size of the grid.\n"
            "5. Reproducibility (Optional): Turning on Reproducibility means the numbers in the game board "
            "will be generated using a fixed random seed. If you enable it and keep the same board size across "
            "multiple games, you'll get the same layout every time, making it perfect for practicing strategies! "
            "If left off, a completely random board will be created for each new game.\n\n"
            "You’re all set to begin your match! Best of luck, and most importantly, have fun!"
        )

        txt = st.ScrolledText(
            body, wrap="word", height=18,
            bg=self.COLOR_BG, fg=self.COLOR_TEXT,
            relief="flat", bd=0, font=("Helvetica", 14)
        )
        txt.pack(fill="both", expand=True)

        # Use the Text widget's tag system for formatting
        txt.insert("1.0", instructions_text)

        # --- Formatting tags ---
        bright_pink = "#E36BAE"

        txt.tag_add("welcome", "1.0", "1.end")
        txt.tag_config("welcome", foreground=bright_pink, font=("Helvetica", 18, "bold"))

        # further fine-tuning to make the instructions clearer
        rules_index = txt.search("Rules:", "1.0", tk.END)
        if rules_index:
            txt.tag_add("rules", rules_index, f"{rules_index} lineend")
            txt.tag_config("rules", foreground=bright_pink, font=("Helvetica", 16, "bold"))

        instructions_index = txt.search("Instructions:", "1.0", tk.END)
        if instructions_index:
            txt.tag_add("instructions", instructions_index, f"{instructions_index} lineend")
            txt.tag_config("instructions", foreground=bright_pink, font=("Helvetica", 16, "bold"))


        end_index = txt.search("Best of luck", "1.0", tk.END)
        if end_index:
            txt.tag_add("ending", end_index, f"{end_index} lineend")
            txt.tag_config("ending", foreground=bright_pink, font=("Helvetica", 14, "bold"))

        txt.config(state="disabled")  # read-only

        # Footer
        tk.Button(
            self.root, text="Go back to start page",
            command=self.show_start_page,
            bg=self.COLOR_BTN, fg=self.COLOR_TEXT,
            activebackground=self.COLOR_BTN, activeforeground=self.COLOR_TEXT,
            relief="flat", bd=1, highlightthickness=0,
            width=20, height=2, font=("Helvetica", 11, "bold")
        ).pack(pady=10)

    # switches to setup page
    def show_setup_page(self):
        self.clear_window()

        # Title (canvas)
        self._draw_outlined_title(self.root, "Row-Column Game Setup")

        # Container (Player 1 vs. Player 2)
        container = tk.Frame(self.root, bg=self.COLOR_BG)
        container.pack(fill="x", padx=20, pady=(0, 8))  # <- no expand=True
        container.grid_columnconfigure(0, weight=1, minsize=180)
        container.grid_columnconfigure(1, weight=0, minsize=60)
        container.grid_columnconfigure(2, weight=1, minsize=180)

        # Editable names (defaults)
        self.p1_name_var = tk.StringVar(value="Player 1")
        self.p2_name_var = tk.StringVar(value="Player 2")

        # Entry Player 1
        tk.Entry(
            container, textvariable=self.p1_name_var, font=("Arial", 16),
            fg=self.COLOR_TEXT, bg=self.COLOR_BTN, insertbackground=self.COLOR_TEXT,
            justify="center", width=14, relief="flat", bd=1, highlightthickness=1,
            highlightbackground=self.ACCENT_SOFT
        ).grid(row=0, column=0, pady=(10, 6))

        # "VS."
        tk.Label(
            container, text="VS.", font=("Arial", 16, "bold"),
            fg=self.COLOR_TEXT, bg=self.COLOR_BG
        ).grid(row=0, column=1, pady=(10, 6))

        # Entry Player 2
        tk.Entry(
            container, textvariable=self.p2_name_var, font=("Arial", 16),
            fg=self.COLOR_TEXT, bg=self.COLOR_BTN, insertbackground=self.COLOR_TEXT,
            justify="center", width=14, relief="flat", bd=1, highlightthickness=1,
            highlightbackground=self.ACCENT_SOFT
        ).grid(row=0, column=2, pady=(10, 6))

        # Player 1 choice buttons
        self.p1_human = tk.Button(
            container, text="Human", width=12,
            command=lambda: self.select_player("p1", "human"),
            bg=self.COLOR_BTN, fg=self.COLOR_TEXT,
            activebackground=self.COLOR_BTN, activeforeground=self.COLOR_TEXT,
            relief="flat", bd=1, highlightthickness=0
        )
        self.p1_human.grid(row=1, column=0, pady=5)

        self.p1_computer = tk.Button(
            container, text="Computer", width=12,
            command=lambda: self.select_player("p1", "computer"),
            bg=self.COLOR_BTN, fg=self.COLOR_TEXT,
            activebackground=self.COLOR_BTN, activeforeground=self.COLOR_TEXT,
            relief="flat", bd=1, highlightthickness=0
        )
        self.p1_computer.grid(row=2, column=0, pady=5)

        # Placeholder for P1 strategies
        self.p1_strategy_frame = tk.Frame(container, bg=self.COLOR_BG)
        self.p1_strategy_frame.grid(row=3, column=0, pady=(0, 10))

        # Player 2 choice buttons
        self.p2_human = tk.Button(
            container, text="Human", width=12,
            command=lambda: self.select_player("p2", "human"),
            bg=self.COLOR_BTN, fg=self.COLOR_TEXT,
            activebackground=self.COLOR_BTN, activeforeground=self.COLOR_TEXT,
            relief="flat", bd=1, highlightthickness=0
        )
        self.p2_human.grid(row=1, column=2, pady=5)

        self.p2_computer = tk.Button(
            container, text="Computer", width=12,
            command=lambda: self.select_player("p2", "computer"),
            bg=self.COLOR_BTN, fg=self.COLOR_TEXT,
            activebackground=self.COLOR_BTN, activeforeground=self.COLOR_TEXT,
            relief="flat", bd=1, highlightthickness=0
        )
        self.p2_computer.grid(row=2, column=2, pady=5)

        # Placeholder for P2 strategies
        self.p2_strategy_frame = tk.Frame(container, bg=self.COLOR_BG)
        self.p2_strategy_frame.grid(row=3, column=2, pady=(0, 10))

        # Board Setup "card"
        board_frame = tk.LabelFrame(
            self.root, text="Board Setup", fg=self.COLOR_TEXT, bg=self.COLOR_BG,
            font=("Arial", 13, "bold"), labelanchor="n"
        )
        board_frame.configure(highlightbackground=self.ACCENT_SOFT, highlightcolor=self.ACCENT_SOFT,
                              highlightthickness=2)
        board_frame.pack(fill="x", padx=40, pady=(6, 12))  # <- wider + centered

        inner = tk.Frame(board_frame, bg=self.COLOR_BG)
        inner.pack(padx=16, pady=16, fill="x")  # <- more breathing room

        tk.Label(
            inner, text="Pick the board size (2–10):",
            fg=self.COLOR_TEXT, bg=self.COLOR_BG, font=("Arial", 11)
        ).grid(row=0, column=0, sticky="e", pady=4, padx=6)

        tk.Spinbox(
            inner, from_=2, to=10, textvariable=self.board_size_var, width=4,
            justify="center", fg=self.COLOR_TEXT
        ).grid(row=0, column=1, sticky="w", pady=4)

        self.repro_checkbox = tk.Checkbutton(
            inner, text="Reproducibility (fixed seed)", variable=self.reproducible_var,
            bg=self.COLOR_BG, fg=self.COLOR_TEXT,
            activebackground=self.COLOR_BG, activeforeground=self.COLOR_TEXT,
            selectcolor=self.COLOR_BTN
        )
        self.repro_checkbox.grid(row=0, column=2, columnspan=2, sticky="w", padx=16)

        # Buttons row
        btns = tk.Frame(inner, bg=self.COLOR_BG)
        btns.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(12, 0))
        btns.grid_columnconfigure(0, weight=0)
        btns.grid_columnconfigure(1, weight=1)
        btns.grid_columnconfigure(2, weight=0)

        tk.Button(
            btns, text="Create board with chosen size",
            command=lambda: self.generate_board(),
            bg=self.COLOR_BTN, fg=self.COLOR_TEXT,
            activebackground=self.COLOR_BTN, activeforeground=self.COLOR_TEXT,
            relief="flat", bd=1, highlightthickness=0
        ).grid(row=0, column=0, sticky="w", padx=6)

        # footer buttons
        footer = tk.Frame(self.root, bg=self.COLOR_BG)
        footer.pack(pady=(6, 12))

        tk.Button(
            footer, text="Go back to start page", command=self.show_start_page,
            bg=self.COLOR_BTN, fg=self.COLOR_TEXT,
            activebackground=self.COLOR_BTN, activeforeground=self.COLOR_TEXT,
            relief="flat", bd=1, highlightthickness=0,
            width=20, height=2, font=("Helvetica", 11, "bold")
        ).pack(side="left", padx=10)

        self.start_button = tk.Button(
            footer, text="Start Game", command=self.finish_setup, state="disabled",
            bg=self.COLOR_BTN, fg="#E36BAE",
            activebackground=self.COLOR_BTN, activeforeground=self.COLOR_TEXT,
            relief="flat", bd=1, highlightthickness=0,
            width=20, height=2, font=("Helvetica", 11, "bold")
        )
        self.start_button.pack(side="left", padx=10)

        # Re-check whenever strategy selection changes
        self.p1_strategy_var.trace_add("write", lambda *_: self.update_start_button())
        self.p2_strategy_var.trace_add("write", lambda *_: self.update_start_button())

    # Creates strategy radio buttons dynamically when Computer is chosen
    def show_strategy_options(self, which_player: str):
        """
        Create or refresh strategy radio buttons for the given player (p1/p2).
        The chosen value is stored into p1_strategy_var / p2_strategy_var.
        """
        frame = self.p1_strategy_frame if which_player == "p1" else self.p2_strategy_frame
        var = self.p1_strategy_var if which_player == "p1" else self.p2_strategy_var

        # Clear the frame before adding fresh widgets
        for w in frame.winfo_children():
            w.destroy()

        # Label
        tk.Label(
            frame, text="Select strategy:", fg=self.COLOR_TEXT, bg=self.COLOR_BG, font=("Arial", 10, "bold")
        ).pack(pady=(2, 2))

        # RadioButtons
        rb_values = [
            ("Random Strategy", "random"),
            ("Safe Choice Strategy", "safe_choice"),
            ("Greedy Strategy", "greedy"),
            ("Monte Carlo Tree Search Strategy", "MCTS"),  
            ("Minimax", "minimax"),
        ]
        for text, value in rb_values:
            tk.Radiobutton(
                frame, text=text, variable=var, value=value,
                bg=self.COLOR_BG, fg=self.COLOR_TEXT,
                selectcolor=self.COLOR_BTN,
                activebackground=self.COLOR_BG, activeforeground=self.COLOR_TEXT,
                command=self.update_start_button
            ).pack(anchor="w")

    # DOES NOT store player objects. Disables the opposite button and shows/hides strategy options.
    def select_player(self, player, choice):
        if player == "p1":
            self.p1_type = choice
            if choice == "human":
                self.p1_computer.config(state="disabled")
                self.p1_human.config(relief="sunken")
                self.p1_strategy_var.set("")
                for w in self.p1_strategy_frame.winfo_children():
                    w.destroy()
            else:
                self.p1_human.config(state="disabled")
                self.p1_computer.config(relief="sunken")
                self.show_strategy_options("p1")
        else:  # p2
            if choice == "human":
                self.p2_computer.config(state="disabled")
                self.p2_human.config(relief="sunken")
                self.p2_strategy_var.set("")
                for w in self.p2_strategy_frame.winfo_children():
                    w.destroy()
            else:
                self.p2_human.config(state="disabled")
                self.p2_computer.config(relief="sunken")
                self.show_strategy_options("p2")

        self.update_start_button()

    def update_start_button(self):
        """
        Start is enabled only if:
          - P1 has chosen (one of its buttons is disabled),
          - P2 has chosen,
          - For every player marked as 'Computer', a strategy has been selected.
          - The board file has been configured
        """
        p1_chosen = (self.p1_human["state"] == "disabled") or (self.p1_computer["state"] == "disabled")
        p2_chosen = (self.p2_human["state"] == "disabled") or (self.p2_computer["state"] == "disabled")

        # If Computer is chosen, require a non-empty strategy string
        p1_ok = p1_chosen and (
                (self.p1_human["state"] == "disabled") or  # chose Computer
                (self.p1_computer["state"] == "disabled" and self.p1_strategy_var.get() == "") is False
        )
        # Equivalent explicit logic:
        if self.p1_computer["state"] == "disabled" and self.p1_human["state"] == "normal":
            p1_ok = True
        elif self.p1_human["state"] == "disabled" and self.p1_computer["state"] == "normal":
            p1_ok = bool(self.p1_strategy_var.get())

        if self.p2_computer["state"] == "disabled" and self.p2_human["state"] == "normal":
            p2_ok = True
        elif self.p2_human["state"] == "disabled" and self.p2_computer["state"] == "normal":
            p2_ok = bool(self.p2_strategy_var.get())
        else:
            p2_ok = False

        ready_board = bool(self.board_file)

        self.start_button.config(state="normal" if (p1_chosen and p2_chosen and p1_ok and p2_ok and ready_board) else "disabled")

    def create_players(self):
        """
        Build Player objects only here, just before starting the game.
        As requested, pass the strategy NAME string as the third argument when a player is a computer.
        """
        name1 = (self.p1_name_var.get() or "Player 1").strip() or "Player 1"
        name2 = (self.p2_name_var.get() or "Player 2").strip() or "Player 2"

        if self.p1_computer["state"] == "disabled" and self.p1_human["state"] == "normal":
            p1 = Player.Player(name=name1, is_human=True)
        else:
            p1_strategy_name = self.p1_strategy_var.get()
            strategy1 = self.create_strategy(p1_strategy_name)
            p1 = Player.Player(name=name1, is_human=False, strategy=strategy1)

        if self.p2_computer["state"] == "disabled" and self.p2_human["state"] == "normal":
            p2 = Player.Player(name=name2, is_human=True)
        else:
            p2_strategy_name = self.p2_strategy_var.get()
            strategy2 = self.create_strategy(p2_strategy_name)
            p2 = Player.Player(name=name2, is_human=False, strategy=strategy2)

        return p1, p2

    def finish_setup(self):
        self.p1, self.p2 = self.create_players()
        self.root.destroy()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_strategy(self, strategy_name):
        match strategy_name:
            case "random":
                return RandomStrategy()
            case "safe_choice":
                return SafeChoiceStrategy()
            case "greedy":
                return GreedyStrategy()
            case "MCTS":
                return MCTSStrategy()
            case "minimax":
                return AlphaBetaStrategy()
            case _:
                raise ValueError(f"Unknown strategy: {strategy_name}")

    # Generates a quadratic Board according to the board size input
    def generate_board(self):
        try:
            size = int(self.board_size_var.get())
        except ValueError:
            self.board_file = None
            self.update_start_button()
            return

        if self.repro_checkbox:
            self.repro_checkbox.config(state="normal")

        rnd = random.Random(CONSTANT_SEED) if self.reproducible_var.get() else random.Random()

        matrix = [[rnd.randint(1,9) for _ in range(size)] for _ in range(size)]
        out_dir = "boards"
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "board.txt")

        with open(path, "w", encoding="utf-8") as file:
            for row in matrix:
                file.write(" ".join(map(str, row)) + "\n")

        if self.repro_checkbox:
            self.repro_checkbox.config(state="disabled")

        self.board_file = path
        self.update_start_button()
      

        

    