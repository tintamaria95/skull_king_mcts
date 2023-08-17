class GameConfig():
    # GLOBAL
    id_config = 0
    csv_name = './games.csv'
    nb_games = 1
    log_level = 'DEBUG'  # DEBUG, INFO, WARNING, ERROR

    # NUMBER OF ROUNDS
    # An usual game has 10 rounds (below parameters might not be changed)
    first_game_round = 1
    last_game_round = 10

    # PLAYERS
    nb_players = 2
    # key is player_id in range [0, ..., nb_players - 1],
    # value is player's type
    player_id2type_player = {
            0: 'random',
            1: 'mcts',
            2: 'mcts',
            # 3: 'human'
    }

    # (Not need to attribute values to 'random' players)
    player_id2nb_of_iterations = {
        1: 15,
        2: 15
    }

    # if value is True, mcts has all informations on the game
    # (ie mcts sees players' hands) else,
    # mcts plays with hidden information (PIMC) and generates
    # possible hands of other players based on previous observed
    # informations (cards in hand and played cards in round).
    player_id2is_cheater = {
        1: True,
        2: False
    }

    # MCTS
    mcts_type = 'flatmc'  # available choices:
    # - flatmc
    # - puremcts - WARNING NOT FINISHED ! NOT REALLY USEABLE YET
