from replay_parsing.actor_parsing.parse_car_components.car_component_parser import CarComponentParser


class DodgeParser(CarComponentParser):
    actor_type = "Archetypes.CarComponents.CarComponent_Dodge"
    actor_type_short = "Dodge"

    def parse(self, dodge_actor):
        return CarComponentParser.parse(self, dodge_actor)
