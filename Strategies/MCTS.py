import math
import random
import sys
import os
import time

#look for "Strategy" in the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Strategies.Strategy import Strategy

#set exploration parameter to sqrt(2), is used to balance exploration and exploitation
UCB_CONST=math.sqrt(2)


#create a MCTSNode class to represent each node in the search tree. Each node corresponds
# to a specific state of the Row-Column game.

class MCTSNode:
    def __init__(self, board, last_move, player_turn, parent=None, move=None, scores=(0, 0)):
        """
        Initializes a node in the search tree-> what board looks like
        """
        self.board=board                      #what game board looks like at this node, according to setup value 0 = taken number
        self.last_move = last_move              #last move taken
        self.player_turn =player_turn          #which player's turn it is
        self.parent =parent                    #parent node of this node/state
        self.move=move                        #move that resulted in this node's state
        self.scores =scores                    #store the player's scores for that node

        self.visits=0                       #visit count
        self.score_total=0.0                #score overview
        self.children = []                      #list of child nodes
        
        #get moves to be explored in the algo
        self.untried_actions =self.get_available_moves(self.board, self.last_move)
        
        #shuffle to ensure random exploration for moves with same value
        random.shuffle(self.untried_actions)
        
        #sort list so highest values are at the end -> pop() will take the best move first (Greedy optimization)
        self.untried_actions.sort(key=lambda m: self.board[m[0]][m[1]])

    
    @staticmethod 
    def get_available_moves(board, last_move):
        """
        return all all valid moves from the current state for any board and any last_move-> can use it in simulation
        """
        #first move of the game:
        if last_move is None:
            return [(r, c) for r, row in enumerate(board) for c, val in enumerate(row) if val!= 0]
        
        moves= []

        #coordinates of last move
        last_r, last_c =last_move
        
        #add all row coordinates to moves list, if they were not taken already (-> not set to 0 in setup)
        #speed optimization: direct access
        row_data = board[last_r]
        for col in range(len(row_data)):
            if row_data[col]!= 0:
                moves.append((last_r, col))
        
        #same cor columns
        for r in range(len(board)):
            if r !=last_r and board[r][last_c]!= 0:
                moves.append((r, last_c))
                
        return moves
    
    def is_terminal(self):
        """Check if the game has ended."""
        #ends if list of untried actions from node on is empty and have not created any further nodes from here on
        return len(self.untried_actions)== 0 and len(self.children)==0
    
    def is_fully_expanded(self):
        """
        returns True if all possible child nodes have been created
        """
        return len(self.untried_actions) ==0
    
    def expand(self):
        """
        adds one of the remaining actions as a child node ->investigate move AI hasn't looked at before
        """
        #check if there really are untried moves:
        if not self.untried_actions:
            return None
        
        action=self.untried_actions.pop()             #take last move from moves list and remove it (best move due to sort)
        
        #want to simulate future without messing up present-> copy
        #manual list comprehension is faster than deepcopy here
        copied_board =[row[:] for row in self.board]
        
        value_of_move= copied_board[action[0]][action[1]]   #get value of action from the copied board
        copied_board[action[0]][action[1]]=0                  #remove the action on the copied board 

        #update scores card: first convert to list because tuples are immutable
        new_scores =list(self.scores)                      
        new_scores[self.player_turn-1] +=value_of_move   #if player1's turn, update 1. of score board

        #switch players as child node will be played by other player (if Player1-> 3-1=Player 2)
        next_player_turn =3-self.player_turn

        #create and add the new child node to the tree
        child =MCTSNode(board=copied_board, last_move=action, player_turn=next_player_turn, parent=self,
            move=action, scores=tuple(new_scores))
        self.children.append(child)
        return child
    
    def best_child(self):
        """
        Select child with best UCB1 score (according to formula on Webpage mentioned above).
        This score balances exploitation of the moves currently known to be good with exploration of 
        less-visited moves to ensure a potentially better strategy hasn't been overlooked
        """
        #initialize
        best_child =None
        best_score =-float('inf')

        #pre-calculate log for speed
        log_n =math.log(self.visits)

        for child in self.children:
            #if a child haven't been visited, choose it to make sure every child is getting visited at least once
            if child.visits==0:
                return child

            # UCB1 formula: \text{UCB1}(i) = \bar{X}_i + c \sqrt{\frac{\ln(N)}{n_i}}
            exploitation_term= child.score_total/child.visits
            exploration_term =UCB_CONST*math.sqrt(log_n/child.visits)
            ucb_score=exploitation_term+exploration_term

            if ucb_score >best_score:
                best_score=ucb_score
                best_child=child

        return best_child
    
    
    def update(self, result):
        """
        updates node's visit count and number of wins during backpropagation
        """
        self.visits +=1
        self.score_total+=result    #-1 if the outcome of simulation is a loss, 0 for draw, 1 for win

    
class MCTSStrategy(Strategy):
    """
    Implementing the MCTS Search, it performs:
    -Selection: choose a promising node.
    -Expansion: add new nodes for unexplored moves.
    -Simulation: play random games.
    -Backpropagation: update nodes with results.
    """
    
    def __init__(self, max_iterations=10000, time_limit=5):   #set time_limit=0.3 when running multiple simulations to have results in reasonable amount of time 
        """
        Want to have speed and efficiency limit.
        Speed limit-> don't have to wait too long
        """
        self.max_iterations=max_iterations
        self.time_limit= time_limit

    def move(self, board, last_move, scores):
        """
        Analyzes the current game state and returns the best move.
        """

        #until now have used 0 for used moves, but in gamehandler is a "-" -> convert:
        internal_board =[[0 if cell=="-" else cell for cell in row] for row in board]

        #calculate total sum available on board -> used to normalize score later
        total_sum =sum(v for row in internal_board for v in row if v>0) or 1

        #determine whose turn it is by counting the moves already made.
        moves_made =sum(row.count(0) for row in internal_board)
        player_id=2 if moves_made%2 else 1
        
        #start stopping thinking time:
        start_time = time.time()

        #create root node= current state of real game
        root =MCTSNode(board=internal_board, last_move=last_move, player_turn=player_id, scores=tuple(scores))

        #trivial moves: if no move available return None, and if only 1 move available choose that without simulating
        if not root.untried_actions:
            return None
        if len(root.untried_actions) ==1:
            return root.untried_actions[0]
        
        #repeat 4 steps of MCTS as many times as possible-> until the time runs out
        while (time.time()-start_time< self.time_limit):

            #Selection: travels down the tree, with UCB1 until it hits a node that hasn't been fully explored (=leaf)
            node =root
            while not node.is_terminal() and node.is_fully_expanded():
                node =node.best_child()
            
            #Expansion: at leaves pick one move, it hasn't tried before and create a new child node for it
            #due to sorting in __init__, this picks the best greedy move first
            if not node.is_terminal() and not node.is_fully_expanded():
                node= node.expand()

            #Simulation: AI plays randomly until the game ends
            result= self.simulate(node, total_sum)
            
            #Backpropagation: AI traces its steps back up the tree, back o root
            self.backpropagate(node, result)

        #select child with highest visit count -> most robust move when time is short
        best_child =max(root.children, key=lambda c: c.visits)
        return best_child.move

    def simulate(self, node, total_sum):
        """
        Simulation phase: play a random game and return the outcome
        """
        #want to simulate future without messing up present-> copy
        copied_board =[row[:] for row in node.board]
        copied_last_move = node.last_move
        
        #track scores locally
        p1_score =node.scores[0]
        p2_score= node.scores[1]
        
        #player whose perspective will evaluate the final score from.
        perspective_player = node.player_turn

        #track turn in simulation
        sim_turn = node.player_turn

        while True:
            #get available moves manually to avoid function overhead
            moves = []
            if copied_last_move is None:
                 moves = [(r, c) for r, row in enumerate(copied_board) for c, val in enumerate(row) if val != 0]
            else:
                lastrow, lastcol =copied_last_move
                #add all row coordinates
                moves.extend([(lastrow, col) for col in range(len(copied_board[0])) if copied_board[lastrow][col]!= 0])
                #same for columns
                moves.extend([(row, lastcol) for row in range(len(copied_board)) if row !=lastrow and copied_board[row][lastcol]!= 0])

            if not moves:
                break #Game over

            #epsilon = 0.5 -> instead of pure random choice, want 50% to be greedy heuristics-> no waste of time on bad moves
            if random.random()<0.5:
                move = random.choice(moves)
            else:
                #pick the move with the highest immediate value
                move =max(moves, key=lambda m: copied_board[m[0]][m[1]])
            
            #apply random move to the temporary state & get value for it
            val =copied_board[move[0]][move[1]]
            copied_board[move[0]][move[1]]=0
            #add value to scores
            if sim_turn ==1:
                p1_score +=val
            else:
                p2_score +=val
            
            #move in simulation and swithc player
            copied_last_move =move
            sim_turn =3-sim_turn

        #calculate final scores from the perspective_player's point of view
        if perspective_player== 1:
            raw =p1_score-p2_score
        else:
            raw = p2_score-p1_score

        #return score difference
        return raw/total_sum
    
    
    def backpropagate(self, node, result):
        """
        backpropagation phase: update node statistics up the tree
        """
        #start at leaf node
        current_node =node
        sign =-1
        
        #move up and give results back 
        while current_node is not None:
            current_node.update(sign*result)
            sign =-sign
            current_node =current_node.parent






