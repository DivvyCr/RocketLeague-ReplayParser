import logging
import time
from enum import Enum

import pandas
from replay_parsing.actor_parser import ActorParser
from replay_parsing.data_formatter import DataFormatter

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ReplayProperties(Enum):
    BUILD_ID = 'BuildID'
    BUILD_VERSION = 'BuildVersion'
    REPLAY_DATE = 'Date'
    GAME_VERSION = 'GameVersion'
    GOALS = 'Goals'
    HIGHLIGHTS = 'HighLights'
    REPLAY_ID = 'Id'
    MAP_NAME = 'MapName'
    MATCH_TYPE = 'MatchType'
    NUM_FRAMES = 'NumFrames'
    OWNER_NAME = 'PlayerName'
    PLAYER_STATS = 'PlayerStats'
    RECORD_FPS = 'RecordFPS'
    REPLAY_NAME = 'ReplayName'
    REPLAY_VERSION = 'ReplayVersion'
    TEAM0_SCORE = 'Team0Score'
    TEAM1_SCORE = 'Team1Score'
    TEAM_SIZE = 'TeamSize'
# Also these: 'Changelist', 'KeyframeDelay', 'MaxChannels', 'MaxReplaySizeMB', 'ReplayLastSaveVersion',
# 'ReserveMegabytes', 'UnfairTeamSize'


class Replay:
    """
    The Replay class can parse and present all replay data in a manageable format.
    """

    def __init__(self, replay):
        """
        :param replay: The return of the parsed .replay file form boxcars-py.
        """
        self.replay = replay

        replay_properties = self.replay['properties']

        self.id = replay_properties.get(ReplayProperties.REPLAY_ID.value, None)
        self.name = replay_properties.get(ReplayProperties.REPLAY_NAME.value, None)
        self.owner_name = replay_properties.get(ReplayProperties.OWNER_NAME.value, None)
        self.date = replay_properties.get(ReplayProperties.REPLAY_DATE.value, None)

        self.total_frames = replay_properties.get(ReplayProperties.NUM_FRAMES.value, None)
        self.record_fps = replay_properties.get(ReplayProperties.RECORD_FPS.value, None)

        self.team_size = replay_properties.get(ReplayProperties.TEAM_SIZE.value, None)
        self.match_score = {'Team 0': replay_properties.get(ReplayProperties.TEAM0_SCORE.value, -1),
                            'Team 1': replay_properties.get(ReplayProperties.TEAM1_SCORE.value, -1)}
        self.match_goals = replay_properties.get(ReplayProperties.GOALS.value, None)
        self.match_player_stats = replay_properties.get(ReplayProperties.PLAYER_STATS.value, None)

        self.players = None
        self.ball = None
        self.game_info = None

    def parse_replay(self):
        logger.info("Started parsing...")
        t1 = time.time()

        replay_frames = self.replay['network_frames']['frames']

        actor_parser = ActorParser(replay_frames, self.replay['objects'], self.replay['names'])
        actor_parser.parse_actors_from_replay_frames()  # Frame-by-frame, raw actor data.

        t2 = time.time()
        logger.info("Parsing complete in %ss!" % str(round(t2-t1, 3)))

        self.players = actor_parser.get_players()
        self.ball = actor_parser.get_ball()
        self.game_info = actor_parser.get_game_info()

        data_formatter = DataFormatter()
        for player in self.players:
            data_formatter.format_player_dataframe(player)

    def get_players(self):
        return self.players

    def get_ball(self):
        return self.ball

    def get_game_info(self):
        return self.game_info
