class Player():
    _id = None
    cards = None
    predicted_folds = None
    won_folds = 0
    score = None

    def __init__(self, _id: int) -> None:
        self._id = _id
