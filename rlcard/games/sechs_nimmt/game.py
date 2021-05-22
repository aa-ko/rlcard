import deck
import player
import stack
import util
import board


class Game:
    def __init__(self):
        self.deck = deck.CardDeck()
        self.players = []
        self.board = board.Board([self.deck.popRandom() for i in range(4)])
        for i in range(4):
            p = player.Player(i)
            for i in range(10):
                p.addHardCard(self.deck.popRandom())
            self.players.append(p)

    def __str__(self):
        return "\n".join([
            "Deck: %s" % self.deck,
            "Players: %s" % util.strlst(self.players),
            "Board: %s" % self.board])

    def run(self):
        for turn in range(10):
            for player in self.players:
                # Do not pass boardstate yet.
                crd = player.makePlay(None)
                pen = self.board.playCard(crd)
                player.addPenalty(pen)
                print("Player %s (%s) played the card %s and got a penalty of %s points" %
                      (player.name, player, crd, pen))
                print("Board: %s" % self.board)
        return [p.PenaltyPoints for p in self.players]

    def printResult(self):
        for p in self.players:
            print("Player %s has %s points." % (p.name, p.PenaltyPoints))
