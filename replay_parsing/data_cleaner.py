import pandas as pd


class DataCleaner:
    replay = None

    def __init__(self, replay):
        self.replay = replay

    def clean_replay(self):
        for p in self.replay.get_players():
            self.clean_player(p)

    def clean_player(self, player):
        player_dataframe = player.get_dataframe()

        # Find all unique names that the player used in the game. Add them to the Player object.
        # Delete name column in the DataFrame.
        names = list(player_dataframe['name'].value_counts().to_dict().keys())
        for name in names:
            player.add_name(name[0])  # 'name' is a single-value tuple.
        del player_dataframe['name']

        # Find all indexes where the player's car was 'sleeping'.
        # is_sleeping_series = player_dataframe['is_sleeping'].iloc[:, 0]
        # sleeping_idxs = is_sleeping_series[is_sleeping_series == True].index.to_list()

        # pd.set_option('max_rows', None)
        # pd.set_option('max_columns', None)
        # print(player_dataframe['location']['x'])
