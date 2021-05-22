import stack
import util
import random


class Board:
    def __init__(self, initials):
        self.stacks = []
        for i in range(4):
            self.stacks.append(stack.Stack(initials[i]))

    def __str__(self):
        return util.strlst(self.stacks)

    def playCard(self, card):
        candidates = {}
        for c in filter(lambda s: s.canAppend(card), self.stacks):
            candidates[c.diff(card)] = c

        if len(candidates) == 0:
            return random.choice(self.stacks).addCard(card)

        diffs = map(lambda c: c.diff(card), candidates.values())
        mindiff = min(diffs, default=0)
        return candidates[mindiff].addCard(card)
