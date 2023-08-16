import random


class Deck():

    cards_list = [
        *[(number, color)
            for number in range(1, 14)
            for color in ('red', 'blue', 'yellow', 'black')],
        *[('escape', None)] * 6,
        *[('pirate', None)] * 5,
        *[('mermaid', None)] * 2,
        ('skull_king', None),
        # ('scary_mary', None)
    ]

    card2index = {card: i for i, card in enumerate(cards_list)}
    index2card: {i: card for i, card in enumerate(cards_list)}

    number_of_cards = len(cards_list)
    cards_to_draw = None

    def __init__(self) -> None:

        self.cards_to_draw = self.get_shuffled_deck()

    def get_shuffled_deck(self):
        return random.sample(self.cards_list, self.number_of_cards)
