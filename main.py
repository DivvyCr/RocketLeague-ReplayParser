import os
import sys

from boxcars_py import parse_replay

from replay_objects.replay import Replay

if __name__ == '__main__':
    replay_path = sys.argv[1]
    if not os.path.exists(replay_path):
        print("Invalid path!")
        sys.exit()

    with open(replay_path, "rb") as f:
        buf = f.read()
        f.close()

    boxcars_replay = parse_replay(buf)
    replay = Replay(boxcars_replay)
    replay.parse_replay() # Not the same function as the boxcars' one!

    players = replay.get_players()
    ball = replay.get_ball()
    game_info = replay.get_game_info()

    print(game_info.get_dataframe()
          .iloc[::10, :] # Every 10th entry (frame).
          .to_string())
