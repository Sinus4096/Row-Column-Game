# Row–Column Game 

This repository contains a Python implementation of the Row–Column Game, a two-player strategic board game. Players alternately select numbers from a matrix, restricted to the opponent’s last row or column choice.  
The game tests both short-term tactics and long-term planning, and provides a platform to experiment with different AI strategies such as Greedy, Minimax, and Monte Carlo Tree Search.

---

## Contributors
- Anna Roson
- Antonia Sophie Gilles
- Aron Vaisman
- Giulia Dorata
- Marton Nemeth
- Sina Maria Schlegel

---

## Project Overview

### Game Module
Implements the game’s mechanics, rules, and player interactions.
- `Board.py` – Board representation and move handling  
- `Player.py` – Player class with score tracking  
- `GameHandler.py` – Core game loop and turn management  
- `GameSetup.py` – Mode, board, and player setup  
- `fileReading.py` – Loads matrix configurations from text files  

### Strategies Module
Includes multiple AI strategies, all following a common interface (`Strategy.py`).
- `RandomStrategy.py` – Chooses random legal moves  
- `GreedyStrategy.py` – Picks the highest immediate value  
- `safe_choice_strategy.py` – Prioritizes safe moves for future flexibility  
- `minimax_f.py` – Lookahead search using a minimax heuristic  
- `MCTS.py` – Monte Carlo Tree Search for probabilistic play  

### Simulations Module
Handles running multiple automated simulations and analyzing results.
To be continued....

---

## Installation

To set up the project locally:

# Clone the repository
```bash
git clone https://github.com/<Sinus4096>/RC-Game.git
cd RC-Game
```
# Install dependencies (if required)
```bash
pip install -r requirements.txt
```

## Usage

To start the game, run:

```bash
python main.py
```

You can select:

- Game mode: Human vs Human, Human vs Computer, or Computer vs Computer
- Board size: Randomly generated NxN boards
- Strategies: Choose between implemented AI strategies

## Results

Simulation outcomes comparing AI strategies can be generated using:

```bash
python Simulations/SimulationHandler.py
```
TO be continued........................

## Source Code Directory Tree
```bash
.
├── Game/                                    #game logic and components
│ ├── Board.py                               #board rendering
│ ├── fileReading.py                     
│ ├── GameHandler.py                         #main game loop and turn handling
│ ├── GameSetup.py                           #initialization of board and players
│ └── Player.py                              #player class and score tracking
│
├── Strategies/                              #AI strategies and decision algorithms
│ ├── Strategy.py                            #base strategy interface
│ ├── RandomStrategy.py                      #random move selection
│ ├── GreedyStrategy.py                      #greedy move selection
│ ├── safe_choice_strategy.py                #???????????????????????????
│ ├── minimax_f.py                           #minimax (alpha-beta pruning) implementation
│ └── MCTS.py                                #Monte Carlo Tree Search
│
├── Simulations/                             #simulations for performance statistics
│ ├── SimulationHandler.py                   #simulation loop
│ └── Results/                               #stored simulation outputs & plots
│
└── main.py                                  #entry point for running the game
```



