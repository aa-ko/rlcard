import unittest
import numpy as np

from rlcard.games.sechs_nimmt.game import SechsNimmtGame as Game
from rlcard.games.sechs_nimmt.card import SechsNimmtCard as Card
from rlcard.games.sechs_nimmt.round import SechsNimmtRound as Round
from rlcard.games.sechs_nimmt.player import SechsNimmtPlayer as Player
from rlcard.games.sechs_nimmt.utils import (
    ACTION_LIST, TAKE_ROW_ACTIONS, DECK_SIZE, NUM_ACTIONS, NUM_ROWS, HAND_SIZE)


class TestSechsNimmtMethods(unittest.TestCase):

    def test_get_num_players(self):
        game = Game()
        self.assertEqual(game.get_num_players(), 4)

    def test_get_num_actions(self):
        game = Game()
        self.assertEqual(game.get_num_actions(), NUM_ACTIONS)
        self.assertEqual(NUM_ACTIONS, DECK_SIZE + NUM_ROWS)

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
        if game.round.pending_card is not None:
            # A too-low card was played: the same player must now take a row.
            self.assertEqual(next_player_id, player_id)
            self.assertEqual(game.get_legal_actions(), list(TAKE_ROW_ACTIONS))
        else:
            self.assertEqual(next_player_id, (player_id + 1) % game.get_num_players())

    def test_take_row_two_phase(self):
        # Build a round whose rows all have high tops, then play a low card so
        # the player is forced into the "take a row" decision.
        round_obj = Round.__new__(Round)
        round_obj.num_players = 2
        round_obj.current_player = 0
        round_obj.pending_card = None
        round_obj.board = [[Card(90)], [Card(91)], [Card(92)], [Card(93)]]
        players = [Player(0, None), Player(1, None)]
        players[0].hand = [Card(5)]

        # Phase 1: play the low card -> enters pending, turn does not advance
        round_obj.proceed_round(players, '5')
        self.assertIsNotNone(round_obj.pending_card)
        self.assertEqual(round_obj.current_player, 0)
        self.assertEqual(round_obj.get_legal_actions(players, 0), list(TAKE_ROW_ACTIONS))

        # Phase 2: take row 2 (top card 92, worth 1 bull)
        round_obj.proceed_round(players, 'take-2')
        self.assertIsNone(round_obj.pending_card)
        self.assertEqual(players[0].bulls, Card(92).bulls)
        self.assertEqual([c.number for c in round_obj.board[2]], [5])
        self.assertEqual(round_obj.current_player, 1)

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
