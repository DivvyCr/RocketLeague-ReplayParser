from replay_parsing.actor_parsing.base_parser import BaseParser


class PlayerParser(BaseParser):
    actor_type = "TAGame.Default__PRI_TA"
    actor_type_short = "Player"

    def parse(self, player_actor):
        player_dict = BaseParser.parse(self, player_actor)
        return player_dict

        # TODO Manage loadouts.
