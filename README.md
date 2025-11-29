# Row–Column Game 

This repository contains a Python implementation of the Row–Column Game, a two-player strategic board game. Players take turns selecting numbers, with each move constrained to the row or column of the opponent’s previous choice. Every selected number is removed from the board and added to the player’s score, and the game ends when no valid moves remain.
The game tests both short-term tactics and long-term planning, and provides a platform to experiment with different AI strategies such as Greedy, Minimax, and Monte Carlo Tree Search.

- [Row–Column Game](#rowcolumn-game)
  - [Contributors](#contributors)
  - [Project Overview](#project-overview)
    - [Game Module](#game-module)
    - [Strategies Module](#strategies-module)
    - [Simulations Module](#simulations-module)
  - [Usage](#usage)
  - [Results](#results)
  - [Tools and Libraries](#tools-and-libraries)
  - [Source Code Directory Tree](#source-code-directory-tree)

---

## Contributors
### Anna Roson
  - Development of the core game architecture and setup, including: `fileReading.py`, `GameHandler.py`, `Player.py`, `Board.py` , `main.py`.
  - Design of the graphical interface
  - Implementation of `RandomStrategy.py`
  - Worked on the `GameSetup.py` 
### Antonia Sophie Gilles
  - Developed the core `GameSetup.py` logic.
  - Implemented the random matrix creation. 
  - Worked on `GameHandler.py`and `fileReading.py`
  - Co-created the presentation and presented
### Aron Vaisman
  - Developed the `safe_choice_strategy.py`
### Giulia Dorata
- Developed the `GreedyStrategy.py`
- Performed the `Statistical computations.py` supporting strategy evaluation.
- Graph creation supporting the statistical outputs
### Marton Nemeth
- Developed the Minimax strategy with alpha-beta pruning `minimax_f.py`
- Co-created the presentation and presented
### Sina Maria Schlegel
  - Designed a Monte Carlo Tree Search (MCTS) strategy implementing the standard phases: Selection (using UCB1), Expansion, Simulation (with a greedy bias), and Backpropagation. 
  - Integrated all strategies into a Simulation Engine to evaluate performance. 
  - Ran a statistically robust tournament across multiple board sizes, playing each board twice to eliminate first-mover bias.

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
- `SimulationHandler.py` – Executes repeated games and logs results  
- `Results/` – Raw simulation outputs (CSV summaries, match data)  
- `Statistical Conclusions/` – Win-rate plots and analysis scripts

---
## Usage

To start the game, run:

```bash
python main.py
```

You can select:

- Game mode: Human vs Human, Human vs Computer, or Computer vs Computer
- Board size: Randomly generated NxN boards
- Strategies: Choose between implemented AI strategies

---

## Results

Simulation outcomes comparing AI strategies can be generated using:

```bash
python Simulations/SimulationHandler.py
```
The results show clear performance differences: 
- Minimax was the strongest strategy overall, achieving the highest win rates across all board sizes.  
- MCTS and SafeChoice performed well but consistently ranked below Minimax, while Greedy showed moderate, size-dependent performance.  
- Random was outperformed by every other strategy, winning only a negligible fraction of games.

---

## Tools and Libraries

The following Python libraries were essential for developing the game's core functionality, AI strategies, and statistical evaluation:

### Core Libraries

* [cite_start]**TKINTER**: Used for creating the Graphical User Interface (GUI) for the game[cite: 39, 40].
* [cite_start]**OS**: Used for interaction with the operating system (files, paths, etc.)[cite: 41, 45].
* [cite_start]**RANDOM**: Essential for generating random numbers, used in board generation and the strategies[cite: 42, 46].
* [cite_start]**NUMPY**: Used for computing numerical two-dimensional arrays and mathematical operations necessary for the strategies[cite: 43, 44, 47].
* [cite_start]**TIME**: Used to limit the time of iterations for smoother runs, particularly for Monte Carlo Tree Search (MCTS)[cite: 48, 49].
* [cite_start]**MATH**: Used for mathematical operations for the strategies[cite: 44, 56].
* [cite_start]**COPY**: Used to assist the setup of the statistical simulations[cite: 51, 54].

### Statistical Analsysis and Plotting Libraries
These libraries were used for running the simulations, handling the resulting data, and generating the performance graphs:

* [cite_start]**PANDAS**: Used for assisting the setup of the statistical simulations and data handling of the results[cite: 51, 55].
* [cite_start]**MATPLOTLIB**: Used for plotting the final results of the statistical evaluation[cite: 52, 58].
* [cite_start]**SEABORN**: Used for creating visually appealing statistical graphs and heatmaps, also for plotting the final results[cite: 53, 57].

---

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
│ ├── safe_choice_strategy.py                #Greedy strategy enhanced with defensive heuristics
│ ├── minimax_f.py                           #minimax (alpha-beta pruning) implementation
│ └── MCTS.py                                #Monte Carlo Tree Search
│
├── Simulations/                             #simulations for performance statistics
│   ├── SimulationHandler.py                 #simulation loop
│   ├── Results/                             #stored simulation outputs as CSVs
│   └── Statistical Conclusions/             #plots and statistical analysis scripts
│
└── main.py                                  #entry point for running the game
```



