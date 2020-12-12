from enum import Enum

from replay_parsing.actor_parsing.base_parser import BaseParser
from replay_parsing.actor_parsing.utils import handle_default, handle_player_info


class CarComponentAttributes(Enum):
    VEHICLE = "TAGame.CarComponent_TA:Vehicle"
    ACTIVE = "TAGame.CarComponent_TA:ReplicatedActive"


class CarComponentParser(BaseParser):
    actor_type = "Archetypes.CarComponents."
    actor_type_short = "CarComponent"

    def __init__(self, parser_config):
        self_config = parser_config['CarComponent']
        for fields in self_config:
            if self_config[fields]['is_selected']:
                if self.selected_attributes is None:
                    self.selected_attributes = {}
                self.selected_attributes[self_config[fields]['actor_type']] = self_config[fields]['custom_name']

        super(CarComponentParser, self).__init__(parser_config)

    def parse(self, car_component_actor):
        car_component_dict = BaseParser.parse(self, car_component_actor)

        # To ease data handling, rename 'is_active' to 'is_cc_active' where cc is the car component short type.
        is_cc_active = car_component_dict['is_active']
        is_cc_active_str = 'is_%s_active' % str(self.actor_type_short.lower())
        car_component_dict[is_cc_active_str] = is_cc_active
        del car_component_dict['is_active']

        return car_component_dict
