from rlcard.games.sechs_nimmt.utils import cards2list, MAX_ROW_SIZE, TAKE_ROW_ACTIONS


class SechsNimmtRound:
    ''' Manage the board and turn order of a Sechs Nimmt game.

    Note on the rules model: real Sechs Nimmt is a simultaneous game (every
    player secretly commits a card, then the committed cards are resolved in
    ascending order). RLCard's engine is sequential, so this implementation
    uses the standard sequential approximation: on their turn each player
    plays one card, which is resolved onto the shared board immediately, then
    play passes to the next seat. The placement rules ("play onto the row
    whose top card is the highest number still below your card" and the
    "6th card takes the row" penalty) are modelled faithfully.

    When a player plays a card lower than every row's top card they must gather
    a row of their choice. This is modelled as a genuine decision: playing such
    a card does not immediately advance the turn but puts the round into a
    "pending" state where the same player chooses a row to take via one of the
    ``take-r`` actions. Only then does play pass to the next seat.
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
        # A card awaiting its owner's choice of which row to take (or None).
        self.pending_card = None

    def proceed_round(self, players, action):
        ''' Advance the game by one action.

        Args:
            players (list): The list of ``SechsNimmtPlayer`` objects
            action (str): Either the face number (as a string) of a card to
                play, or a ``take-r`` action choosing a row to gather
        '''
        # Second phase: the current player resolves a pending "take a row".
        if action in TAKE_ROW_ACTIONS:
            row_index = int(action.split('-')[1])
            self._take_row(players[self.current_player], row_index, self.pending_card)
            self.pending_card = None
            self.current_player = (self.current_player + 1) % self.num_players
            return

        # First phase: the current player plays a card from their hand.
        player = players[self.current_player]
        number = int(action)
        remove_index = next(index for index, card in enumerate(player.hand)
                            if card.number == number)
        card = player.hand.pop(remove_index)

        # Rows whose top card is lower than the played card are candidates.
        eligible = [index for index, row in enumerate(self.board)
                    if row[-1].number < card.number]

        if not eligible:
            # The card is lower than every row's top card. The player must take
            # a row of their choice: enter the pending state without advancing.
            self.pending_card = card
            return

        # Play onto the row with the highest top card still below the played
        # card (i.e. the closest fit).
        row_index = max(eligible, key=lambda i: self.board[i][-1].number)
        row = self.board[row_index]
        if len(row) >= MAX_ROW_SIZE:
            # This would be the 6th card: the player takes the whole row.
            self._take_row(player, row_index, card)
        else:
            row.append(card)

        self.current_player = (self.current_player + 1) % self.num_players

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
        ''' The legal actions for a player.

        While a card is pending a row choice, the only legal actions are the
        four ``take-r`` actions. Otherwise every card in hand can be played.

        Args:
            players (list): The list of ``SechsNimmtPlayer`` objects
            player_id (int): The id of the player

        Returns:
            (list): The legal action strings
        '''
        if self.pending_card is not None:
            return list(TAKE_ROW_ACTIONS)
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
        state['pending_card'] = self.pending_card.get_str() if self.pending_card else None
        state['legal_actions'] = self.get_legal_actions(players, player_id)
        return state
