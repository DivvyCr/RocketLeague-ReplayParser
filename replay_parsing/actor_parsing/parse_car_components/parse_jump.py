from replay_parsing.actor_parsing.parse_car_components.car_component_parser import CarComponentParser


class JumpParser(CarComponentParser):
    actor_type = "Archetypes.CarComponents.CarComponent_Jump"
    actor_type_short = "Jump"

    def parse(self, jump_actor):
        return CarComponentParser.parse(self, jump_actor)
