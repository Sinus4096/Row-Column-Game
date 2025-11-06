import GameHandler
import tkinter as tk
import RandomStrategy
import Player
from safe_choice_strategy import SafeChoiceStrategy
player_1=input("Do you want player one to be a human or a computer(h/c)? ")
player_2=input("Do you want player two to be a human or a computer(h/c)? ")

if player_1.lower()=="h":
    p1 = Player.Player("Player 1", True)
else:
    # Strategies must be added
 p1 = Player.Player("Player 1", False, SafeChoiceStrategy())
if player_2.lower() == "h":
    p2 = Player.Player("Player 2", True)
else:
    #Strategies must be added
    p2 = Player.Player("Player 2h", False, SafeChoiceStrategy())

game=GameHandler.GameHandler(player1=p1, player2=p2)
game.play()
