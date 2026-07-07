class SechsNimmtJudger:
    ''' Judge the outcome of a Sechs Nimmt game. The winner(s) are the
    player(s) that collected the fewest bull heads.
    '''

    @staticmethod
    def judge_winner(players):
        ''' Determine the winner(s) of the game.

        Args:
            players (list): The list of ``SechsNimmtPlayer`` objects

        Returns:
            (list): The player id(s) with the fewest bull heads
        '''
        min_bulls = min(player.bulls for player in players)
        return [player.player_id for player in players if player.bulls == min_bulls]
