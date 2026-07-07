import numpy as np
from collections import OrderedDict

from rlcard.envs import Env
from rlcard.games.sechs_nimmt import Game
from rlcard.games.sechs_nimmt.utils import ACTION_SPACE, ACTION_LIST
from rlcard.games.sechs_nimmt.utils import DECK_SIZE, NUM_ROWS, cards2list

DEFAULT_GAME_CONFIG = {
        'game_num_players': 4,
        }


class SechsNimmtEnv(Env):
    ''' The RLCard environment for Sechs Nimmt (6 nimmt!).

    Observation: a ``(1 + NUM_ROWS, DECK_SIZE)`` binary tensor.
        * plane 0        - the current player's hand (multi-hot over 1..104)
        * planes 1..4    - the cards currently in each of the four board rows
    '''

    def __init__(self, config):
        self.name = 'sechs-nimmt'
        self.default_game_config = DEFAULT_GAME_CONFIG
        self.game = Game()
        super().__init__(config)
        self.state_shape = [[1 + NUM_ROWS, DECK_SIZE] for _ in range(self.num_players)]
        self.action_shape = [None for _ in range(self.num_players)]

    def _extract_state(self, state):
        obs = np.zeros((1 + NUM_ROWS, DECK_SIZE), dtype=int)
        # plane 0: the current player's hand
        for number in state['hand']:
            obs[0][int(number) - 1] = 1
        # planes 1..NUM_ROWS: the four board rows
        for row_index, row in enumerate(state['board']):
            for number in row:
                obs[1 + row_index][int(number) - 1] = 1

        legal_action_id = self._get_legal_actions()
        extracted_state = {'obs': obs, 'legal_actions': legal_action_id}
        extracted_state['raw_obs'] = state
        extracted_state['raw_legal_actions'] = [a for a in state['legal_actions']]
        extracted_state['action_record'] = self.action_recorder
        return extracted_state

    def get_payoffs(self):
        return np.array(self.game.get_payoffs())

    def _decode_action(self, action_id):
        legal_ids = self._get_legal_actions()
        if action_id in legal_ids:
            return ACTION_LIST[action_id]
        return ACTION_LIST[np.random.choice(list(legal_ids.keys()))]

    def _get_legal_actions(self):
        legal_actions = self.game.get_legal_actions()
        legal_ids = {ACTION_SPACE[action]: None for action in legal_actions}
        return OrderedDict(legal_ids)

    def get_perfect_information(self):
        ''' Get the perfect information of the current state.

        Returns:
            (dict): A dictionary of all the perfect information of the current state
        '''
        state = {}
        state['num_players'] = self.num_players
        state['hand_cards'] = [cards2list(player.hand) for player in self.game.players]
        state['board'] = [cards2list(row) for row in self.game.round.board]
        state['bulls'] = [player.bulls for player in self.game.players]
        state['current_player'] = self.game.round.current_player
        state['legal_actions'] = self.game.get_legal_actions()
        return state
