import unittest
import numpy as np

from rlcard.games.sechs_nimmt.game import SechsNimmtGame as Game
from rlcard.games.sechs_nimmt.card import SechsNimmtCard as Card
from rlcard.games.sechs_nimmt.utils import ACTION_LIST, DECK_SIZE, NUM_ROWS, HAND_SIZE


class TestSechsNimmtMethods(unittest.TestCase):

    def test_get_num_players(self):
        game = Game()
        self.assertEqual(game.get_num_players(), 4)

    def test_get_num_actions(self):
        game = Game()
        self.assertEqual(game.get_num_actions(), DECK_SIZE)

    def test_bulls(self):
        # Bull-head values for the special cards
        self.assertEqual(Card(55).bulls, 7)
        self.assertEqual(Card(11).bulls, 5)
        self.assertEqual(Card(10).bulls, 3)
        self.assertEqual(Card(15).bulls, 2)
        self.assertEqual(Card(1).bulls, 1)

    def test_init_game(self):
        game = Game()
        state, player_id = game.init_game()
        self.assertIn(player_id, range(game.get_num_players()))
        self.assertEqual(len(state['hand']), HAND_SIZE)
        self.assertEqual(len(state['board']), NUM_ROWS)
        # Each row starts with a single card
        for row in state['board']:
            self.assertEqual(len(row), 1)

    def test_get_player_id(self):
        game = Game()
        _, player_id = game.init_game()
        self.assertEqual(player_id, game.get_player_id())

    def test_get_legal_actions(self):
        game = Game()
        game.init_game()
        actions = game.get_legal_actions()
        self.assertEqual(len(actions), HAND_SIZE)
        for action in actions:
            self.assertIn(action, ACTION_LIST)

    def test_step(self):
        game = Game()
        _, player_id = game.init_game()
        action = np.random.choice(game.get_legal_actions())
        _, next_player_id = game.step(action)
        self.assertEqual(next_player_id, (player_id + 1) % game.get_num_players())

    def test_play_full_game(self):
        game = Game()
        game.init_game()
        while not game.is_over():
            action = np.random.choice(game.get_legal_actions())
            game.step(action)
        # Every hand is empty at the end
        for player in game.players:
            self.assertEqual(len(player.hand), 0)

    def test_get_payoffs(self):
        game = Game()
        game.init_game()
        while not game.is_over():
            action = np.random.choice(game.get_legal_actions())
            game.step(action)
        payoffs = game.get_payoffs()
        self.assertEqual(len(payoffs), game.get_num_players())
        # Mean-centred payoffs must sum to zero
        self.assertAlmostEqual(sum(payoffs), 0)

    def test_step_back(self):
        game = Game(allow_step_back=True)
        _, player_id = game.init_game()
        action = np.random.choice(game.get_legal_actions())
        game.step(action)
        self.assertTrue(game.step_back())
        self.assertEqual(game.get_player_id(), player_id)
        # No more history to step back through
        self.assertFalse(game.step_back())

    def test_two_players(self):
        game = Game(num_players=2)
        state, _ = game.init_game()
        self.assertEqual(state['num_players'], 2)
        self.assertEqual(len(game.players), 2)


if __name__ == '__main__':
    unittest.main()
