from replay_parsing.actor_parsing.base_parser import BaseParser


class CarParser(BaseParser):
    actor_type = "Archetypes.Car."
    actor_type_short = "Car"

    def parse(self, car_actor):
        car_dict = BaseParser.parse(self, car_actor)

        if car_dict.get('car_data', None) is not None:
            car_dict.update(**car_dict['car_data'])
            del car_dict['car_data']

        return car_dict
