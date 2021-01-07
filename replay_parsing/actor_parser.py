import logging
import time

from replay_parsing.parsing_magic_strings.internal_actor import InternalActor
from replay_parsing.parsing_magic_strings.external_actor import ExternalActor

from replay_parsing.actor_parsing import *
from replay_parsing.data_handler import DataHandler
from replay_parsing.parser_factory import ParserFactory
from replay_parsing.parsing_magic_strings.primary_objects import PrimaryObjects

logger = logging.getLogger(__name__)

# Main parsers.
PARSERS = [CarParser,
           PlayerParser,
           TeamParser,
           BallParser,
           GameEventParser,

           BoostParser,
           DodgeParser,
           JumpParser,
           DoubleJumpParser]


def get_replay_stuff_dict(replay_stuff):
    stuff_dict = {}
    for index, obj in enumerate(replay_stuff):
        stuff_dict[index] = str(obj)
    return stuff_dict


class ActorParser:
    """
    The ActorParser is responsible for receiving all video-frames from the replay and parsing all actor data; an actor
    is any object within the replay - each actor has a base type, aka class, which is how the ActorParser delegates
    parsing. Each actor's data is parsed individually by the classes in the actor_parsing directory.
    """

    def __init__(self, replay_frames, replay_objects, replay_names):
        self.replay_frames = replay_frames

        # These dictionaries map the object/name ID to the object/name string name.
        # These are necessary because IDs are not guaranteed to be equal across replays.
        self.objects_dict = get_replay_stuff_dict(replay_objects)
        with open("obj.txt", "a") as f:
            for k, v in self.objects_dict.items():
                f.write("%s. %s\n" % (str(k), str(v)))
            f.close()
        self.names_dict = get_replay_stuff_dict(replay_names)

        # The actors that are currently existing in the replay. Accessed by the actor_id, value is determined in the
        # manage_new_actor method.
        self.current_actors = {}
        # The actors that have just changed (variable populated during each frame, and reset for the next). This is a
        # list of actor IDs that should be parsed again. All current_actors not in updated_actors will use cached data.
        self.updated_actors = set()

        # The 'states' of actors within the replay matched up to the appropriate handling method.
        self.ACTOR_STATES = {ExternalActor.DELETED_ACTORS: self.handle_deleted_actor,
                             ExternalActor.NEW_ACTORS: self.handle_new_actor,
                             ExternalActor.UPDATED_ACTORS: self.handle_updated_actor}

        # A factory for parsers, to avoid excess object creation..
        self.parser_factory = ParserFactory(PARSERS)
        # A dictionary that matches actor IDs to the appropriate parser; set in the handle_new_actors method.
        self.current_actor_parser_pairs = {}

        # ---

        self.data_handler = DataHandler()
        self.is_data_processed = False

        # ---

        self.t = 0

    def parse_actors_from_replay_frames(self):
        """
        This method is responsible for going through every received video-frame and working with the actors within the
        frame, where they are deleted/created/updated and (the existing actors are) parsed.

        NOTE: Actor IDs may change throughout the replay, hence the need for a current_actors dictionary.

        :return: A dictionary with the following structure:
                {frame_idx:
                   {'type_short1':
                      [type1actor1_dict,
                       type1actor2_dict,
                       ...]},
                    {'type_short2':
                       [type2actor1_dict,
                        type2actor2_dict,
                        ...]}}
             The frame_idx is an integer of the replay video-frame that contains the actors.
             The 'type_short' is defined in the actor's manager class. (MANAGER.type_short)
             The 'actor_dict' dictionaries contain the actor's data as parsed by the actor's manager class.
        """
        for frame_idx, frame in enumerate(self.replay_frames):
            self.handle_all_actors_in_frame(frame)

            data_per_actor_type = self.parse_current_actors()
            data_per_actor_type['GameTime'] = [{'replay_time': frame['time'], 'time_delta': frame['delta']}]

            t1 = time.time()
            self.data_handler.process_actor_data_in_frame(frame_idx, data_per_actor_type)
            self.t += time.time() - t1

            # Reset updated actors for the next frame.
            self.updated_actors.clear()

        print(self.t)
        self.data_handler.create_dataframes()
        self.is_data_processed = True

    def parse_current_actors(self):
        """
        This method is responsible for parsing each actor with the appropriate parser (found in the current_actor_parser
        _pairs dictionary), and then storing the result as a dictionary, with the key being an actor's short type and
        the value being a list of parsed actor data (there are often multiple same-type actors).
        """

        type_sorted_actors = {}
        for p in PARSERS:
            type_sorted_actors[p.actor_type_short] = []

        for actor_id, parser in self.current_actor_parser_pairs.items():
            if parser is not None:
                if actor_id in self.updated_actors:
                    actor = self.current_actors[actor_id]
                    actor_dict = parser.parse(actor)
                    parser.update_cache_with(actor_dict)
                else:
                    actor_dict = parser.get_cache_for(actor_id)

                type_sorted_actors[parser.actor_type_short].append(actor_dict)

        return type_sorted_actors

    def handle_all_actors_in_frame(self, frame):
        """
        In the given frame, for each actor_state, retrieve the actors and handle them with the appropriate handler; the
        appropriate handlers are defined in self.actor_states

        :param frame: A dictionary of all actors per actor_state (i.e. updated data for this video-frame)
        """
        for actor_state, actor_state_handler in self.ACTOR_STATES.items():
            for actor in frame[actor_state]:
                actor_state_handler(actor)

    def handle_deleted_actor(self, deleted_actor_id):
        del self.current_actors[deleted_actor_id]
        del self.current_actor_parser_pairs[deleted_actor_id]

    def handle_new_actor(self, new_actor):
        new_actor_id = new_actor[ExternalActor.ACTOR_ID]
        new_actor_name = self.names_dict[new_actor[ExternalActor.ACTOR_NAME_ID]]
        new_actor_type = self.objects_dict[new_actor[ExternalActor.ACTOR_TYPE_ID]]

        self.current_actors[new_actor_id] = {
            InternalActor.ACTOR_ID: new_actor_id,
            InternalActor.ACTOR_NAME: new_actor_name,
            InternalActor.ACTOR_TYPE: new_actor_type,
            InternalActor.ACTOR_ATTRIBUTES: {}
        }

        # Straight away, assign a parser to the actor; this is to avoid excessive loops.
        # We cannot parse here, because this actor may be updated.
        actor_parser = self.parser_factory.get_parser(new_actor_type)
        self.current_actor_parser_pairs[new_actor_id] = actor_parser
        self.updated_actors.add(new_actor_id)

    def handle_updated_actor(self, updated_actor):
        """
        This method takes an updated actor and adds/overwrites its updated attribute to the appropriate current actor's
        attributes. (key = attribute type name, value = attribute)
        """
        updated_actor_id = updated_actor[ExternalActor.ACTOR_ID]
        updated_object_id = updated_actor[ExternalActor.ACTOR_TYPE_ID]
        updated_object_name = self.objects_dict[updated_object_id]
        updated_attribute_value = updated_actor[ExternalActor.ACTOR_ATTRIBUTE]
        self.current_actors[updated_actor_id][InternalActor.ACTOR_ATTRIBUTES][updated_object_name] = \
            updated_attribute_value

        self.updated_actors.add(updated_actor_id)

        # TODO (Possibly) Keep track of the specific attribute to reparse i.e. dynamically change selected_attributes

    # def get_raw_data(self):
    #     if self.is_data_processed:
    #         return {PrimaryObjects.PLAYERS: self.data_handler.full_player_data,
    #                 PrimaryObjects.BALL: self.data_handler.full_ball_data,
    #                 PrimaryObjects.GAME: self.data_handler.full_game_data}
    #     else:
    #         logger.warning("Cannot get data before it was created.")

    # def get_dataframes(self):
    #     if self.is_data_processed:
    #         self.data_handler.create_dataframes()
    #
    #         temp = {PrimaryObjects.PLAYERS: {}, PrimaryObjects.BALL: {}, PrimaryObjects.GAME_INFO: {}}
    #         for p in self.data_handler.players_by_uid.values():
    #             temp[PrimaryObjects.PLAYERS][p.get_unique_id()] = p.get_dataframe()
    #
    #         temp[PrimaryObjects.BALL] = self.data_handler.ball.get_dataframe()
    #         temp[PrimaryObjects.GAME_INFO] = self.data_handler.game_info.get_dataframe()
    #
    #         return temp
    #     else:
    #         logger.warning("Cannot get data before it was created.")

    def get_players(self):
        if self.is_data_processed:
            players = []
            for player in self.data_handler.players_by_uid.values():
                players.append(player)
            return players
        else:
            logger.warning("Cannot get players before they were created.")

    def get_ball(self):
        if self.is_data_processed:
            return self.data_handler.ball
        else:
            logger.warning("Cannot get ball before it was created.")

    def get_game_info(self):
        if self.is_data_processed:
            return self.data_handler.game_info
        else:
            logger.warning("Cannot get game info before it was created.")
