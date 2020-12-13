class DataFormatter:
    def __init__(self):
        pass

    def format_player_dataframe(self, player):
        player_dataframe = player.get_dataframe()
        # TODO Create a ConfigParser that would provide variables to universally access columns in code?
        # Find all unique names that the player used in the game. Add them to the Player object.
        # Delete name column in the DataFrame.
        if 'name' in player_dataframe.columns:
            names = list(player_dataframe['name'].value_counts().to_dict().keys())
            for name in names:
                player.add_name(name[0])  # 'name' is a single-value tuple.
            del player_dataframe['name']

        # Find all indexes where the player's car was 'sleeping'.
        if 'is_sleeping' in player_dataframe.columns:
            is_sleeping_series = player_dataframe['is_sleeping'].iloc[:, 0]
            sleeping_idxs = is_sleeping_series[is_sleeping_series == True].index.to_list()
