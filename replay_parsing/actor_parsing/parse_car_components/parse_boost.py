from replay_parsing.actor_parsing.parse_car_components.car_component_parser import CarComponentParser


class BoostParser(CarComponentParser):
    actor_type = "Archetypes.CarComponents.CarComponent_Boost"
    actor_type_short = "Boost"

    def parse(self, boost_actor):
        return CarComponentParser.parse(self, boost_actor)
