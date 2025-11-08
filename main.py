import GameHandler
import tkinter as tk
import RandomStrategy
import Player
from safe_choice_strategy import SafeChoiceStrategy
from GameSetup import GameSetup

setup = GameSetup()
config = setup.run() # config will store the player's choices in a map


p1 = config[0]
p2 = config[1]


game=GameHandler.GameHandler(player1=p1, player2=p2)
game.play()
