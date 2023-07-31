import random


class Deck():

    cards_to_draw = None

    def __init__(self) -> None:

        self.cards_list = [
            *[(number, color)
                for number in range(1, 13)
                for color in ['red', 'blue', 'yellow', 'black']],
            *[('escape', None)] * 6,
            *[('pirate', None)] * 5,
            *[('mermaid', None)] * 2,
            ('skull_king', None),
            # ('scary_mary', None)
        ]
        self.number_of_cards = len(self.cards_list)
        self.cards_to_draw = self.get_shuffled_deck()

    def get_shuffled_deck(self):
        return random.sample(self.cards_list, self.number_of_cards)
