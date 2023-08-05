import random


class Deck():

    cards_to_draw = None
    card2index = {}
    index2card = {}

    def __init__(self) -> None:
        # False indicates that the card hasn't been played yet
        self.cards_list = [
            *[(number, color)
                for number in range(1, 13)
                for color in ('red', 'blue', 'yellow', 'black')],
            *[('escape', None)] * 6,
            *[('pirate', None)] * 5,
            *[('mermaid', None)] * 2,
            ('skull_king', None),
            # ('scary_mary', None)
        ]

        for i, card in enumerate(self.cards_list):
            self.card2index[card] = i
            self.index2card[i] = card

        self.number_of_cards = len(self.cards_list)
        self.cards_to_draw = self.get_shuffled_deck()

    def get_shuffled_deck(self):
        return random.sample(self.cards_list, self.number_of_cards)

    def get_cards_from_deck(nb_cards: int, cards_already_played: list):
        pass
