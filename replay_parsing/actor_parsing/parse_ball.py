from replay_parsing.actor_parsing.base_parser import BaseParser


class BallParser(BaseParser):
    actor_type = "Archetypes.Ball."
    actor_type_short = "Ball"

    def parse(self, ball_actor):
        ball_dict = BaseParser.parse(self, ball_actor)

        if ball_dict.get('ball_data', None) is not None:
            ball_dict.update(**ball_dict['ball_data'])
            del ball_dict['ball_data']

        return ball_dict
