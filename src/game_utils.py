import random

from Game import Game
from Deck import Deck


def play_card(game: Game, player_id, action: int):

    game.players_played_cards_indexes[player_id][action] = True
    chosen_card = game.players_cards[player_id][action]
    # when a card is played, all players observe it as played
    card_index = Deck.card2index[chosen_card]
    for player_id in range(game.nb_players):
        set_card_as_observed_by_player(
            game=game,
            card_index=card_index,
            player_id=player_id
        )
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


def set_card_as_observed_by_player(
        game: Game, card_index: int, player_id: int):
    game.players_observed_cards_in_round[player_id][card_index] = True


def get_legal_moves(game: Game, player_id: int):
    is_chosen_color_in_player_cards = game.chosen_color in [
        card[1] for i, card in enumerate(game.players_cards[player_id])
        if not game.players_played_cards_indexes[player_id][i]]
    # A player must follow the color of the round if he can
    # 'black' and special cards are not concerned.
    if game.chosen_color not in ['black', None] and \
            is_chosen_color_in_player_cards:
        return [
            i for i, card in enumerate(game.players_cards[player_id])
            # special cards can be played instead of chosen_color
            if (card[1] == game.chosen_color or card[1] is None)
            and not game.players_played_cards_indexes[player_id][i]]
    else:
        return [
            i for i, _ in enumerate(game.players_cards[player_id])
            if not game.players_played_cards_indexes[player_id][i]]


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


def get_randomly_generated_player_hand(game: Game, player_id: int):
    '''
    Skull King is a Hidden information game, this function allows
    to generate possible hands of other players based on the game class
    variable 'players_observed_cards_in_round'.
    This function can used by the mcts algorithm to do simulation as a
    non-cheater algorithm: this function "hides" the real hand of players
    to mcts while it is learning to play.
    parameter 'player_id' indicates from which player point of view we
    build randomly the hand.
    '''
    possible_remaining_card_indexes = [
        i for i, x in enumerate(
            game.players_observed_cards_in_round[player_id])
        if not x]
    selected_indexes = random.sample(
        possible_remaining_card_indexes, game.game_round)
    return [Deck().cards_list[i] for i in selected_indexes]


def replace_hands_of_other_players_depending_of_player_pov(
        game: Game, player_id: int):
    for p_id in range(game.nb_players):
        if player_id != p_id:
            game.players_cards[p_id] = get_randomly_generated_player_hand(
                game, player_id)
