class GameConfig():
    # GLOBAL
    nb_games = 5
    log_level = 'INFO'  # DEBUG, INFO, WARNING, ERROR

    # PLAYERS
    # Players config, nb_players and players_type must be consistent
    nb_players = 2
    # Indicate the index of each player in range [0, ..., nb_players - 1]
    players_type = {
            'random': [0],
            'mcts': [1],
            'human': []
    }

    # NUMBER OF ROUNDS
    # An usual game has 10 rounds (below parameters might not be changed)
    first_game_round = 1
    last_game_round = 10

    # MCTS
    mcts_type = 'flatmc'  # available choices:
    # - flatmc
    # - puremcts
    nb_iters_per_action = 20
    # if True, mcts has all informations on the game (see players' hands)
    # else, mcts with hidden information (PIMC)
    is_mcts_cheater = False
