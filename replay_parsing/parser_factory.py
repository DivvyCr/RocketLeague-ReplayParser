import logging

import yaml

logger = logging.getLogger(__name__)


class ParserFactory:
    cfg = None

    def __init__(self, selected_parsers):
        self.selected_parsers = selected_parsers
        self.parsers = {}

        with open("config.yml", "r") as ymlfile:
            self.cfg = yaml.safe_load(ymlfile)

        logger.debug(" ParserFactory created (with a loaded configuration file).")

    def get_parser(self, actor_type):
        if actor_type in self.parsers.keys():
            return self.parsers[actor_type]
        else:
            for parser in self.selected_parsers:
                if actor_type.startswith(parser.actor_type):
                    self.parsers[actor_type] = parser(self.cfg['Parsers'])
                    logger.debug(" New parser \'" + str(parser.__name__) + "\' created and configured.")
                    return self.parsers[actor_type]
            return None
