import random
from operator import attrgetter
import util


class Player:
    def __init__(self, name):
        self.name = name
        self.HandCards = []
        self.PenaltyPoints = 0

    def __str__(self):
        return util.strlst(self.HandCards)

    def makePlay(self, boardstate):
        # For now, players will play random card everytime, boardstate is not passed yet.
        i = random.choice(self.HandCards)
        self.HandCards.remove(i)
        return i

    def addPenalty(self, points):
        self.PenaltyPoints += points

    def addHardCard(self, card):
        self.HandCards.append(card)
        self.HandCards.sort(key=attrgetter("value"))


class SechsNimmtPlayer(object):

    def __init__(self, player_id, np_random):
        ''' Initilize a player.

        Args:
            player_id (int): The id of the player
        '''
        self.np_random = np_random
        self.player_id = player_id
        self.hand = []
        self.stack = []

    def get_player_id(self):
        ''' Return the id of the player
        '''

        return self.player_id
