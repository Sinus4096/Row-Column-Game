import tkinter as tk
import Player
import Strategy
from GameHandler import GameHandler
from RandomStrategy import RandomStrategy
from safe_choice_strategy import SafeChoiceStrategy
from GreedyStrategy import GreedyStrategy


class GameSetup:
    def __init__(self):
        self.root = tk.Tk()  # own set-up window
        self.root.title("Game Start")
        self.root.geometry("420x320")
        self.root.config(bg="#222")

        # Hold optional strategy selections for p1/p2 (string names)
        self.p1_strategy_var = tk.StringVar(value="")  # empty means not selected yet
        self.p2_strategy_var = tk.StringVar(value="")

        # Frames that will host strategy buttons (created later)
        self.p1_strategy_frame = None
        self.p2_strategy_frame = None

        self.show_start_page()
        self.p1 = None
        self.p2 = None

    def run(self):
        self.root.mainloop()
        return [self.p1, self.p2]

    # start page
    def show_start_page(self):
        self.clear_window()

        # title
        tk.Label(self.root, text="Welcome to the Row-Column Game!",
                 font=("Helvetica", 20, "bold"), fg="white", bg="#222").pack(pady=40)

        # START button
        tk.Button(self.root, text="START", width=15, height=2, command=self.show_setup_page).pack(pady=10)

        # Instructions button
        tk.Button(self.root, text="Instructions", width=15, height=2, command=self.show_instructions).pack(pady=10)

    # switches to instruction page
    def show_instructions(self):
        self.clear_window()
        tk.Label(self.root, text="Row-Column Game Instructions", font=("Helvetica", 20, "bold")).pack(pady=20)
        tk.Button(self.root, text="Go back to start page", command=self.show_start_page).pack(pady=10)

    # switches to setup page
    def show_setup_page(self):
        self.clear_window()

        # Title
        title = tk.Label(self.root, text="Row-Column Game Setup", font=("Helvetica", 20, "bold"), bg="#222", fg="white")
        title.pack(pady=10)

        # Container (Player 1 vs. Player 2)
        container = tk.Frame(self.root, bg="#222")
        container.pack(expand=True, fill="both", padx=12)
        container.grid_columnconfigure(0, weight=1, minsize=180)
        container.grid_columnconfigure(1, weight=0, minsize=60)
        container.grid_columnconfigure(2, weight=1, minsize=180)

        # Editable names (defaults)
        self.p1_name_var = tk.StringVar(value="Player 1")
        self.p2_name_var = tk.StringVar(value="Player 2")

        # Entry Player 1
        tk.Entry(
            container, textvariable=self.p1_name_var, font=("Arial", 16),
            fg="white", bg="#333", insertbackground="white", justify="center", width=14
        ).grid(row=0, column=0, pady=(10, 6))

        # "VS."
        tk.Label(container, text="VS.", font=("Arial", 16, "bold"), fg="white", bg="#222").grid(row=0, column=1,
                                                                                                pady=(10, 6))

        # Entry Player 2
        tk.Entry(
            container, textvariable=self.p2_name_var, font=("Arial", 16),
            fg="white", bg="#333", insertbackground="white", justify="center", width=14
        ).grid(row=0, column=2, pady=(10, 6))

        # --- Player 1 choice buttons ---
        self.p1_human = tk.Button(container, text="Human", width=12,
                                  command=lambda: self.select_player("p1", "human"))
        self.p1_human.grid(row=1, column=0, pady=5)

        self.p1_computer = tk.Button(container, text="Computer", width=12,
                                     command=lambda: self.select_player("p1", "computer"))
        self.p1_computer.grid(row=2, column=0, pady=5)

        # Placeholder for P1 strategy buttons (created only if Computer is selected)
        self.p1_strategy_frame = tk.Frame(container, bg="#222")
        self.p1_strategy_frame.grid(row=3, column=0, pady=(0, 10))

        # --- Player 2 choice buttons ---
        self.p2_human = tk.Button(container, text="Human", width=12,
                                  command=lambda: self.select_player("p2", "human"))
        self.p2_human.grid(row=1, column=2, pady=5)

        self.p2_computer = tk.Button(container, text="Computer", width=12,
                                     command=lambda: self.select_player("p2", "computer"))
        self.p2_computer.grid(row=2, column=2, pady=5)

        # Placeholder for P2 strategy buttons
        self.p2_strategy_frame = tk.Frame(container, bg="#222")
        self.p2_strategy_frame.grid(row=3, column=2, pady=(0, 10))

        # Go back button
        tk.Button(self.root, text="Go back to start page", command=self.show_start_page).pack(pady=(4, 6))

        # Start the game button (disabled until all choices are valid)
        self.start_button = tk.Button(self.root, text="Start Game", command=self.finish_setup, state="disabled")
        self.start_button.pack(pady=(0, 10))

        # Re-check whenever a strategy selection changes (enables Start when valid)
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

        # Label to explain the requirement
        tk.Label(frame, text="Select strategy:", fg="white", bg="#222", font=("Arial", 10, "bold")).pack(pady=(2, 2))

        # RadioButtons: save the "name" of the strategy in the StringVar
        # Note: you asked to pass the strategy name to Player; we keep plain strings here.
        rb_values = [
            ("Random Strategy", "random"),
            ("Safe Choice Strategy", "safe_choice"),
            ("Greedy Strategy", "greedy"),
            #("Minimax", "minimax"), implement when the minmax strategy will be completed
        ]
        for text, value in rb_values:
            tk.Radiobutton(
                frame, text=text, variable=var, value=value,
                bg="#222", fg="white", selectcolor="#333", activebackground="#222", activeforeground="white",
                command=self.update_start_button  # Re-evaluate when a choice is made
            ).pack(anchor="w")

    # DOES NOT store player objects. Disables the opposite button and shows/hides strategy options.
    def select_player(self, player, choice):
        if player == "p1":
            if choice == "human":
                # Disable the opposite button; reset and hide any previous strategy selection for p1
                self.p1_computer.config(state="disabled")
                self.p1_human.config(relief="sunken")
                self.p1_strategy_var.set("")  # clear selection if switching from computer to human
                for w in self.p1_strategy_frame.winfo_children():
                    w.destroy()
            else:
                self.p1_human.config(state="disabled")
                self.p1_computer.config(relief="sunken")
                # Show strategy options for player 1
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
                # Show strategy options for player 2
                self.show_strategy_options("p2")

        # After any selection, update the Start button availability
        self.update_start_button()

    def update_start_button(self):
        """
        Start is enabled only if:
          - P1 has chosen (one of its buttons is disabled),
          - P2 has chosen,
          - For every player marked as 'Computer', a strategy has been selected.
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
            # human chosen -> OK regardless of strategy
            p1_ok = True
        elif self.p1_human["state"] == "disabled" and self.p1_computer["state"] == "normal":
            # computer chosen -> need strategy
            p1_ok = bool(self.p1_strategy_var.get())

        if self.p2_computer["state"] == "disabled" and self.p2_human["state"] == "normal":
            p2_ok = True
        elif self.p2_human["state"] == "disabled" and self.p2_computer["state"] == "normal":
            p2_ok = bool(self.p2_strategy_var.get())
        else:
            p2_ok = False  # nothing chosen yet

        self.start_button.config(state="normal" if (p1_chosen and p2_chosen and p1_ok and p2_ok) else "disabled")

    def create_players(self):
        """
        Build Player objects only here, just before starting the game.
        As requested, pass the strategy NAME string as the third argument when a player is a computer.
        """
        name1 = (self.p1_name_var.get() or "Player 1").strip() or "Player 1"
        name2 = (self.p2_name_var.get() or "Player 2").strip() or "Player 2"

        # Deduce P1: "Human" chosen when p1_computer is disabled and p1_human is normal (your previous rule)
        if self.p1_computer["state"] == "disabled" and self.p1_human["state"] == "normal":
            p1 = Player.Player(name=name1, is_human=True)
        else:
            # Computer -> pass the strategy name string
            p1_strategy_name = self.p1_strategy_var.get()
            strategy1 = self.create_strategy(p1_strategy_name)
            p1 = Player.Player(name=name1, is_human=False, strategy=strategy1)

        # Deduce P2
        if self.p2_computer["state"] == "disabled" and self.p2_human["state"] == "normal":
            p2 = Player.Player(name=name2, is_human=True)
        else:
            p2_strategy_name = self.p2_strategy_var.get()
            strategy2=self.create_strategy(p2_strategy_name)
            p2 = Player.Player(name=name2, is_human=False, strategy=strategy2)

        return p1, p2

    def finish_setup(self):
        # Create players now
        self.p1, self.p2 = self.create_players()
        # Close setup window
        self.root.destroy()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_strategy(self,strategy_name):
        match strategy_name:
            case "random":

                return RandomStrategy()

            case "safe_choice":

                return SafeChoiceStrategy()

            case "greedy":

                return GreedyStrategy()
            # Add other possible strategies here

            #case "minimax":

                #return MinimaxStrategy()

            case _:
                # default case (if none of the above match)
                raise ValueError(f"Unknown strategy: {strategy_name}")