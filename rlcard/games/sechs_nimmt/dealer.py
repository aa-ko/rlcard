from rlcard.games.sechs_nimmt.utils import init_deck


class SechsNimmtDealer:
    ''' Initialize a Sechs Nimmt dealer that owns and shuffles the deck.
    '''

    def __init__(self, np_random):
        self.np_random = np_random
        self.deck = init_deck()
        self.shuffle()

    def shuffle(self):
        ''' Shuffle the deck in place.
        '''
        self.np_random.shuffle(self.deck)

    def deal_cards(self, player, num):
        ''' Deal ``num`` cards from the top of the deck to a player.

        Args:
            player (object): A ``SechsNimmtPlayer`` object
            num (int): The number of cards to deal
        '''
        for _ in range(num):
            player.hand.append(self.deck.pop())

    def deal_row_cards(self, num):
        ''' Deal ``num`` cards to seed the initial rows of the board.

        Args:
            num (int): The number of starter cards (one per row)

        Returns:
            (list): A list of ``SechsNimmtCard`` objects
        '''
        return [self.deck.pop() for _ in range(num)]
