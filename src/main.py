
from tqdm import tqdm
from numpy import argmax
import logging

from Game import Game
from game_config import GameConfig
from game_logic import play_game


def main():

    cpt_victory = 0
    nb_games = GameConfig.nb_games
    for _ in tqdm(range(nb_games)):
        game = Game(**vars(GameConfig))
        logging.info('Start game -------------------------------')
        play_game(game)
        logging.info('End game -------------------------------')
        if argmax(game.players_scores) == 1:
            cpt_victory += 1

    print(f'victory ratio mcts on random: {cpt_victory / nb_games}')


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
    main()