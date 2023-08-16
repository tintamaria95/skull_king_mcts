from typing import Type, List


class Node():

    def __init__(
            self, parent: None | Type['Node'] = None, move=None,
            won_games=1, n_visits=1, is_terminal=False):
        self.parent = parent
        self.children: List[Node] = []
        self.move = move
        self.won_games = won_games
        self.n_visits = n_visits
        self.is_terminal = is_terminal

    def incr_won_games(self):
        self.won_games += 1

    def incr_n_visits(self):
        self.n_visits += 1

    def get_weight(self):
        return self.won_games / self.n_visits

    def get_parent(self):
        return self.parent

    def set_parent(self, parent: Type['Node']):
        self.parent = parent

    def get_move(self):
        return self.move

    def get_children(self):
        return self.children

    def add_child(self, node: Type['Node']):
        self.children.append(node)

    def is_has_child_node(self):
        return len(self.children) > 0
