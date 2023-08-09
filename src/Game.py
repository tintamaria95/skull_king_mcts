import random
from typing import List
import logging
from copy import deepcopy
from tqdm import tqdm
from numpy import argmax

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

    # The chosen color during a fold
    chosen_color = None
    fold_cards = []
    # Keep track of information (owned or played cards) that mcts player
    # should have  of the game and build a list of the cards which still
    # have to be played.
    # The list is completed whenn the player receives cards and when an other
    # player plays a card.
    # (We note that whole deck card is shuffled between each of the 10 rounds)
    possible_remaining_cards_in_deck = []

    game_round = 1  # from 1 to 10

    # MCTS
    mode_playout = False
    chckpt_bid = 0
    chckpt_fold = 0
    chckpt_player_turn = 0
    nb_iters_per_action = 20

    def __init__(self, game_round=1, nb_players=2, players=None,
                 players_type={'random': [0, 1], 'human': [], 'mcts': []},
                 nb_iters_per_action=20):
        assert nb_players == sum([len(x) for x in players_type.values()]), \
            ("param 'nb_players' must be equal to the number of"
             " players indexes defined in 'players_type'")
        assert all(v in range(nb_players)
                   for v in [
                       y for x in players_type.values() for y in x]), \
            ("Index values in 'players_type' must be"
             " >= 0 and < 'nb_players' (in range(nb_players))")

        self.nb_players = nb_players
        self.nb_iters_per_action = nb_iters_per_action
        self.game_round = game_round
        self.first_round_player = random.randint(0, nb_players - 1)
        self.players_scores = [0 for _ in range(nb_players)]

        for t in ['random', 'human', 'mcts']:
            for player_id in players_type[t]:
                self.player_id2type_player[player_id] = t


def get_score(game: Game, predicted_wins, actual_wins):
    if predicted_wins == 0:
        if predicted_wins == actual_wins:
            return 10 * game.game_round
        else:
            return - 10 * game.game_round
    else:
        if predicted_wins == actual_wins:
            return 20 * predicted_wins
        else:
            return - 10 * abs(predicted_wins - actual_wins)


def action_bid(game: Game, player_id: int):
    if game.player_id2type_player[player_id] == 'random' \
            or game.mode_playout:
        return random.randint(
            0, game.game_round)
    elif game.player_id2type_player[player_id] == 'mcts':
        return mcts(game=game, player_id=player_id, phase='bid')
    elif game.player_id2type_player[player_id] == 'human':
        bid_choice = ''
        while True:
            bid_choice = input(
                f'Choose bid (in range (0-{game.game_round}): ')
            if bid_choice.isnumeric():
                if int(bid_choice) in range(game.game_round + 1):
                    return int(bid_choice)
    else:
        raise ValueError(
            f"Type of player {player_id} = "
            "{game.player_id2type_player[player_id]}."
            "Player type must be in 'random', 'human' or 'mcts'.")


def action_choose_card(game: Game, player_id: int, legal_moves: List[int]):
    if game.player_id2type_player[player_id] == 'random' \
            or game.mode_playout:
        return random.choice(legal_moves)
    elif game.player_id2type_player[player_id] == 'mcts':
        return mcts(game=game, player_id=player_id,
                    legal_moves=legal_moves, phase='play_card')
    elif game.player_id2type_player[player_id] == 'human':
        card_choice = ''
        while True:
            card_choice = input(
                f'Choose bid (in range (0-{game.game_round}): ')
            try:
                if int(card_choice) in legal_moves:
                    return int(card_choice)
            except ValueError:
                logging.debug(f"Invalid card  choice: {card_choice}")
    else:
        raise ValueError(
            f"Type of player {player_id} = "
            f"{game.player_id2type_player[player_id]}."
            "Player type must be in 'random', 'human' or 'mcts'.")


def get_legal_moves(game: Game, player_id: int):
    is_chosen_color_in_player_cards = game.chosen_color in [
        card[1] for card in game.players_cards[player_id]
        if not card[2]]
    # A player must follow the color of the round if he can
    # 'black' and special cards are not concerned.
    if game.chosen_color not in ['black', None] and \
            is_chosen_color_in_player_cards:
        return [
            i for i, card in enumerate(game.players_cards[player_id])
            # special cards can be played instead of chosen_color
            if (card[1] == game.chosen_color or card[1] is None)
            and not card[2]]
    else:
        return [
            i for i, card in enumerate(game.players_cards[player_id])
            if not card[2]]


def get_randomly_generated_players_hands(game: Game):
    '''
    Skull King is a Hidden information game, this function replaces
    the actual hands of other players by 'possible' hands they may
    have, based on the 'possible_remaining_cards_in_deck' Game class
    variable.
    It simulates the fact that we shouldn't have information of other
    players hands.
    '''
    pass


def mcts(game: Game, player_id: int, legal_moves=None, phase=None):
    '''
    '''
    if phase == 'bid':
        legal_moves = range(game.game_round + 1)
    best_sum_scores = - 1e6
    for move in legal_moves:
        sum_scores = 0
        for _ in range(game.nb_iters_per_action // len(legal_moves)):
            chckpt_game = deepcopy(game)
            assert not chckpt_game.mode_playout, \
                ('logic error, should not already be in mode_playout')
            chckpt_game.mode_playout = True
            if phase == 'bid':
                chckpt_game.players_pred_folds[player_id] = move
            elif phase == 'play_card':
                play_card(chckpt_game, player_id=player_id, action=move)
            else:
                raise ValueError(
                    f"'phase: {phase}'"
                    "Parameter 'phase must have been set to 'bid' or"
                    "'play_card'.")
            play_round(chckpt_game)
            sum_scores += chckpt_game.players_scores[player_id]
        if sum_scores > best_sum_scores:
            best_sum_scores = sum_scores
            best_move = move
    return best_move


def play_card(game: Game, player_id, action: int):

    game.players_cards[player_id][action][2] = True  # set as played
    chosen_card = game.players_cards[player_id][action]
    game.fold_cards = [x for x in game.fold_cards]
    game.fold_cards.append(chosen_card)

    # Set the color for the fold if not already set
    if game.chosen_color is None:
        if str(chosen_card[0]).isnumeric():
            game.chosen_color = chosen_card[1]  # numbered card
        elif chosen_card[0] in [
                'pirate', 'mermaid', 'scary_mary', 'skull_king']:
            game.chosen_color = 'incolor'  # No mandatory color
        elif chosen_card[0] == 'escape':
            game.chosen_color = None  # No change, maybe next cards
        else:
            raise ValueError('Logic problem')


def init_round(game: Game):

    if not game.mode_playout:
        logging.debug(
            f'Init round {game.game_round} (deal cards)')
    # shuffle the deck
    deck = Deck()
    cards_to_draw = [[v, c, False] for (v, c) in deck.cards_to_draw]
    # keep track of cards which have not been already played
    game.possible_remaining_cards_in_deck = [x.copy() for x in cards_to_draw]
    # gives each player a number of cards equal to the game round number
    game.players_won_folds = [0] * game.nb_players
    game.players_cards = [
            cards_to_draw[
                player_id * game.game_round:
                player_id * game.game_round + game.game_round
            ] for player_id in range(game.nb_players)]

    game.players_pred_folds = [0 for _ in range(game.nb_players)]
    game.chckpt_bid = 0
    game.chckpt_fold = 0
    game.chckpt_player_turn = 0

    if not game.mode_playout:
        for player_id in range(game.nb_players):
            logging.debug(
                f'Cards player {player_id}:'
                f'{game.players_cards[player_id]}')


def play_round(game: Game):

    # The first player to play at the beginning of the round
    # changes at each round
    game.first_player = game.first_round_player % (game.nb_players)
    if not game.mode_playout:
        logging.debug(f'Start round {game.game_round}')
    # Phase 1: Bid
    for player_id in range(game.chckpt_bid, game.nb_players):
        game.chckpt_bid = player_id + 1
        game.players_pred_folds[player_id] = action_bid(game, player_id)
        if not game.mode_playout:
            logging.debug(
                f'Prediction player {player_id}:'
                f' {game.players_pred_folds[player_id]}')

    # Phase 2: Play cards and save score
    for i_fold in range(game.chckpt_fold, game.game_round):
        game.chckpt_fold = i_fold + 1
        if not game.mode_playout:
            logging.debug(
                f'Fold {i_fold + 1}: '
                f'First player: {game.first_player}')
        game.chosen_color = None
        for i_turn in range(game.chckpt_player_turn, game.nb_players):
            game.chckpt_player_turn = i_turn + 1
            turn = (game.first_player + i_turn) % (game.nb_players)
            legal_moves = get_legal_moves(game, turn)

            # ACTION
            action = action_choose_card(game, turn, legal_moves)
            # remove card of list of remaining cards to play
            game.possible_remaining_cards_in_deck.remove(
                game.players_cards[turn][action])
            play_card(game, turn, action)

        game.chckpt_player_turn = 0

        # Check who wins the fold
        if not game.mode_playout:
            logging.debug(
                f'Played cards: {game.fold_cards}')
        player_who_won = (
            game.first_player +
            get_index_winner_card(game.fold_cards)) % (game.nb_players)
        # set the winner as the first player for next fold
        game.first_player = player_who_won
        # empty the fold after getting winner
        game.fold_cards = []
        if not game.mode_playout:
            logging.debug(
                f'Fold winner: {player_who_won}')
        game.players_won_folds[player_who_won] += 1

    # Calculate the score for each player and save
    game.players_scores = [game.players_scores[player_id] + get_score(
        game=game, predicted_wins=game.players_pred_folds[player_id],
        actual_wins=game.players_won_folds[player_id]
    ) for player_id in range(game.nb_players)]
    # set the first player of the next round
    game.first_round_player = (game.first_round_player + 1) % (
        game.nb_players)
    if not game.mode_playout:
        for player_id in range(game.nb_players):
            logging.debug(
                f'SCORE Player {player_id};'
                f' folds: {game.players_won_folds[player_id]}'
                f'/{game.players_pred_folds[player_id]}'
                f' -> score: {game.players_scores[player_id]}')
        logging.debug(f'End round {game.game_round}')


def play_game(game: Game):
    assert game.game_round > 0 and game.game_round <= 10
    for _ in range(game.game_round, 11):
        init_round(game)
        play_round(game)
        game.game_round += 1


def get_index_winner_card(fold_cards: list):
    assert len(fold_cards) > 1
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
                if card[0] != 'escape':
                    is_all_escape = False
                    chosen_color = card[1]
                    max_value = card[0]
                    break
            if is_all_escape:
                # case if all cards are 'escape', first wins
                return 0
            index_best_card = 0
            for i, card in enumerate(fold_cards):
                if card[1] == chosen_color and card[0] >= max_value:
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
        'nb_iters_per_action': 10,
        'players_type': {
            'random': [0],
            'mcts': [1],
            'human': []
        }
    }

    cpt_victory = 0
    nb_games = 20
    for _ in tqdm(range(nb_games)):
        game = Game(**args)
        # game.init_round()
        # game.play_round()
        # game = play_game(game)
        play_game(game)

        logging.info('Game ended')

        if argmax(game.players_scores) == 1:
            cpt_victory += 1
    print(f'victory ratio mcts on random: {cpt_victory / nb_games}')
