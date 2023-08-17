
from tqdm import tqdm
from numpy import argmax
import logging
import csv
from pathlib import Path

from Node import Node
from Game import Game
from GameConfig import GameConfig
from game_logic import play_game


def main(config: GameConfig):

    players_victory_count = {k: 0 for k in range(config.nb_players)}
    nb_games = config.nb_games

    node_root = None
    if config.mcts_type == 'puremcts':
        node_root = Node(
            parent=None)

    for _ in tqdm(range(nb_games)):
        game = Game(node_root=node_root, **vars(config))
        logging.info('Start game -------------------------------')
        play_game(game)

        if game.node_root is not None:
            node_root = game.node_root
            while game.node_current != game.node_root:
                game.node_current.incr_n_visits()
                if argmax(game.players_scores) == 1:
                    game.node_current.incr_won_games()
                game.node_current = game.node_current.get_parent()

        logging.info('End game -------------------------------')
        players_victory_count[argmax(game.players_scores)] += 1

    # ratios = {k: v / nb_games for k, v in players_victory_count.items()}
    # print(f"Victory ratios: {ratios}")

    # SAVE CONFIG AND RESULTS TO CSV
    is_write_header = True
    csv_name = config.csv_name
    if Path(csv_name).is_file():
        is_write_header = False
    try:
        csvfile = open(csv_name, mode='a', newline='')
        fieldnames = [
            'id_config', 'player_id', 'player_type',
            'nb_victories', 'is_cheater', 'nb_iters']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    except KeyError:
        csvfile = open(csv_name, mode='w', newline='')
        fieldnames = [
            'id_config', 'player_id', 'player_type',
            'nb_victories', 'is_cheater', 'nb_iters']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    if is_write_header:
        writer.writeheader()
    row = {}
    for i in range(game.nb_players):
        row['id_config'] = config.id_config
        row['player_id'] = i
        row['nb_victories'] = players_victory_count[i]
        row['player_type'] = config.player_id2type_player[i]
        if config.player_id2type_player[i] == 'mcts':
            row['is_cheater'] = config.player_id2is_cheater[i]
            row['nb_iters'] = config.player_id2nb_of_iterations[i]
        writer.writerow(row)


if __name__ == "__main__":
    if GameConfig.log_level == 'DEBUG':
        level = logging.DEBUG
    elif GameConfig.log_level == 'INFO':
        level = logging.INFO
    elif GameConfig.log_level == 'WARNING':
        level = logging.WARNING
    elif GameConfig.log_level == 'ERROR':
        level = logging.ERROR
    else:
        raise ValueError(
            'config error: log_level must have value in: '
            'DEBUG, INFO, WARNING, ERROR.')

    logging.basicConfig(filename='games.log', encoding='utf-8',
                        level=level)
    logging.debug('Start main.py -------------------------------')
    config = GameConfig
    main(config)
