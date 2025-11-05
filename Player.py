class Player:
    def __init__(self, name="Player", is_human=True):
        self.name = name
        self.is_human = is_human
        self.score = 0

    def choose_position(self, available_positions, board):
        if self.is_human:
            print(f"{self.name}, posizioni disponibili: {available_positions}")
            row = int(input("Inserisci riga: "))
            col = int(input("Inserisci colonna: "))
            return (row, col)
        else:
            # Strategia del computer (da implementare in seguito)
            import random
            return random.choice(available_positions)

    def getName(self):
        return self.name