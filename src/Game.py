import random
from typing import List
import logging

from Player import Player
from Deck import Deck


class Game():
    nb_players = None
    players: List[Player] = []
    first_player = None

    game_round = 1  # from 1 to 10

    def __init__(self, game_round=1, game_phase=0, nb_players=2):
        self.nb_players = nb_players
        for player_id in range(nb_players):
            player = Player(player_id)
            self.players.append(player)
        self.game_round = game_round
        self.game_phase = game_phase
        self.first_player = random.randint(0, nb_players - 1)

    def get_score(self, predicted_wins, actual_wins):
        if predicted_wins == 0:
            if predicted_wins == actual_wins:
                return 10 * self.game_round
            else:
                return - 10 * self.game_round
        else:
            if predicted_wins == actual_wins:
                return 10 * predicted_wins
            else:
                return - 10 * abs(predicted_wins - actual_wins)

    def play_round(self):
        logging.debug(f'Start round {self.game_round}')
        # shuffle the deck
        deck = Deck()
        cards_to_draw = deck.cards_to_draw
        # gives each player a number of cards equal to the game round number
        for player in self.players:
            player.won_folds = 0
            player.cards = cards_to_draw[
                player._id * self.game_round:
                player._id * self.game_round + self.game_round
                ]
            logging.debug(
                f'Cards player {player._id}: {player.cards}')
            # Each card has tags (number, color, is_played)
            player.cards = [[n, c, False] for (n, c) in player.cards]
        # Phase 1: Bid
        for player in self.players:
            # ACTION
            player.predicted_folds = random.randint(0, self.game_round)
            logging.debug(
                f'Prediction player {player._id}: {player.predicted_folds}')
        # Phase 2: Play cards
        for i_round in range(self.game_round):
            logging.debug(
                f'Fold {i_round + 1}: '
                f'First player: {self.first_player}')
            chosen_color = None
            fold_cards = []
            for i_player in range(self.nb_players):
                turn = (self.first_player + i_player) % (self.nb_players)
                is_chosen_color_in_player_cards = chosen_color in [
                        card[1] for card in self.players[turn].cards
                        if not card[2]]
                # A player must follow the color of the round if he can
                # 'black' and special cards are not concerned.
                if chosen_color not in ['black', None] and \
                        is_chosen_color_in_player_cards:
                    legal_moves = [
                        i for i, card in enumerate(self.players[turn].cards)
                        if card[1] == chosen_color and not card[2]]
                else:
                    legal_moves = [
                        i for i, card in enumerate(self.players[turn].cards)
                        if not card[2]]
                # ACTION
                action = random.choice(legal_moves)
                chosen_card = self.players[turn].cards[action]

                fold_cards.append(chosen_card)
                chosen_card[2] = True  # set as played

                # Set the color for the fold if not already set
                if chosen_color is None:
                    if str(chosen_card[0]).isnumeric():
                        chosen_color = chosen_card[1]  # numbered card
                    elif chosen_card[0] in [
                            'pirate', 'mermaid', 'scary_mary', 'skull_king']:
                        chosen_color = 'incolor'  # No mandatory color
                    elif chosen_card[0] == 'escape':
                        chosen_color = None  # No change, wait for future color
                    else:
                        raise ValueError('Logic problem')
            # Check who wins the fold
            logging.debug(
                f'Played cards: {fold_cards}')
            player_who_won = (
                self.first_player +
                get_index_winner_card(fold_cards)) % (self.nb_players)
            # set the winner as the first player for next fold
            self.first_player = player_who_won
            logging.debug(
                f'Fold winner: {player_who_won}')
            self.players[player_who_won].won_folds += 1
        # Calculate the score for each player and save
        for player in self.players:
            player.score = self.get_score(
                predicted_wins=player.predicted_folds,
                actual_wins=player.won_folds
            )
            logging.debug(
                f'SCORE Player {player._id};'
                f' folds: {player.won_folds}/{player.predicted_folds}'
                f' -> score: {player.score}')
        logging.debug(f'End round {self.game_round}')


def get_index_winner_card(fold_cards: list):
    # Case with no special cards:
    if not any([True for card in fold_cards
                if card[0] in [
                    'pirate', 'mermaid', 'scary_mary', 'skull_king']]):
        # Case if only red, yellow, blue AND black (and escape)
        if any([True for card in fold_cards if card[1] == 'black']):
            max_value = -1
            for i, card in enumerate(fold_cards):
                if card[1] == 'black' and card[0] > max_value:
                    index_best_card = i
                    max_value = card[0]
            return index_best_card
        # Case if only colors red, yellow, blue (and escape)
        elif all([True for card in fold_cards
                  if card[1] in ['red', 'yellow', 'blue'] or
                  card[0] == 'escape']):
            chosen_color = fold_cards[0][1]
            max_value = fold_cards[0][0]
            index_best_card = 0
            for i, card in enumerate(fold_cards):
                if card[1] == chosen_color and card[0] > max_value:
                    index_best_card = i
                    max_value = card[0]
            return index_best_card
        else:
            raise ValueError(
                'Logic problem. No special cards, no only-colours,'
                'no colours with black')
    # Case with special cards, handle win card by card
    else:
        winning_card = None
        winning_index = 0
        for i, card in enumerate(fold_cards):

            # TEMPORARY CONDITION
            if card[0] == 'scary_mary':
                raise ValueError('scary_mary effect not implemented yet')

            if str(card[0]).isnumeric() or card[0] == 'escape':
                continue  # No declare number as winning card bc special cards
            elif (card[0] in ['pirate', 'mermaid', 'scary_mary', 'skull_king']
                    and winning_card is None):
                winning_card = card[0]
                winning_index = i
            elif (card[0] == 'skull_king' and winning_card == 'pirate'):
                winning_card = card[0]
                winning_index = i
            elif (card[0] == 'mermaid' and winning_card == 'skull_king'):
                winning_card = card[0]
                winning_index = i
            elif (card[0] == 'pirate' and winning_card == 'mermaid'):
                winning_card = card[0]
                winning_index = i
            elif (card[0] in ['pirate', 'mermaid', 'scary_mary', 'skull_king']
                    and winning_card is not None):
                # other associations as "pirate on pirate", "pirate on sk",
                # or "mermaid on pirate" or "mermaid on mermaid" is no change
                continue
            else:
                raise ValueError('Logic problem')
        return winning_index


if __name__ == "__main__":

    logging.basicConfig(filename='games.log', encoding='utf-8',
                        level=logging.DEBUG)
    logging.info('New game started -------------------------------')

    args = {
        'nb_players': 5,
        'game_round': 5
    }

    game = Game(**args)
    game.play_round()
    logging.info('Game ended')
