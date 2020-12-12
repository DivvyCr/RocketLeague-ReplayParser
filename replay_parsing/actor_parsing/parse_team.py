from replay_parsing.actor_parsing.base_parser import BaseParser


class TeamParser(BaseParser):
    actor_type = "Archetypes.Teams."
    actor_type_short = "Team"

    def parse(self, team_actor):
        team_dict = BaseParser.parse(self, team_actor)
        team_dict['team_side'] = (0, "blue") if team_actor['actor_type'][-1] == '0' else (1, "orange")
        return team_dict
