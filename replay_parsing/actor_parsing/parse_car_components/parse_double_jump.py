from replay_parsing.actor_parsing.parse_car_components.car_component_parser import CarComponentParser


class DoubleJumpParser(CarComponentParser):
    actor_type = "Archetypes.CarComponents.CarComponent_DoubleJump"
    actor_type_short = "DoubleJump"

    def parse(self, jump_actor):
        return CarComponentParser.parse(self, jump_actor)
