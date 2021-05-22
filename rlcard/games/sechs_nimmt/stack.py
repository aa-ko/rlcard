from operator import attrgetter
import util


class Stack:
    def __init__(self, initial):
        self.cards = [initial]

    def __str__(self):
        return util.strlst(self.cards)

    def addCard(self, card):
        if self.canAppend(card):
            self.cards.append(card)
            return 0
        else:
            penalty = self.totalValue()
            self.cards = [card]
            return penalty

    def canAppend(self, card):
        if len(self.cards) >= 5:
            return False
        if self.diff(card) < 0:
            return False
        return True

    def diff(self, card):
        return card.value - self.cards[len(self.cards) - 1].value

    def totalValue(self):
        return sum(map(lambda c: c.points, self.cards))
