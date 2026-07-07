import unittest
import numpy as np

import rlcard
from rlcard.agents.random_agent import RandomAgent
from rlcard.games.sechs_nimmt.utils import DECK_SIZE, NUM_ROWS
from .determism_util import is_deterministic


class TestSechsNimmtEnv(unittest.TestCase):

    def test_reset_and_extract_state(self):
        env = rlcard.make('sechs-nimmt')
        state, _ = env.reset()
        self.assertEqual(state['obs'].size, (1 + NUM_ROWS) * DECK_SIZE)

    def test_is_deterministic(self):
        self.assertTrue(is_deterministic('sechs-nimmt'))

    def test_get_legal_actions(self):
        env = rlcard.make('sechs-nimmt')
        env.set_agents([RandomAgent(env.num_actions) for _ in range(env.num_players)])
        env.reset()
        legal_actions = env._get_legal_actions()
        for legal_action in legal_actions:
            self.assertLessEqual(legal_action, env.num_actions - 1)

    def test_step(self):
        env = rlcard.make('sechs-nimmt')
        state, _ = env.reset()
        action = np.random.choice(list(state['legal_actions'].keys()))
        _, player_id = env.step(action)
        self.assertEqual(player_id, env.game.round.current_player)

    def test_step_back(self):
        env = rlcard.make('sechs-nimmt', config={'allow_step_back': True})
        state, player_id = env.reset()
        action = np.random.choice(list(state['legal_actions'].keys()))
        env.step(action)
        env.step_back()
        self.assertEqual(env.game.round.current_player, player_id)

        env = rlcard.make('sechs-nimmt', config={'allow_step_back': False})
        state, player_id = env.reset()
        action = np.random.choice(list(state['legal_actions'].keys()))
        env.step(action)
        self.assertRaises(Exception, env.step_back)

    def test_run(self):
        env = rlcard.make('sechs-nimmt')
        env.set_agents([RandomAgent(env.num_actions) for _ in range(env.num_players)])
        trajectories, payoffs = env.run(is_training=False)
        self.assertEqual(len(trajectories), env.num_players)
        self.assertEqual(len(payoffs), env.num_players)
        self.assertAlmostEqual(sum(payoffs), 0)

    def test_run_various_players(self):
        for num_players in (2, 6, 10):
            env = rlcard.make('sechs-nimmt', config={'game_num_players': num_players})
            env.set_agents([RandomAgent(env.num_actions) for _ in range(env.num_players)])
            _, payoffs = env.run(is_training=False)
            self.assertEqual(len(payoffs), num_players)

    def test_get_perfect_information(self):
        env = rlcard.make('sechs-nimmt')
        env.reset()
        info = env.get_perfect_information()
        self.assertEqual(len(info['hand_cards']), env.num_players)
        self.assertEqual(len(info['board']), NUM_ROWS)


if __name__ == '__main__':
    unittest.main()
