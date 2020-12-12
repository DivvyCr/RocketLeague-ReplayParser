from replay_parsing.parsing_magic_strings.internal_actor import InternalActor as IntActor
from replay_parsing.actor_parsing.utils import handle_default, handle_rb_state_split, handle_rb_state, \
    handle_player_info, extract_player_id, handle_coords_dict


def _get_handler(attribute: str):
    """
    This method is responsible for handling attributes.

    :param attribute: The class (type) name of the attribute.
    :return: A callable that processes the value in a specific way.
    """

    if attribute == "TAGame.RBActor_TA:ReplicatedRBState":
        return handle_rb_state

    if attribute == "Engine.Pawn:PlayerReplicationInfo" or attribute == "TAGame.CarComponent_TA:Vehicle":
        return handle_player_info

    if attribute == "Engine.PlayerReplicationInfo:UniqueId":
        return extract_player_id

    if attribute == "Archetypes.CarComponents.CarComponent_Dodge":
        return handle_coords_dict

    return handle_default


# ActorParser is more fitting, but that class name is already used.
class BaseParser:
    actor_type: str = None
    actor_type_short: str = None

    selected_attributes: dict = None

    cache: dict = {}

    # TODO Need to handle defaults properly, to avoid creation of {NaN: {NaN...}} dictionary entries.

    def __init__(self, parser_config):
        # Assign selected_attributes for each new parser, according to the configuration.
        if self.actor_type_short in parser_config:
            self_config = parser_config[self.actor_type_short]
            for fields in self_config:
                if self_config[fields]['is_selected']:
                    if self.selected_attributes is None:
                        self.selected_attributes = {}
                    self.selected_attributes[self_config[fields]['actor_type']] = self_config[fields]['custom_name']

    @classmethod
    def is_suitable_type(cls, actor):
        return actor[IntActor.ACTOR_TYPE].startswith(cls.actor_type)

    def parse(self, actor: dict):
        # Initialise the actor data dictionary with the actor ID, which must exist.
        actor_dict = {IntActor.ACTOR_ID: actor[IntActor.ACTOR_ID]}

        if self.selected_attributes is None:
            return actor_dict

        # Fetch actor attributes.
        actor_attributes = actor[IntActor.ACTOR_ATTRIBUTES]

        for attribute, custom_name in self.selected_attributes.items():
            # Get the value for each selected attribute, if it does not exist, assign None.
            value = actor_attributes.get(attribute, None)

            # Process the value and store it under the custom name (in configuration file) in the actor data dictionary.
            actor_dict[custom_name] = _get_handler(attribute)(value)

        return actor_dict

    def update_cache_with(self, actor_dict: dict):
        # Need to copy the dictionary to avoid linking 2+ actors to the same cache.
        self.cache[actor_dict[IntActor.ACTOR_ID]] = actor_dict.copy()

    def get_cache_for(self, actor_id: int):
        # Need to copy the dictionary to avoid linking 2+ actors to the same cache.
        return self.cache[actor_id].copy()

    # Key actor types:
    # ---------------
    # Archetypes.Ball.Ball_Default
    # Archetypes.Car.Car_Default
    # Archetypes.CarComponents.CarComponent_Boost
    # Archetypes.CarComponents.CarComponent_Dodge
    # Archetypes.CarComponents.CarComponent_DoubleJump
    # Archetypes.CarComponents.CarComponent_FlipCar
    # Archetypes.CarComponents.CarComponent_Jump
    # Archetypes.GameEvent.GameEvent_Soccar
    # Archetypes.Teams.Team0
    # Archetypes.Teams.Team1
    # Stadium_P.TheWorld:PersistentLevel.VehiclePickup_Boost_TA_{id}
    # GameInfo_Soccar.GameInfo.GameInfo_Soccar:GameReplicationInfoArchetype
    # TAGame.Default__CameraSettingsActor_TA
    # TAGame.Default__PRI_TA
