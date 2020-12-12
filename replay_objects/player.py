from replay_objects.replay_object import ReplayObject


class Player(ReplayObject):
    unique_id = None

    names = None

    def __init__(self, unique_id):
        super().__init__()
        self.unique_id = unique_id

        self.names = []

    def get_unique_id(self):
        return self.unique_id

    def add_name(self, name):
        self.names.append(name)
