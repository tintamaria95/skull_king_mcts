
import random
import logging
from copy import deepcopy
from typing import List

from GameConfig import GameConfig
from Game import Game
from Node import Node
from Deck import Deck
from game_utils import (
    play_card, set_card_as_observed_by_player, get_score,
    replace_hands_of_other_players_depending_of_player_pov,
    get_index_winner_card,
    get_legal_moves)


def play_game(game: Game):
    assert game.game_round > 0 and game.game_round <= 10
    for _ in range(game.game_round, game.last_game_round + 1):
        init_round(game)
        play_round(game)
        game.game_round += 1


def init_round(game: Game):

    if not game.mode_playout:
        logging.debug(
            f'Init round {game.game_round} (deal cards)')
    # shuffle the deck
    deck = Deck()
    # gives each player a number of cards equal to the game round number
    game.players_cards = [
            deck.cards_to_draw[
                player_id * game.game_round:
                player_id * game.game_round + game.game_round
            ] for player_id in range(game.nb_players)]
    game.players_played_cards_indexes = [
        [False for _ in range(game.game_round)]
        for _ in range(game.nb_players)]
    game.players_observed_cards_in_round = [
        [0] * len(deck.cards_to_draw)
        for _ in range(game.nb_players)]
    game.players_pred_folds = [0 for _ in range(game.nb_players)]
    game.players_won_folds = [0] * game.nb_players
    game.chckpt_bid = 0
    game.chckpt_fold = 0
    game.chckpt_player_turn = 0

    # Players observe their cards
    for player_id in range(game.nb_players):
        for card in game.players_cards[player_id]:
            card_index = Deck.card2index[card]
            set_card_as_observed_by_player(game, card_index, player_id)

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
        logging.info(f'Round {game.game_round}')
        for player_id in range(game.nb_players):
            logging.info(
                f'SCORE Player {player_id};'
                f' folds: {game.players_won_folds[player_id]}'
                f'/{game.players_pred_folds[player_id]}'
                f' -> score: {game.players_scores[player_id]}')


def action_bid(game: Game, player_id: int):
    if game.player_id2type_player[player_id] == 'human' \
            and not game.mode_playout:
        bid_choice = ''
        while True:
            bid_choice = input(
                f'Choose bid (in range (0-{game.game_round}): ')
            if bid_choice.isnumeric():
                if int(bid_choice) in range(game.game_round + 1):
                    return int(bid_choice)
    elif game.player_id2type_player[player_id] == 'random' \
            or game.mode_playout:
        return random.randint(
            0, game.game_round)
    elif game.player_id2type_player[player_id] == 'mcts':
        return mcts(game=game, player_id=player_id, phase='bid')
    else:
        raise ValueError(
            f"Type of player {player_id} = "
            "{game.player_id2type_player[player_id]}."
            "Player type must be in 'random', 'human' or 'mcts'.")


def action_choose_card(game: Game, player_id: int, legal_moves: List[int]):
    if game.player_id2type_player[player_id] == 'human' \
            and not game.mode_playout:
        card_choice = ''
        while True:
            card_choice = input(
                f'Choose card (in range (0-{game.game_round}): ')
            try:
                if int(card_choice) in legal_moves:
                    return int(card_choice)
            except ValueError:
                logging.debug(f"Invalid card  choice: {card_choice}")
    elif (game.player_id2type_player[player_id] == 'mcts' or
            GameConfig.mcts_type == 'puremcts') and \
            not game.mode_playout:
        return mcts(game=game, player_id=player_id,
                    legal_moves=legal_moves, phase='play_card')
    elif game.player_id2type_player[player_id] == 'random' \
            or game.mode_playout:
        return random.choice(legal_moves)
    else:
        raise ValueError(
            f"Type of player {player_id} = "
            f"{game.player_id2type_player[player_id]}."
            "Player type must be in 'random', 'human' or 'mcts'.")


def mcts(game: Game, player_id: int, legal_moves=None, phase=None):
    if GameConfig.mcts_type == 'flatmc':
        return flatmc(game, player_id, legal_moves, phase)
    elif GameConfig.mcts_type == 'puremcts':
        return puremcts(game, player_id, legal_moves, phase)
    else:
        raise ValueError(
            'config error: mcts_type must has value in: '
            '["flatmc", "puremcts"]')


def flatmc(game: Game, player_id: int, legal_moves=None, phase=None):
    '''
    Monte Carlo algoritmh for next move to play prediction.
    The algorithm gives each legal move the same credit of iterations.
    It creates a copy of the game to simulate the following:
    It plays a legal move and choose randomly (playouts) each next play
    until the end of the game (terminal state) and save the result of the game.
    Once each legal move has been tried, it selects the move which gives back
    the most victories.
    '''
    if phase == 'bid':
        legal_moves = range(game.game_round + 1)
    best_sum_scores = - 1e6
    for move in legal_moves:
        sum_scores = 0
        for _ in range(game.player_id2nb_of_iterations[player_id]
                       // len(legal_moves)):
            chckpt_game = deepcopy(game)
            # Defines if mcts plays with hidden information or not
            if not game.player_id2is_cheater[player_id]:
                replace_hands_of_other_players_depending_of_player_pov(
                    chckpt_game, player_id)
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


def puremcts(game: Game, player_id: int, legal_moves=None, phase=None):

    # in bid phase, set legal_moves
    if phase == 'bid':
        legal_moves = range(game.game_round + 1)
    # Option 1, current node has chlid(ren), leaf not reached
    if game.node_current.is_has_child_node():
        # no constraint on bid choice
        if phase == 'bid':
            chosen_move = random.choices(
                population=legal_moves,
                weights=[
                    x.get_weight()
                    for x in game.node_current.get_children()],
                k=1
            )
            move = chosen_move[0]
            game.node_current = game.node_current.get_children()[move]
        # possible constraint on card choice
        elif phase == 'play_card':
            # we consider duplicate cards as same action to play,
            # then we must must remove duplicate choices in legal_moves
            legal_moves_without_duplicates = [
                x for x in {
                    game.players_cards[player_id][move]: move
                    for move in legal_moves}.values()]
            # restrict the choice of nodes to the legal_moves
            playable_move = [
                x for i, x in enumerate(game.players_cards[player_id])
                if i in legal_moves_without_duplicates]

            chosen_move = random.choices(
                population=legal_moves_without_duplicates,
                weights=[
                    x.get_weight()
                    for x in game.node_current.get_children()
                    if x.get_move() in playable_move
                    ],
                k=1
            )
            move = chosen_move[0]
            game.node_current = [
                x for x in game.node_current.get_children()
                if x.get_move() == game.players_cards[player_id][move]][0]
        else:
            raise ValueError('incorrect phase type')

    # Option 2, new leaf nodes are created and one is chosen randomly
    else:
        # all next moves will be randomly played until terminal
        game.mode_playout = True
        chosen_move = random.choice(legal_moves)
        move = chosen_move
        if phase == 'play_card':
            # from index in hand to tuple card
            chosen_move = game.players_cards[player_id][chosen_move]

        if phase == 'bid':
            all_moves = range(game.game_round + 1)
        elif phase == 'play_card':
            # remove duplicates, 2 same cards are the same action
            # less states, faster convergence
            all_moves = list(set(Deck.cards_list))
        else:
            raise ValueError('incorrect phase type')

        for m in all_moves:
            child_node = Node(
                parent=game.node_current,
                move=m
                )
            if chosen_move == m:
                next_node = child_node
            game.node_current.add_child(child_node)
        game.node_current = next_node
    return move
