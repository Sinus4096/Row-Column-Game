import random
import numpy as np
import pandas as pd
import sys
import os
# need file to be able to see the Game and Strategies folders to run it driectly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from Strategies.RandomStrategy import RandomStrategy
from Strategies.GreedyStrategy import GreedyStrategy
from Strategies.MCTS import MCTSStrategy
from Strategies.safe_choice_strategy import SafeChoiceStrategy
from Strategies.minimax_f import AlphaBetaStrategy
from Game.Player import Player

#each random board is played twice to eliminate first-mover bias -> will have to swap roles
games_per_board=2 

class SimulationEngine:
    """
    need a new class that can run an entire game from start to finish in memory, without opening any windows
    """
    def __init__(self, player1, player2, board_matrix):
        """
        initializes a new game 
        """
        self.players =[player1, player2]       #store players in list
        self.matrix =np.copy(board_matrix)     #create copy of the board to not modify original matrix
        self.dim = len(self.matrix)             #store dim of board
        self.score=[0, 0]                     #initialize score count
        self.current_player=0                 #start game with player 1
        self.last_move =None                   #no moves yet-> initializes last move made with None

    def get_available_moves(self):
        """
        find all valid moves for the current player
        """
        moves =[]
        
        #   first move-> everything is possible-> iterate over entire board and assure no move already taken
        if self.last_move is None:
            for r in range(self.dim):
                for c in range(self.dim):
                    if self.matrix[r][c] !="-": #check if cell is not taken
                        moves.append((r, c))
            return moves

        #subsequent moves: limited to row or column of the last move
        last_r, last_c =self.last_move

        #same column
        for r in range(self.dim):
            #check if cell is not taken
            if self.matrix[r][last_c] !="-": 
                moves.append((r, last_c))
        #same row (avoid double-adding intersection)
        for c in range(self.dim):
            if c !=last_c and self.matrix[last_r][c] !="-": #skip the intersection cell if already added from column check
                moves.append((last_r, c))
        
        return moves

    def run_game(self):
        """
        run until no moves are left, return final score and winner
        """

        while True:
            #find all moves based on current board
            available_moves =self.get_available_moves()
            
            #if no moves available-> end
            if not available_moves:
                break

            #get current player
            player =self.players[self.current_player]

            #ask AI strategy to choose a move 
            move =player.move(self.matrix, self.last_move, self.score) 

            #if move is non legal-> return VAlue Error
            if move not in available_moves:
                raise ValueError(f"Non-available move by player {self.current_player}.")
                        
            #devide returned move in coordinates
            row, col =move

            #get value from chosen move and add to player's score
            value = self.matrix[row][col]
            self.score[self.current_player] +=value
            
            #mark cell as taken and store the move as last taken move
            self.matrix[row][col] ="-" 
            self.last_move =(row, col)

            #switch players
            self.current_player = 1-self.current_player 


        #left loop-> can determine a winner
        p1_score, p2_score = self.score
        
        winner ="Tie"
        if p1_score> p2_score:
            winner ="P1"
        elif p2_score> p1_score:
            winner ="P2"
            
        # return result in dic
        return {"p1_score": p1_score, "p2_score": p2_score, "winner": winner}
    

def create_random_board(size: int) -> np.ndarray:
    """
    geenerate random NxN board for the simulation
    """
    #create list of lists for game 
    matrix =[[random.randint(1, 9) for row in range(size)] for col in range(size)]
    #convert to array with object type, so will be able to store '-' for used fields
    return np.array(matrix, dtype=object) 

def create_strategy(name: str):
    """
    match string names to the strategies
    """
    if name =="Random": return RandomStrategy()
    if name =="Greedy": return GreedyStrategy()
    if name == "SafeChoice": return SafeChoiceStrategy()
    if name =="MCTS": return MCTSStrategy()
    if name =="Minimax": return AlphaBetaStrategy()
    raise ValueError(f"{name}-strategy not existent for game")


class SimulationRunner:
    def __init__(self, number_of_simulations=None, strategies=None, board_dims=None, boards_per_size=None): # New boards_per_size parameter
        """
        initialize one simulation run
        """
        if strategies is None:
            strategies =["Random", "Greedy", "SafeChoice", "MCTS", "Minimax"]
        if board_dims is None:
            #decide for small medium and large games of even and odd row/col numbers
            board_dims =[3, 5, 6, 8, 9] 
        if boards_per_size is None:
            #new parameter to set the number of boards for each size
            #based on 97% CI, h=3% calculation: n=(z/2h)^2 * 0.25 -> 1308 games total / 2 games per board / 5 sizes -> approx. 131 boards per size
            #see calculation below for details (maybe put in README later)
            boards_per_size ={3: 132, 5: 132, 6: 132, 8: 132, 9: 132}

        self.strategies = strategies                   #which strategies to be used
        self.number_of_simulations = number_of_simulations #kept for legacy, but board_per_size dictates counts now
        self.results =[]                              #initialize list with results (Win, Loss, Tie)
        self.board_dim= board_dims
        self.boards_per_size=boards_per_size         #store the new board counts per dimension

    def run_match(self, board_dim, P1_strat, P2_strat, set_of_boards):
        """
        run one single match up of competing strategy pairs, but both of them get first mover advantage once-> check how performance
        is as 1. and 2. player. Returns raw counts for later aggregation.
        """
        
        #raw counts for S1 and S2
        S1_wins_as_P1 =S1_wins_as_P2 = 0
        S2_wins_as_P1 =S2_wins_as_P2 =0
        ties= 0
        #track first-mover advantage
        starter_wins = 0 

        #iterate through generated boards, so that the strategies can play the exact same boards twice 
        for board in set_of_boards:
            #Game 1: S1=P1 (-> is starter), S2=P2
            #set up game with random board, creating player with their strategies
            engine1 = SimulationEngine(Player(P1_strat, False, create_strategy(P1_strat)),Player(P2_strat, False, create_strategy(P2_strat)),np.copy(board))
            
            #run game simulation to completion
            r1 = engine1.run_game()
        
            if r1["winner"] =="P1":        #S1 wins as P1
                S1_wins_as_P1 +=1
                starter_wins +=1
            elif r1["winner"] =="P2":      #S2 wins as P2
                S2_wins_as_P2 +=1
            else:
                ties += 1

            #Game 2: S2=P1, S1=P2
            engine2 = SimulationEngine(Player(P2_strat, False, create_strategy(P2_strat)),Player(P1_strat, False, create_strategy(P1_strat)),np.copy(board) )
            r2 = engine2.run_game()

            if r2["winner"]== "P1":        #S2 wins as P1
                S2_wins_as_P1 +=1
                starter_wins +=1
            elif r2["winner"] =="P2":      #S1 wins as P2
                S1_wins_as_P2 +=1
            else:
                ties +=1
        
        #calculate rates for printing and data storage
        boards = len(set_of_boards)
        total_games = boards*games_per_board
        non_ties =max(1, total_games - ties)       #         avoid division by zero if all games were ties

        #rates by role (bumber of wins / number boards (-> number it was P1 and/or P2))
        S1_win_rate_as_P1= S1_wins_as_P1/boards
        S1_win_rate_as_P2 =S1_wins_as_P2/boards
        S2_win_rate_as_P1= S2_wins_as_P1/boards
        S2_win_rate_as_P2 = S2_wins_as_P2/boards

        #overall rates (number of wins/ number of games played against other strategy)
        S1_overall =(S1_wins_as_P1+S1_wins_as_P2)/total_games
        S2_overall =(S2_wins_as_P1+S2_wins_as_P2)/total_games
        tie_rate =ties/total_games
        starter_win_rate =starter_wins/non_ties

        #return all raw counts and calculated rates for complete data storage
        return {"board_size": board_dim, "boards": boards, "games_per_board": games_per_board, "total_games_matchup": total_games,
            "S1": P1_strat, "S2": P2_strat,

            #raw counts -> can aggregate later
            "S1_wins_as_P1": S1_wins_as_P1, "S1_wins_as_P2": S1_wins_as_P2, "S2_wins_as_P1": S2_wins_as_P1, "S2_wins_as_P2": S2_wins_as_P2,
            "ties": ties,

            #rates of strategy in each roles
            "S1_win_rate_as_P1": S1_win_rate_as_P1, "S1_win_rate_as_P2": S1_win_rate_as_P2, "S2_win_rate_as_P1": S2_win_rate_as_P1,
            "S2_win_rate_as_P2": S2_win_rate_as_P2,

            #overalls + meta
            "S1_overall_win_rate": S1_overall, "S2_overall_win_rate": S2_overall, "total_tie_rate": tie_rate,
            "starter_win_rate": starter_win_rate
        }


    def run_iteration(self):
        """
        iterate through board dimensions and strategies
        """
        #check if boards_per_size is defined for all dimensions
        missing = [s for s in self.board_dim if s not in self.boards_per_size]
        if missing:
            raise KeyError(f"missing boards_per_size entries for sizes: {missing}")
        
        for size in self.board_dim:
            #use the determined number of boards for the size
            n_boards = self.boards_per_size[size] 
            
            #generate all boards per size to ensure fair match ups
            boards_set = [create_random_board(size) for _ in range(n_boards)] 

            #iterate through strategies, while avoiding duplicate pairs (A,B) and (B,A)
            for index1, s1 in enumerate(self.strategies):
                for index2, s2 in enumerate(self.strategies):
                    #avoid duplication
                    if index1>=index2:
                        continue
                    
                    #run the games on fixed boards for fairness
                    data =self.run_match(size, s1, s2, boards_set)
                    #append the generated results to the result list
                    if data:
                        self.results.append(data)
    
    def save_results(self, filename="simulation_results2.csv"): 
        """
        saves the simulation results as csv and exports
        """
        df =pd.DataFrame(self.results)
        #define directory to save in 'results' subfolder
        out_dir =os.path.join(current_dir, "results") 
        os.makedirs(out_dir, exist_ok=True)
        
        csv_path= os.path.join(out_dir, filename)
        df.to_csv(csv_path, index=False)
        return csv_path

def aggregate_per_strategy(csv_path: str, out_name="strategy_summary.csv"):
    """Aggregate overall per-strategy win rates as P1 and as P2 across all opponents & sizes."""
    df =pd.read_csv(csv_path)

    #wins when the strategy appears as S1 (P1/P2) + when it appears as S2 (P1/P2)
    wins_as_P1 =(df.groupby("S1")["S1_wins_as_P1"].sum().add(df.groupby("S2")["S2_wins_as_P1"].sum(), fill_value=0))
    wins_as_P2 = (df.groupby("S1")["S1_wins_as_P2"].sum().add(df.groupby("S2")["S2_wins_as_P2"].sum(), fill_value=0))
    
    #each matchup contributes exactly one game as P1 and one as P2 per board
    games_as_P1 =(df.groupby("S1")["boards"].sum().add(df.groupby("S2")["boards"].sum(), fill_value=0))

    #symmetric by design-> just make copy
    games_as_P2 =games_as_P1.copy()  

    summary =pd.DataFrame({"wins_as_P1": wins_as_P1.astype(int), "games_as_P1": games_as_P1.astype(int),"win_rate_as_P1": wins_as_P1 / games_as_P1,
        "wins_as_P2": wins_as_P2.astype(int), "games_as_P2": games_as_P2.astype(int),
        "win_rate_as_P2": wins_as_P2 / games_as_P2,}).sort_values(["win_rate_as_P1", "win_rate_as_P2"], ascending=False)

    out_dir =os.path.join(current_dir, "results")
    os.makedirs(out_dir, exist_ok=True)
    out_path =os.path.join(out_dir, out_name)
    summary.to_csv(out_path, index=True)
    return out_path


#run code/simulation
if __name__ =="__main__":
    #execute simulation by calling functions
    #reasoning for calculation for number of simulations:
    #goal: 97% CI with half-width (h) = 3% (±0.03) for binomial win rate, worst case p=0.5
    #formula for sample size n:
    #$$n = \frac{z^2 \times p(1-p)}{h^2}$$
    #For 97% CI, z-score $z \approx 2.17$. Max variance is $p(1-p) = 0.5 \times 0.5 = 0.25$
    #$$n = \frac{2.17^2 \times 0.25}{0.03^2} = \frac{4.7089 \times 0.25}{0.0009} \approx 1308.05$$
    #total independent games needed: $\mathbf{1308}$
    #each board is played 2 times (->games_per_board=2), so total boards needed: $1308 / 2 = 654$
    #distributed evenly over 5 board sizes: $654 / 5 = 130.8$
    #set boards_per_size to 132 for each size to be safe.
    
    runner = SimulationRunner(
        strategies=["Random", "Greedy", "SafeChoice", "MCTS", "Minimax"],
        board_dims=[3, 5, 6, 8, 9],
        boards_per_size = {3: 132, 5: 132, 6: 132, 8: 132, 9: 132} #set based on 97% CI calculation
    )
    runner.run_iteration()
    results_csv = runner.save_results()
    #aggregate overall results per strategy for a final summary
    aggregate_per_strategy(results_csv)
