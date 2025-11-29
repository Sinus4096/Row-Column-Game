from Game.GameSetup import GameSetup
from Game.GameHandler import GameHandler

# initializes and runs a GameSetup
setup = GameSetup()
config = setup.run() # config will store the player's choices in a map

# GameSetup returns the two players
p1 = config[0]
p2 = config[1]

# initializes and runs a GameHandler that will start the game
game=GameHandler(player1=p1, player2=p2)
game.play()
