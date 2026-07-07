from collections import OrderedDict

from rlcard.games.sechs_nimmt.card import SechsNimmtCard as Card

# Game constants
DECK_SIZE = 104        # cards numbered 1..104
NUM_ROWS = 4           # the board has four rows
MAX_ROW_SIZE = 5       # taking the 6th card forces you to collect the row
HAND_SIZE = 10         # each player is dealt 10 cards

# The action space is simply "play card with face number n". Action id ``n-1``
# corresponds to playing the card numbered ``n``. ``ACTION_LIST[i]`` is the
# string representation of the card played by action ``i``.
ACTION_LIST = [str(number) for number in range(1, DECK_SIZE + 1)]
ACTION_SPACE = OrderedDict({action: index for index, action in enumerate(ACTION_LIST)})


def init_deck():
    ''' Build a fresh, ordered Sechs Nimmt deck of 104 cards.

    Returns:
        (list): A list of ``SechsNimmtCard`` numbered 1..104
    '''
    return [Card(number) for number in range(1, DECK_SIZE + 1)]


def cards2list(cards):
    ''' Get the string representation of a list of cards.

    Args:
        cards (list): A list of ``SechsNimmtCard`` objects

    Returns:
        (list): A list of card face numbers as strings
    '''
    return [card.get_str() for card in cards]


def encode_cards(plane, cards):
    ''' Set the multi-hot ``plane`` (length ``DECK_SIZE``) for a list of cards.

    Args:
        plane (numpy.array): A 1-D array of length ``DECK_SIZE``
        cards (list): A list of ``SechsNimmtCard`` objects
    '''
    for card in cards:
        plane[card.number - 1] = 1
