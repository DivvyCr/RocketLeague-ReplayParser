from enum import Enum

from replay_parsing.actor_parsing.base_parser import BaseParser
from replay_parsing.actor_parsing.parse_car_components.car_component_parser import CarComponentParser
from replay_parsing.actor_parsing.utils import handle_default


class BoostAttributes(Enum):
    # All attributes of a boost car component actor.
    AMOUNT = "TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount"


class BoostParser(CarComponentParser):
    actor_type = "Archetypes.CarComponents.CarComponent_Boost"
    actor_type_short = "Boost"

    def parse(self, boost_actor):
        return CarComponentParser.parse(self, boost_actor)
