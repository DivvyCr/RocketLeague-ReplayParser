from replay_parsing.actor_parsing.parse_car_components import *


def reformat_actions_to_bools(series):
    """
    Rocket League replays store player actions (jump, double jump and dodge) as cumulative integers:
      - odd values signify that the action is currently active;
      - even values signify that the action is currently inactive.

    This method fills NaN values with 0s (which will yield False in the result) and then transforms the series by
    taking the modulo of 2, which returns a series with only 0s and 1s. Lastly, it converts those to booleans.
    """
    series = series.fillna(0)
    return (series % 2).astype(bool)


def select_rename_true_values(series, name):
    """
    This method selects all True values (i.e. deletes all False values) and renames those to the given name.
    """
    series = series.loc[series]
    series.loc[series] = name
    return series


def reformat_player_action(action_series, action_name):
    """
    This method reduces the initial player action Series into (practically) an array of indices where the action was
    active - each index has the equivalent value action_name.

    The return value is used in combination with the other player actions to create a single action column in the player
    DataFrame.
    """
    action_active_series = reformat_actions_to_bools(action_series)
    action_active_series = select_rename_true_values(action_active_series, action_name)
    return action_active_series


def merge_player_action_columns(player):
    """
    This method replaces the individual Jump, DoubleJump and Dodge columns in the player DataFrame with a single
    column that provides the action active at a given frame by a string name (or NaN).

    Due to the nature of Rocket League's actions, they (realistically) cannot overlap - a Jump cannot be happening
    during a Dodge, etc. Therefore, this method combines the actions by overwriting Jump with DoubleJump and then
    overwriting with Dodge; lastly, when joined with the player DataFrame, the missing indices are filled with NaN.
    """
    player_dataframe = player.get_dataframe()

    # NOTE: .iloc[:, 0] selects the first column (which is NaN due to uneven MultiIndex levels)
    jump_active = player_dataframe['is_jump_active']
    jump_series = reformat_player_action(jump_active.iloc[:, 0], JumpParser.actor_type_short.lower())

    doublejump_active = player_dataframe['is_doublejump_active']
    doublejump_series = reformat_player_action(doublejump_active.iloc[:, 0], DoubleJumpParser.actor_type_short.lower())

    dodge_active = player_dataframe['is_dodge_active']
    dodge_series = reformat_player_action(dodge_active.iloc[:, 0], DodgeParser.actor_type_short.lower())
    # END NOTE.

    # Dodge overwrites DoubleJump overwrites Jump, but should be little to no overlap.
    # This order was chosen because dodge is more likely to require precise analysis than the jumps.
    player_actions = dodge_series.combine_first(doublejump_series.combine_first(jump_series))

    # Replace the individual action columns with a single column called 'action'.
    player_dataframe['action'] = player_actions
    del player_dataframe['is_jump_active']
    del player_dataframe['is_doublejump_active']
    del player_dataframe['is_dodge_active']


class DataFormatter:
    def __init__(self, players, ball, game_info):
        self.players = players
        self.ball = ball
        self.game_info = game_info

    def format_all_players(self):
        for player in self.players:
            self.format_player(player)

    def format_player(self, player):
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

        merge_player_action_columns(player)
