import card
import random
import util


class CardDeck:
    def __init__(self):
        self.resetDeck()

    def resetDeck(self):
        self.CurrentDeck = []
        for i in range(1, 105):
            p = 1
            if i == 55:
                p = 7
            elif i % 11 == 0:
                p = 5
            elif i % 10 == 0:
                p = 3
            elif i % 5 == 0:
                p = 2
            self.CurrentDeck.append(card.Card(i, p))

    def __str__(self):
        return util.strlst(self.CurrentDeck)

    def popRandom(self):
        i = random.choice(self.CurrentDeck)
        self.CurrentDeck.remove(i)
        return i
