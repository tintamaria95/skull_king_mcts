import random
from typing import List
from Node import Node


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

    # List of cards in the hand of each player.
    # Each card is a tuple: (card_value: int | str, color: str | None)
    players_cards = []
    # Lists of card indexes for each player.
    # 0: card not played in this round
    # 1: card already played in this round
    # example: [[0, 0, 1, 0], [0, 0, 0, 0]]]
    # -> 2 players, round 4, p1 played 3rd card
    players_played_cards_indexes = []
    # Keep track of observed cards (in hand and played) by each player
    # Possibility to only update mcts players (useless for others)
    players_observed_cards_in_round = []
    # Predictions of folds each player make for the round
    players_pred_folds: List[str] = []
    # Won folds of each player at the end of the round
    players_won_folds: List[str] = []
    players_scores = []
    player_id2nb_of_iterations = {}
    player_id2type_player = {}
    player_id2is_cheater = {}

    # The chosen color during a fold
    chosen_color = None
    fold_cards = []
    # Keep track of information (owned or played cards) that mcts players
    # should have  of the game and build a list of the cards which still
    # have to be played.
    # The list is completed when the player receives cards and when an other
    # player plays a card.
    # (We note that whole deck card is shuffled between each of the 10 rounds)
    # Works as followed -> [[1, 'red'], [2, 'blue'], ...]

    # possible_remaining_cards_in_deck_by_pov = []  #

    game_round = 1  # from 1 to 10

    # MCTS
    mode_playout = False
    chckpt_bid = 0
    chckpt_fold = 0
    chckpt_player_turn = 0
    nb_iters_per_action = 20

    node_root: Node
    node_current: Node

    def __init__(self, node_root=None, **args):

        self.nb_players = args['nb_players']
        assert args['first_game_round'] <= args['last_game_round']
        self.game_round = args['first_game_round']
        self.last_game_round = args['last_game_round']
        self.first_round_player = random.randint(0, args['nb_players'] - 1)
        self.players_scores = [0 for _ in range(args['nb_players'])]

        self.player_id2type_player = args['player_id2type_player']
        self.player_id2nb_of_iterations = args['player_id2nb_of_iterations']
        self.player_id2is_cheater = args['player_id2is_cheater']

        self.node_root = node_root
        self.node_current = self.node_root
