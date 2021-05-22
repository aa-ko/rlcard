from rlcard.envs import Env
from rlcard.games.sechs_nimmt import Game



class SechsNimmtEnv(Env):

    def __init__(self, config):
        self.name = 'sechs-nimmt'
        self.game = Game()
        super().__init__(config)