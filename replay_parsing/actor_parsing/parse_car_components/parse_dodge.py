from enum import Enum

from replay_parsing.actor_parsing.base_parser import BaseParser
from replay_parsing.actor_parsing.parse_car_components.car_component_parser import CarComponentParser
from replay_parsing.actor_parsing.utils import handle_coords_dict


class DodgeAttributes(Enum):
    # All attributes of a dodge car component actor.
    TORQUE = "TAGame.CarComponent_Dodge_TA:DodgeTorque"


class DodgeParser(CarComponentParser):
    actor_type = "Archetypes.CarComponents.CarComponent_Dodge"
    actor_type_short = "Dodge"

    def parse(self, dodge_actor):
        return CarComponentParser.parse(self, dodge_actor)
