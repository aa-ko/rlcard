class SechsNimmtPlayer:
    ''' A Sechs Nimmt player. Holds a hand of cards and accumulates the bull
    heads (penalty points) collected during the game.
    '''

    def __init__(self, player_id, np_random):
        ''' Initialize a player.

        Args:
            player_id (int): The id of the player
            np_random (numpy.random.RandomState): The shared RNG
        '''
        self.np_random = np_random
        self.player_id = player_id
        self.hand = []
        self.bulls = 0

    def get_player_id(self):
        ''' Return the id of the player.

        Returns:
            (int): The player's id
        '''
        return self.player_id
