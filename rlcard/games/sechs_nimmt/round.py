from rlcard.games.sechs_nimmt.utils import cards2list, MAX_ROW_SIZE


class SechsNimmtRound:
    ''' Manage the board and turn order of a Sechs Nimmt game.

    Note on the rules model: real Sechs Nimmt is a simultaneous game (every
    player secretly commits a card, then the committed cards are resolved in
    ascending order). RLCard's engine is sequential, so this implementation
    uses the standard sequential approximation: on their turn each player
    plays one card, which is resolved onto the shared board immediately, then
    play passes to the next seat. The core placement rules ("play onto the row
    whose top card is the highest number still below your card", the
    "6th card takes the row" penalty, and the "too-low card takes a row" rule)
    are modelled faithfully. When a player must take a row, the row with the
    fewest bull heads is taken automatically (a common heuristic) rather than
    exposing the choice as a separate action, keeping the action space to one
    action per card.
    '''

    def __init__(self, dealer, num_players, np_random):
        ''' Initialize the round.

        Args:
            dealer (object): The ``SechsNimmtDealer`` object
            num_players (int): The number of players
            np_random (numpy.random.RandomState): The shared RNG
        '''
        self.np_random = np_random
        self.dealer = dealer
        self.num_players = num_players
        self.current_player = 0
        # The board: four rows, each seeded with a single starter card.
        self.board = [[card] for card in dealer.deal_row_cards(4)]

    def proceed_round(self, players, action):
        ''' Play one card for the current player and resolve it onto the board.

        Args:
            players (list): The list of ``SechsNimmtPlayer`` objects
            action (str): The face number (as a string) of the card to play
        '''
        player = players[self.current_player]

        # Remove the chosen card from the player's hand
        number = int(action)
        remove_index = next(index for index, card in enumerate(player.hand)
                            if card.number == number)
        card = player.hand.pop(remove_index)

        self._place_card(player, card)

        self.current_player = (self.current_player + 1) % self.num_players

    def _place_card(self, player, card):
        ''' Resolve a single played card onto the board, collecting bull heads
        for the player when a row is taken.

        Args:
            player (object): The ``SechsNimmtPlayer`` playing the card
            card (object): The ``SechsNimmtCard`` being played
        '''
        # Rows whose top card is lower than the played card are candidates.
        eligible = [index for index, row in enumerate(self.board)
                    if row[-1].number < card.number]

        if not eligible:
            # The card is lower than every row's top card: the player must take
            # a row. Automatically take the row with the fewest bull heads.
            row_index = min(range(len(self.board)),
                            key=lambda i: self._row_bulls(self.board[i]))
            self._take_row(player, row_index, card)
            return

        # Otherwise play onto the row with the highest top card still below the
        # played card (i.e. the closest fit).
        row_index = max(eligible, key=lambda i: self.board[i][-1].number)
        row = self.board[row_index]
        if len(row) >= MAX_ROW_SIZE:
            # This would be the 6th card: the player takes the whole row.
            self._take_row(player, row_index, card)
        else:
            row.append(card)

    def _take_row(self, player, row_index, card):
        ''' The player collects every card currently in a row; the played card
        becomes the new (and only) card of that row.

        Args:
            player (object): The ``SechsNimmtPlayer`` taking the row
            row_index (int): The index of the row being taken
            card (object): The played card that starts the row anew
        '''
        player.bulls += self._row_bulls(self.board[row_index])
        self.board[row_index] = [card]

    @staticmethod
    def _row_bulls(row):
        ''' Total bull heads in a row.

        Args:
            row (list): A list of ``SechsNimmtCard`` objects

        Returns:
            (int): The sum of the bull heads of the cards in the row
        '''
        return sum(card.bulls for card in row)

    def get_legal_actions(self, players, player_id):
        ''' Every card in a player's hand can always be played.

        Args:
            players (list): The list of ``SechsNimmtPlayer`` objects
            player_id (int): The id of the player

        Returns:
            (list): The face numbers (as strings) of the player's hand cards
        '''
        return cards2list(players[player_id].hand)

    def get_state(self, players, player_id):
        ''' Build the raw state dictionary for a player.

        Args:
            players (list): The list of ``SechsNimmtPlayer`` objects
            player_id (int): The id of the player

        Returns:
            (dict): The raw state observed by the player
        '''
        state = {}
        state['hand'] = cards2list(players[player_id].hand)
        state['board'] = [cards2list(row) for row in self.board]
        state['bulls'] = [player.bulls for player in players]
        state['num_cards'] = [len(player.hand) for player in players]
        state['legal_actions'] = self.get_legal_actions(players, player_id)
        return state
