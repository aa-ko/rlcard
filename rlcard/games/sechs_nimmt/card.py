class SechsNimmtCard:
    ''' A single card in Sechs Nimmt (6 nimmt!).

    A card is identified by its number (1-104). Every card is worth a
    number of "bull heads" (Hornochsen), which count as penalty points:

        * 55                      -> 7 bulls
        * multiples of 11         -> 5 bulls
        * multiples of 10         -> 3 bulls
        * numbers ending in 5     -> 2 bulls
        * everything else         -> 1 bull
    '''

    def __init__(self, number):
        ''' Initialize a card.

        Args:
            number (int): The face number of the card (1-104)
        '''
        self.number = number
        self.bulls = self.get_bulls(number)

    @staticmethod
    def get_bulls(number):
        ''' Compute the number of bull heads (penalty) of a card number.

        Args:
            number (int): The face number of the card (1-104)

        Returns:
            (int): The number of bull heads
        '''
        if number == 55:
            return 7
        if number % 11 == 0:
            return 5
        if number % 10 == 0:
            return 3
        if number % 5 == 0:
            return 2
        return 1

    def get_str(self):
        ''' Get the string representation of the card, e.g. ``'55'``.

        Returns:
            (str): The face number as a string
        '''
        return str(self.number)

    def __str__(self):
        return '%d (%d)' % (self.number, self.bulls)
