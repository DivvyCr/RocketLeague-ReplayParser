from replay_parsing.actor_parsing.base_parser import BaseParser


class GameEventParser(BaseParser):
    actor_type = "Archetypes.GameEvent."
    actor_type_short = "GameEvent"

    def parse(self, game_actor):
        return BaseParser.parse(self, game_actor)
