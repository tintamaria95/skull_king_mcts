import random
from typing import List
import logging
from copy import deepcopy

from Deck import Deck


class Game():
    '''
    The number players must be defined by'nb_players'.
    (If no definition, the default number is 2)
    The type of players can be :
        - random (actions are chosen randmoly)
        - human (actions are asked by the console)
        - mcts (actions are chosen by the mcts algorithm),
    and must be defined by the parameter 'players_type', making the peers
    key-value 'type': List[player_index0, ...]
    '''
    nb_players = None
    # The player who play the first card at the beginning of a round changes
    # at each round.
    first_round_player = None
    # The player who won the previous fold
    first_player = None

    players_cards: List[str] = []
    players_pred_folds: List[str] = []
    players_won_folds: List[str] = []
    players_scores = []
    player_id2type_player = {}

    chosen_color = None
    fold_cards = []

    game_round = 1  # from 1 to 10

    # MCTS
    mode_playout = False
    chckpt_bid = 0
    chckpt_fold = 0
    chckpt_player_turn = 0
    nb_iterations_per_action = 100

    def __init__(self, game_round=1, nb_players=2, players=None,
                 players_type={'random': [0, 1], 'human': [], 'mcts': []}):
        assert nb_players == sum([len(x) for x in players_type.values()]), \
            ("param 'nb_players' must be equal to the number of"
             " players indexes defined in 'players_type'")
        assert all(v in range(nb_players)
                   for v in [
                       y for x in players_type.values() for y in x]), \
            ("Index values in 'players_type' must be"
             " >= 0 and < 'nb_players' (in range(nb_players))")

        self.nb_players = nb_players
        self.game_round = game_round
        self.first_round_player = random.randint(0, nb_players - 1)
        self.players_scores = [0 for _ in range(nb_players)]

        for t in ['random', 'human', 'mcts']:
            for player_id in players_type[t]:
                self.player_id2type_player[player_id] = t

    def get_score(self, predicted_wins, actual_wins):
        if predicted_wins == 0:
            if predicted_wins == actual_wins:
                return 10 * self.game_round
            else:
                return - 10 * self.game_round
        else:
            if predicted_wins == actual_wins:
                return 20 * predicted_wins
            else:
                return - 10 * abs(predicted_wins - actual_wins)

    def init_round(self):
        if not self.mode_playout:
            logging.debug(
                f'Init round {self.game_round} (deal cards)')
        # shuffle the deck
        deck = Deck()
        cards_to_draw = [[v, c, False] for (v, c) in deck.cards_to_draw]
        # gives each player a number of cards equal to the game round number
        self.players_won_folds = [0] * self.nb_players
        self.players_cards = [
                cards_to_draw[
                    player_id * self.game_round:
                    player_id * self.game_round + self.game_round
                ] for player_id in range(self.nb_players)]

        self.players_pred_folds = [0 for _ in range(self.nb_players)]
        self.chckpt_bid = 0
        self.chckpt_fold = 0
        self.chckpt_player_turn = 0

        if not self.mode_playout:
            for player_id in range(self.nb_players):
                logging.debug(
                    f'Cards player {player_id}:'
                    f'{self.players_cards[player_id]}')

    def action_bid(self, player_id: int):
        if self.player_id2type_player[player_id] == 'random' \
                or self.mode_playout:
            self.players_pred_folds[player_id] = random.randint(
                0, self.game_round)
        elif self.player_id2type_player[player_id] == 'mcts':
            self.players_pred_folds[player_id] = self.mcts_bid(player_id)
        elif self.player_id2type_player[player_id] == 'human':
            bid_choice = ''
            while not bid_choice.isnumeric():
                bid_choice = input(
                    f'Choose bid (in range (0-{self.game_round}): ')
                self.players_pred_folds[player_id] = int(bid_choice)
        else:
            raise ValueError(
                f"Type of player {player_id} = "
                "{self.player_id2type_player[player_id]}."
                "Player type must be in 'random', 'human' or 'mcts'.")

    def action_choose_card(self, player_id: int, legal_moves: List[int]):
        if self.player_id2type_player[player_id] == 'random' \
                or self.mode_playout:
            return random.choice(legal_moves)
        elif self.player_id2type_player[player_id] == 'mcts':
            return self.mcts_choose_card(player_id, legal_moves)
        elif self.player_id2type_player[player_id] == 'human':
            card_choice = ''
            while True:
                card_choice = input(
                    f'Choose bid (in range (0-{self.game_round}): ')
                try:
                    if int(card_choice) in legal_moves:
                        return int(card_choice)
                except ValueError:
                    logging.debug(f"Invalid card  choice: {card_choice}")
        else:
            raise ValueError(
                f"Type of player {player_id} = "
                f"{self.player_id2type_player[player_id]}."
                "Player type must be in 'random', 'human' or 'mcts'.")

    def mcts_bid(self, player_id: int):
        '''
        must make modifs for hidden cards
        '''
        legal_moves = range(self.game_round + 1)
        best_sum_scores = - 1e6
        for move in legal_moves:
            sum_scores = 0
            for _ in range(self.nb_iterations_per_action // len(legal_moves)):
                chckpt_game = deepcopy(self)
                chckpt_game.mode_playout = True
                chckpt_game.players_pred_folds[player_id] = move
                chckpt_game.chckpt_bid += 1
                chckpt_game.play_round()
                sum_scores += chckpt_game.players_scores[player_id]
            if sum_scores > best_sum_scores:
                best_sum_scores = sum_scores
                best_move = move
        return best_move

    def mcts_choose_card(self, player_id: int, legal_moves: List[int]):
        '''
        must make modifs for hidden cards
        '''
        best_sum_scores = - 1e6
        for move in legal_moves:
            sum_scores = 0
            for _ in range(self.nb_iterations_per_action // len(legal_moves)):
                chckpt_game = deepcopy(self)
                chckpt_game.mode_playout = True
                chckpt_game.play_chosen_card(player_id=player_id, action=move)
                chckpt_game.chckpt_player_turn += 1
                chckpt_game.play_round()
                sum_scores += chckpt_game.players_scores[player_id]
            if sum_scores > best_sum_scores:
                best_sum_scores = sum_scores
                best_move = move
        return best_move

    def get_legal_moves(self, player_id: int):
        is_chosen_color_in_player_cards = self.chosen_color in [
            card[1] for card in self.players_cards[player_id]
            if not card[2]]
        # A player must follow the color of the round if he can
        # 'black' and special cards are not concerned.
        if self.chosen_color not in ['black', None] and \
                is_chosen_color_in_player_cards:
            return [
                i for i, card in enumerate(self.players_cards[player_id])
                # special cards can be played instead of chosen_color
                if (card[1] == self.chosen_color or card[1] is None)
                and not card[2]]
        else:
            return [
                i for i, card in enumerate(self.players_cards[player_id])
                if not card[2]]

    def play_chosen_card(self, *, player_id: int, action: int):
        self.players_cards[player_id][action][2] = True  # set as played
        chosen_card = self.players_cards[player_id][action]
        self.fold_cards.append(chosen_card)

        # Set the color for the fold if not already set
        if self.chosen_color is None:
            if str(chosen_card[0]).isnumeric():
                self.chosen_color = chosen_card[1]  # numbered card
            elif chosen_card[0] in [
                    'pirate', 'mermaid', 'scary_mary', 'skull_king']:
                self.chosen_color = 'incolor'  # No mandatory color
            elif chosen_card[0] == 'escape':
                self.chosen_color = None  # No change, maybe next cards
            else:
                raise ValueError('Logic problem')

    def play_round(self):
        # The first player to play at the beginning of the round
        # changes at each round
        self.first_player = self.first_round_player % (self.nb_players)
        if not self.mode_playout:
            logging.debug(f'Start round {self.game_round}')
        # Phase 1: Bid
        for player_id in range(self.chckpt_bid, self.nb_players):
            self.chckpt_bid = player_id
            self.action_bid(player_id)
            if not self.mode_playout:
                logging.debug(
                    f'Prediction player {player_id}:'
                    f' {self.players_pred_folds[player_id]}')
        # Phase 2: Play cards and save score
        for i_fold in range(self.chckpt_fold, self.game_round):
            self.chckpt_fold = i_fold
            if not self.mode_playout:
                logging.debug(
                    f'Fold {i_fold + 1}: '
                    f'First player: {self.first_player}')
            self.chosen_color = None
            self.fold_cards = []
            for i_turn in range(self.chckpt_player_turn, self.nb_players):
                self.chckpt_player_turn = i_turn
                turn = (self.first_player + i_turn) % (self.nb_players)
                legal_moves = self.get_legal_moves(turn)
                # ACTION
                action = self.action_choose_card(turn, legal_moves)
                self.play_chosen_card(player_id=turn, action=action)

            # Check who wins the fold
            if not self.mode_playout:
                logging.debug(
                    f'Played cards: {self.fold_cards}')
            player_who_won = (
                self.first_player +
                get_index_winner_card(self.fold_cards)) % (self.nb_players)
            # set the winner as the first player for next fold
            self.first_player = player_who_won
            if not self.mode_playout:
                logging.debug(
                    f'Fold winner: {player_who_won}')
            self.players_won_folds[player_who_won] += 1
        # Calculate the score for each player and save
        self.players_scores = [self.players_scores[player_id] + self.get_score(
            predicted_wins=self.players_pred_folds[player_id],
            actual_wins=self.players_won_folds[player_id]
        ) for player_id in range(self.nb_players)]
        self.first_round_player += 1
        if not self.mode_playout:
            for player_id in range(self.nb_players):
                logging.debug(
                    f'SCORE Player {player_id};'
                    f' folds: {self.players_won_folds[player_id]}'
                    f'/{self.players_pred_folds[player_id]}'
                    f' -> score: {self.players_scores[player_id]}')
            logging.debug(f'End round {self.game_round}')

    def play_game(self):
        assert self.game_round > 0 and self.game_round <= 10
        for _ in range(self.game_round, 11):
            self.init_round()
            self.play_round()
            self.game_round += 1


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
            is_all_escape = True
            for card in fold_cards:
                if card[1] is not None:
                    is_all_escape = False
                    chosen_color = card[1]
                    max_value = card[0]
            if is_all_escape:
                return 0
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
        'nb_players': 2,
        'game_round': 1,
        # 'players_type': {
        #     'random': [0],
        #     'mcts': [1],
        #     'human': []
        # }
    }

    game = Game(**args)
    # game.init_round()
    # game.play_round()
    game.play_game()

    logging.info('Game ended')
