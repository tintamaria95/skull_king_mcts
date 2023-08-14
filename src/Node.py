from typing import List, Type


class Node():

    signature: str = ''

    won_games: int = 0
    n_visits: int = 0

    parent: Type['Node'] = None
    children: List[Type['Node']] = None

    def __init__(self, signature='', parent=None, won_games=0, n_visits=0):
        self.signature = signature
        self.parent = parent
        self.won_games = won_games
        self.n_visits = n_visits

    def incr_won_games(self):
        self.won_games += 1

    def incr_n_visits(self):
        self.n_visits += 1

    def get_parent_visits(self):
        return self.parent.n_visits

    def add_child(self, node: Type['Node']):
        self.children.append(node)
