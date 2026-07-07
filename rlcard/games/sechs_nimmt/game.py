from copy import deepcopy
import numpy as np

from rlcard.games.sechs_nimmt import Dealer
from rlcard.games.sechs_nimmt import Player
from rlcard.games.sechs_nimmt import Round
from rlcard.games.sechs_nimmt import Judger
from rlcard.games.sechs_nimmt.utils import DECK_SIZE, HAND_SIZE, NUM_ROWS, NUM_ACTIONS


class SechsNimmtGame:
    ''' The game engine for Sechs Nimmt (6 nimmt!). '''

    def __init__(self, allow_step_back=False, num_players=4):
        self.allow_step_back = allow_step_back
        self.np_random = np.random.RandomState()
        self.num_players = num_players
        self.payoffs = [0 for _ in range(self.num_players)]

    def configure(self, game_config):
        ''' Specify game specific parameters, such as the number of players.

        Args:
            game_config (dict): A config dictionary with ``game_num_players``
        '''
        self.num_players = game_config['game_num_players']

    def init_game(self):
        ''' Deal cards, seed the board and start a new game.

        Returns:
            (tuple): Tuple containing:

                (dict): The first state of the game
                (int): The id of the first player to act
        '''
        # ``num_players`` hands of ``HAND_SIZE`` cards plus one starter card
        # per row must fit into the 104-card deck.
        if self.num_players * HAND_SIZE + NUM_ROWS > DECK_SIZE:
            raise ValueError(
                'Too many players for Sechs Nimmt: %d players need %d cards '
                'but the deck only has %d'
                % (self.num_players, self.num_players * HAND_SIZE + NUM_ROWS, DECK_SIZE))

        self.payoffs = [0 for _ in range(self.num_players)]

        # Initialize a dealer and shuffle the deck
        self.dealer = Dealer(self.np_random)

        # Initialize the players and deal each a hand
        self.players = [Player(i, self.np_random) for i in range(self.num_players)]
        for player in self.players:
            self.dealer.deal_cards(player, HAND_SIZE)

        # Initialize the round (which seeds the four board rows)
        self.round = Round(self.dealer, self.num_players, self.np_random)

        # History for step_back
        self.history = []

        player_id = self.round.current_player
        state = self.get_state(player_id)
        return state, player_id

    def step(self, action):
        ''' Play one card and advance the game.

        Args:
            action (str): The face number (as a string) of the card to play

        Returns:
            (tuple): Tuple containing:

                (dict): The next player's state
                (int): The next player's id
        '''
        if self.allow_step_back:
            his_dealer = deepcopy(self.dealer)
            his_round = deepcopy(self.round)
            his_players = deepcopy(self.players)
            self.history.append((his_dealer, his_players, his_round))

        self.round.proceed_round(self.players, action)
        player_id = self.round.current_player
        state = self.get_state(player_id)
        return state, player_id

    def step_back(self):
        ''' Return to the previous state of the game.

        Returns:
            (bool): True if the game stepped back successfully
        '''
        if not self.history:
            return False
        self.dealer, self.players, self.round = self.history.pop()
        return True

    def get_state(self, player_id):
        ''' Return a player's state.

        Args:
            player_id (int): The id of the player

        Returns:
            (dict): The state of the player
        '''
        state = self.round.get_state(self.players, player_id)
        state['num_players'] = self.get_num_players()
        state['current_player'] = self.round.current_player
        return state

    def get_payoffs(self):
        ''' Return the payoffs of the game.

        The payoff of a player is the mean number of bull heads collected
        across all players minus their own bull heads. Collecting fewer bulls
        than average yields a positive payoff, and the payoffs sum to zero.

        Returns:
            (list): One payoff per player
        '''
        bulls = [player.bulls for player in self.players]
        mean_bulls = sum(bulls) / self.num_players
        self.payoffs = [mean_bulls - player_bulls for player_bulls in bulls]
        return self.payoffs

    def get_legal_actions(self):
        ''' Return the legal actions for the current player.

        Returns:
            (list): The face numbers (as strings) of the current player's cards
        '''
        return self.round.get_legal_actions(self.players, self.round.current_player)

    def get_num_players(self):
        ''' Return the number of players.

        Returns:
            (int): The number of players
        '''
        return self.num_players

    @staticmethod
    def get_num_actions():
        ''' Return the number of applicable actions: one per card number plus
        one per row for the "take a row" decision.

        Returns:
            (int): 108
        '''
        return NUM_ACTIONS

    def get_player_id(self):
        ''' Return the current player's id.

        Returns:
            (int): The current player's id
        '''
        return self.round.current_player

    def is_over(self):
        ''' Check if the game is over (all hands have been played and no card
        is still awaiting a "take a row" decision).

        Returns:
            (bool): True if every player has emptied their hand
        '''
        if self.round.pending_card is not None:
            return False
        return all(len(player.hand) == 0 for player in self.players)

    def get_winner(self):
        ''' Return the winner(s): the player(s) with the fewest bull heads.

        Returns:
            (list): The player id(s) of the winner(s)
        '''
        return Judger.judge_winner(self.players)
