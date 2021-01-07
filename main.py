from boxcars_py import parse_replay

from replay_objects.replay import Replay

if __name__ == '__main__':
    with open("replays/BFB0F4B611EB17CB17D5629553218CFC.replay", "rb") as f:
        buf = f.read()
        f.close()

    replay = Replay(parse_replay(buf))
    replay.parse_replay()

    players = replay.get_players()
    ball = replay.get_ball()
    game_info = replay.get_game_info()
