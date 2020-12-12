from boxcars_py import parse_replay

from replay_objects.replay import Replay

with open("replays/BFB0F4B611EB17CB17D5629553218CFC.replay", "rb") as f:
    buf = f.read()
    f.close()

replay = Replay(parse_replay(buf))
replay.parse_replay()
