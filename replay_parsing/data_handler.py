import logging
import time

import pandas as pd

from replay_objects.ball import Ball
from replay_objects.game_info import GameInfo
from replay_objects.player import Player
from replay_parsing.actor_parsing.parse_ball import BallParser
from replay_parsing.actor_parsing.parse_car import CarParser
from replay_parsing.actor_parsing.parse_car_components.parse_boost import BoostParser
from replay_parsing.actor_parsing.parse_car_components.parse_dodge import DodgeParser
from replay_parsing.actor_parsing.parse_car_components.parse_double_jump import DoubleJumpParser
from replay_parsing.actor_parsing.parse_car_components.parse_jump import JumpParser
from replay_parsing.actor_parsing.parse_game import GameEventParser
from replay_parsing.actor_parsing.parse_player import PlayerParser
from replay_parsing.actor_parsing.parse_team import TeamParser


def reform_data(data: dict, depth: int = None, key_map: tuple = None, return_value: dict = None):
    """
    This method flattens the data dictionary into a new dictionary with the keys being tuples that map the 'path' to the
    value. See the example:
        {k1: {k2a: {k3a: v3a, k3b: v3b}, k2b: v2b, k2c: v2c}}

        {(k1, k2a, k3a): v3a,
         (k1, k2a, k3b): v3b,
         (k1, k2b)     : v2b,
         (k1, k2c)     : v2c}

    This is the format used to create DataFrame objects with the .from_dict() method.

    :param data: The data dictionary to be reformed. This should be the data in the single frame, NOT the full data.
    :param depth: This parameter sets how deep into the dictionary to go. i.e. how many nested dictionaries to explore
    :param key_map: This parameter should not be filled; it is used to keep track of the current key map.
    :param return_value: This parameter should not be filled; it is used to keep track of the current return value.
    :return: The flattened dictionary, with a tuple as the value's key map.
    """
    if return_value is None:
        return_value = {}

    if depth is None:
        new_depth = None
        go_deeper = True
    elif depth > 0:
        new_depth = depth - 1
        go_deeper = True
    else:
        new_depth = None
        go_deeper = False

    for key, value in data.items():
        current_key = (key,)
        if key_map is not None:
            current_key = key_map + current_key
        if go_deeper:
            if isinstance(value, dict):
                reform_data(value, new_depth, current_key, return_value)
            else:
                return_value[current_key] = value
        else:
            return_value[current_key] = value

    return return_value


class DataHandler:
    def __init__(self):
        self.current_actor_data_by_actor_type = {}

        self.players_by_uid = {}
        self.ball = None
        self.game_info = None

        self.frame_player_data = {}
        self.frame_ball_data = {}
        self.frame_game_data = {}

        self.t = 0

    def process_actor_data_in_frame(self, frame_idx: int, actor_data_by_actor_type: dict):
        """
        This method takes freshly parsed actor data, stored as a dictionary by actor types, and processes it into a more
        intuitive format. Specifically, it combines Player, Car, Car Component and Team data into one, because to us
        these objects are parts of the Player.

        :param frame_idx: The current frame index, used to store processed data into the correct frame.
        :param actor_data_by_actor_type: The parsed actor data that is yet to be processed.
        """
        self.frame_player_data = {}
        self.frame_game_data = {}
        self.frame_ball_data = {}

        self.current_actor_data_by_actor_type = actor_data_by_actor_type

        # PLAYERS (and Cars, Car Components, Teams)
        player_aid_to_uid, player_uid_to_team_aid = self.collect_player_data_in_frame()
        car_aid_to_player_uid = self.collect_car_data_in_frame(player_aid_to_uid)
        self.collect_car_component_data_in_frame(car_aid_to_player_uid)
        self.collect_team_data_in_frame(player_uid_to_team_aid)
        for player_uid in self.players_by_uid.keys():
            self.players_by_uid[player_uid].update_data(frame_idx, self.frame_player_data[player_uid])

        # BALL
        self.collect_ball_data_in_frame()
        self.ball.update_data(frame_idx, self.frame_ball_data)

        # GAME (and Time, Time Delta)
        self.collect_game_event_data_in_frame()
        self.game_info.update_data(frame_idx, self.frame_game_data)

    def collect_player_data_in_frame(self):
        """
        This method collects data on a per-player basis and then updates the self.player_data_by_uid variable.

        :return: player_aid_to_uid which maps each players' actor ID to its unique ID,
        it is used to allow for easier addition of car data to self.player_data_by_uid.
        """
        player_aid_to_uid = {}
        player_uid_to_team_aid = {}

        players = self.current_actor_data_by_actor_type[PlayerParser.actor_type_short]
        for player in players:
            player_aid = player['actor_id']
            del player['actor_id']

            player_uid = player['player_unique_id']
            del player['player_unique_id']

            player_team_aid = player['team_actor_id']
            del player['team_actor_id']

            player_uid_to_team_aid[player_uid] = player_team_aid
            player_aid_to_uid[player_aid] = player_uid

            if player_uid not in self.players_by_uid.keys():
                self.players_by_uid[player_uid] = Player(player_uid)
            self.frame_player_data[player_uid] = {}

            # self.frame_player_data.update(reform_data(player, None, (player_uid,)))
            self.frame_player_data[player_uid].update(reform_data(player))

        return player_aid_to_uid, player_uid_to_team_aid

    def collect_car_data_in_frame(self, player_aid_to_uid):
        """
        This method collects data on a per-car basis and then updates the self.player_data_by_uid variable.

        :return: car_aid_to_player_uid which maps each cars' actor ID to its player's unique ID,
        it is used to allow for easier addition of car component data to self.player_data_by_uid.
        """
        car_aid_to_player_uid = {}

        cars = self.current_actor_data_by_actor_type[CarParser.actor_type_short]
        for car in cars:
            car_aid = car.get('actor_id', -1)
            if car_aid != -1:
                del car['actor_id']

            driver_aid = car.get('player_actor_id', -1)
            if driver_aid != -1:
                del car['player_actor_id']

            if driver_aid != -1:
                driver_uid = player_aid_to_uid[driver_aid]
                car_aid_to_player_uid[car_aid] = driver_uid
                if driver_uid != -1:
                    # self.frame_player_data.update(reform_data(car, 1, (driver_uid,)))
                    self.frame_player_data[driver_uid].update(reform_data(car))

        return car_aid_to_player_uid

    # TODO Boost usage is not actually recorded. 'carball' assumes boost per second is (80 * 1 / .93).
    def collect_car_component_data_in_frame(self, car_aid_to_player_uid):
        """
        This method collects data on a per-car-component basis and then updates the self.player_data_by_uid variable.
        """
        # NOTE: CC stands for Car Component
        for cc_parser in [BoostParser, DodgeParser, DoubleJumpParser, JumpParser]:
            cc_type = cc_parser.actor_type_short
            car_components = self.current_actor_data_by_actor_type.get(cc_type, [])
            for car_component in car_components:
                # car_component_aid = car_component['actor_id']
                del car_component['actor_id']

                car_aid = car_component['car_actor_id']
                del car_component['car_actor_id']

                if car_aid != -1:
                    driver_uid = car_aid_to_player_uid.get(car_aid, -1)
                    if driver_uid != -1:
                        # self.frame_player_data.update(reform_data(car_component, 1, (driver_uid,)))
                        self.frame_player_data[driver_uid].update(reform_data(car_component))

    def collect_team_data_in_frame(self, player_uid_to_team_aid):
        teams = self.current_actor_data_by_actor_type[TeamParser.actor_type_short]
        for team in teams:
            team_aid = team['actor_id']
            del team['actor_id']

            for player_uid, player_team_aid in player_uid_to_team_aid.items():
                if team_aid == player_team_aid:
                    self.frame_player_data.update({(player_uid, 'team'): team['team_side']})

    def collect_ball_data_in_frame(self):
        """
        This method collects ball data and returns one ball object to transform into a DataFrame.
        """
        balls = self.current_actor_data_by_actor_type[BallParser.actor_type_short]
        if len(balls) > 1:
            # TODO Handle multiple balls?
            logging.warning("Multiple balls in one frame; data only processed for one.")
        ball = balls[0]
        del ball['actor_id']

        if self.ball is None:
            self.ball = Ball()

        self.frame_ball_data.update(reform_data(ball))

    def collect_game_event_data_in_frame(self):
        """
        This method collects game event data and returns one game event object to transform into a DataFrame.
        NOTE: Game event is just generic game info (game time, time delta from previous frame, in-game seconds
        remaining, is it overtime, has the ball been touched..)
        """
        game_events = self.current_actor_data_by_actor_type[GameEventParser.actor_type_short]
        if len(game_events) > 1:
            # TODO Handle multiple game event variables?
            logging.warning("Multiple game event variables in one frame; data only processed for one.")
        game_event = game_events[0]
        game_event.update(**self.current_actor_data_by_actor_type['GameTime'][0])
        del game_event['actor_id']

        if self.game_info is None:
            self.game_info = GameInfo()

        self.frame_game_data.update(reform_data(game_event))

    def create_dataframes(self):
        for player in self.players_by_uid.values():
            player.set_dataframe(pd.DataFrame.from_dict(player.get_data(), orient='index'))

        self.ball.set_dataframe(pd.DataFrame.from_dict(self.ball.get_data(), orient='index'))

        self.game_info.set_dataframe(pd.DataFrame.from_dict(self.game_info.get_data(), orient='index'))
